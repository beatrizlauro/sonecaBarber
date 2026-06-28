"""
Responsabilidades deste processo
----------------------------------
1. Disponibilizar um **servidor de mensagens** baseado em
   ``multiprocessing.managers.BaseManager``, acessível via TCP, para que
   os processos Cliente (``cliente.py``) possam enviar mensagens de chegada.

2. Executar a **lógica do Barbeiro**: aguardar mensagens, atender clientes
   e demonstrar as 3 situações exigidas pelo enunciado.

Mecanismo de IPC (troca de mensagens)
---------------------------------------
O ``BaseManager`` expõe o objeto ``Barbearia`` remotamente, tornando seus
métodos acessíveis a processos externos via proxy TCP autenticado.

- Os Clientes chamam ``barbearia.tentar_sentar(id)`` → enviam uma mensagem.
- A ``queue.Queue(maxsize=3)`` interna representa as 3 cadeiras de espera:
  quando cheia, ``tentar_sentar`` retorna ``False`` e o cliente vai embora.
- O Barbeiro chama ``barbearia.aguardar_cliente()`` diretamente (acesso
  local, sem proxy), bloqueando até chegar uma nova mensagem.

Situações demonstradas
-----------------------
[SITUAÇÃO 1] Abertura: todas as cadeiras vazias e o barbeiro dormindo.
[SITUAÇÃO 2] Cadeiras de espera ocupadas enquanto o barbeiro atende.
[SITUAÇÃO 3] Barbearia lotada: cliente vai embora (detectado em cliente.py).

Uso
----
    python barbeiro.py
    (normalmente iniciado pelo demonstracao.py)
"""

import queue
import threading
import time
from multiprocessing.managers import BaseManager

# ── Constantes de configuração ─────────────────────────────────────────────────
CADEIRAS_ESPERA: int = 3            # capacidade da fila = nº de cadeiras físicas
TEMPO_CORTE_SEGUNDOS: float = 2.0   # duração simulada de cada corte de cabelo

# Endereço e credencial do servidor de mensagens
GERENCIADOR_HOST: str = "127.0.0.1"
GERENCIADOR_PORTA: int = 50000
GERENCIADOR_SENHA: bytes = b"sonecabarber"


# ══════════════════════════════════════════════════════════════════════════════
# Canal de mensagens
# ══════════════════════════════════════════════════════════════════════════════

class Barbearia:
    """
    Canal de mensagens entre Clientes e Barbeiro.

    Encapsula uma ``queue.Queue`` thread-safe com ``maxsize=CADEIRAS_ESPERA``.
    Cada elemento enfileirado representa a mensagem de chegada de um cliente
    (seu ``cliente_id`` inteiro). A string especial ``"FIM"`` encerra o
    expediente do Barbeiro.

    Métodos expostos remotamente via proxy (usados pelos Clientes)
    ---------------------------------------------------------------
    tentar_sentar(id)       — envia mensagem; retorna False se barbearia cheia.
    clientes_aguardando()   — número de clientes aguardando na fila.
    esta_vazia()            — True se não há ninguém esperando.
    encerrar_expediente()   — envia sinal de fim de expediente ("FIM").

    Método de acesso local (usado diretamente pelo Barbeiro neste mesmo processo)
    -----------------------------------------------------------------------------
    aguardar_cliente()      — bloqueia até chegar a próxima mensagem.
                              Não é exposto ao proxy para evitar que clientes
                              externos bloqueiem o servidor indefinidamente.
    """

    def __init__(self) -> None:
        # queue.Queue é thread-safe: o servidor de mensagens atende chamadas
        # remotas em threads paralelas, enquanto o loop do Barbeiro consome
        # mensagens no thread principal — sem risco de corrida de dados.
        self._fila: queue.Queue = queue.Queue(maxsize=CADEIRAS_ESPERA)

    # ── Métodos remotos ───────────────────────────────────────────────────────

    def tentar_sentar(self, cliente_id: int) -> bool:
        """
        Tenta enfileirar a mensagem de chegada do cliente (sem bloquear).

        Usa ``put_nowait`` para garantir que o cliente não bloqueie o
        servidor caso a fila esteja cheia; nesse caso captura ``queue.Full``
        e retorna False, evitando o propagation de RemoteError ao cliente.

        Retorna
        -------
        True  — mensagem entregue; cliente ocupa uma cadeira de espera.
        False — fila cheia [SITUAÇÃO 3]; cliente deve ir embora.
        """
        try:
            self._fila.put_nowait(cliente_id)
            return True
        except queue.Full:
            return False

    def clientes_aguardando(self) -> int:
        """
        Retorna o número aproximado de mensagens pendentes na fila.

        Nota: ``qsize()`` não é garantida em todas as plataformas (ex.: macOS);
        nesse caso retorna -1 como indicador de indisponibilidade.
        """
        try:
            return self._fila.qsize()
        except NotImplementedError:
            return -1

    def esta_vazia(self) -> bool:
        """Retorna True se não há mensagens (clientes) aguardando."""
        return self._fila.empty()

    def encerrar_expediente(self) -> None:
        """
        Envia a mensagem de controle ``'FIM'`` para encerrar o loop do Barbeiro.

        Usa ``put()`` bloqueante (sem maxsize) para garantir entrega mesmo
        que a fila esteja cheia com clientes — o expediente deve ser encerrado.
        """
        self._fila.put("FIM")

    # ── Método local (não exposto ao proxy) ───────────────────────────────────

    def aguardar_cliente(self):
        """
        Bloqueia o thread chamador até chegar a próxima mensagem de cliente.

        Retorna o ``cliente_id`` (int) ou ``"FIM"`` para encerramento.
        Chamado diretamente pelo loop do Barbeiro, nunca via proxy remoto.
        """
        return self._fila.get()


# Instância global: compartilhada entre o servidor de mensagens (threads do
# Manager) e o loop principal do Barbeiro, ambos no mesmo processo.
barbearia = Barbearia()


# ══════════════════════════════════════════════════════════════════════════════
# Servidor de mensagens (BaseManager)
# ══════════════════════════════════════════════════════════════════════════════

class GerenciadorBarbearia(BaseManager):
    """
    Servidor de mensagens TCP baseado em ``multiprocessing.managers.BaseManager``.

    Expõe o objeto ``barbearia`` a processos externos via proxy autenticado.
    Cada Cliente conectado recebe um proxy com acesso somente aos métodos
    listados em ``exposed``, garantindo encapsulamento e segurança.
    """
    pass


# Registra o objeto compartilhado e define quais métodos o proxy pode chamar.
# O método ``aguardar_cliente`` é intencionalmente omitido do ``exposed``:
# apenas o Barbeiro (acesso local) pode bloquear na fila.
GerenciadorBarbearia.register(
    "obter_barbearia",
    callable=lambda: barbearia,
    exposed=[
        "tentar_sentar",
        "clientes_aguardando",
        "esta_vazia",
        "encerrar_expediente",
    ],
)


def _iniciar_servidor_mensagens() -> None:
    """
    Sobe o servidor de mensagens e entra em loop eterno de atendimento.

    Executado em uma thread daemon: encerra automaticamente quando o
    processo principal (loop do Barbeiro) terminar.
    """
    gerenciador = GerenciadorBarbearia(
        address=(GERENCIADOR_HOST, GERENCIADOR_PORTA),
        authkey=GERENCIADOR_SENHA,
    )
    servidor = gerenciador.get_server()
    print(
        f"📡 Servidor de mensagens ativo em "
        f"{GERENCIADOR_HOST}:{GERENCIADOR_PORTA}",
        flush=True,
    )
    servidor.serve_forever()  # bloqueia a thread daemon indefinidamente


# ══════════════════════════════════════════════════════════════════════════════
# Lógica do Barbeiro
# ══════════════════════════════════════════════════════════════════════════════

def executar_barbeiro() -> None:
    """
    Loop principal do Barbeiro: recebe mensagens e simula atendimentos.

    Estados alternados
    ------------------
    dormindo=True
        [SITUAÇÃO 1] — Barbearia vazia; o Barbeiro dorme na cadeira.
        ``aguardar_cliente()`` bloqueia o thread até chegar uma mensagem.

    dormindo=False
        Barbeiro acordado; ao terminar um corte verifica a fila:
        - fila não vazia → [SITUAÇÃO 2] chama o próximo e continua acordado.
        - fila vazia     → volta a dormir (dormindo=True).

    Acesso à ``barbearia`` é direto (objeto local), não via proxy TCP.
    """
    dormindo = True

    while True:

        # ── [SITUAÇÃO 1] Barbearia vazia: barbeiro dormindo ────────────────────
        if dormindo:
            print(
                "\n[SITUAÇÃO 1] Barbearia vazia: "
                "o barbeiro senta na cadeira e tira uma pestana... Zzzzz",
                flush=True,
            )

        # Bloqueia até receber a próxima mensagem de cliente (IPC via fila)
        cliente_id = barbearia.aguardar_cliente()

        # Mensagem de controle para encerrar o expediente
        if cliente_id == "FIM":
            print("\n💈 Barbeiro: Encerrando expediente.", flush=True)
            break

        # ── Acorda ou chama o próximo ──────────────────────────────────────────
        if dormindo:
            # Primeiro cliente acorda o barbeiro dorminhoco
            print(
                f"\n🗣️  Cliente {cliente_id}: "
                "ACORDA! Hora de trabalhar seu dorminhoco!",
                flush=True,
            )
            dormindo = False
        else:
            # Barbeiro já estava acordado; terminou o corte anterior
            print(
                f"\n💈 Barbeiro: PRÓXIMO! (chamando Cliente {cliente_id})",
                flush=True,
            )

        # ── Simulação do corte de cabelo ───────────────────────────────────────
        print(f"💺 Cliente {cliente_id}: sentou na cadeira do barbeiro.", flush=True)
        print(
            f"✂️  Barbeiro: cortando o cabelo do Cliente {cliente_id}...",
            flush=True,
        )
        time.sleep(TEMPO_CORTE_SEGUNDOS)
        print(
            f"✅ Barbeiro: terminou o corte do Cliente {cliente_id}.",
            flush=True,
        )

        # ── Verifica a fila ao terminar o corte ───────────────────────────────
        if barbearia.esta_vazia():
            print(
                "😴 Barbeiro: não há mais clientes. Vou voltar a dormir.",
                flush=True,
            )
            dormindo = True
        else:
            # ── [SITUAÇÃO 2] Cadeiras de espera ainda ocupadas ─────────────────
            n = barbearia.clientes_aguardando()
            print(
                f"[SITUAÇÃO 2] 📋 Ainda há clientes nas cadeiras de espera "
                f"({n} aguardando).",
                flush=True,
            )
            dormindo = False


# ══════════════════════════════════════════════════════════════════════════════
# Ponto de entrada
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 1. Inicia o servidor de mensagens em thread daemon (não bloqueia o main)
    thread_servidor = threading.Thread(
        target=_iniciar_servidor_mensagens, daemon=True
    )
    thread_servidor.start()

    # 2. Pequena pausa para garantir que o servidor TCP está pronto antes de
    #    o Barbeiro começar a aguardar mensagens (evita race condition na demo)
    time.sleep(0.5)

    # 3. Roda a lógica do Barbeiro no thread principal
    try:
        executar_barbeiro()
    except KeyboardInterrupt:
        print("\n⚠️  Barbeiro interrompido pelo teclado.", flush=True)

    print("\n🏁 Soneca Barber encerrada!", flush=True)
