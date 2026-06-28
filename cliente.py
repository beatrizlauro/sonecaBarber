"""
Responsabilidade deste processo
---------------------------------
Representar um único cliente chegando à barbearia. Cada execução deste
script é um **processo de SO completamente independente**, com espaço de
memória próprio — não compartilha variáveis com o Barbeiro nem com outros
Clientes.

Mecanismo de IPC (troca de mensagens)
---------------------------------------
O Cliente conecta-se ao servidor de mensagens do Barbeiro via TCP usando
``multiprocessing.managers.BaseManager``. Em seguida, obtém um **proxy**
do objeto ``Barbearia`` e invoca:

    barbearia.tentar_sentar(cliente_id)

Essa chamada serializa o ``cliente_id`` e o envia pela rede ao servidor,
que o enfileira na ``queue.Queue`` interna. O retorno (``True``/``False``)
indica se o cliente conseguiu uma cadeira de espera ou foi recusado.

Situações deste processo
--------------------------
[SITUAÇÃO 3] — Quando ``tentar_sentar`` retorna ``False``, todas as 3
               cadeiras de espera estão ocupadas: o cliente vai embora.

Uso
----
    python cliente.py <id_cliente>

Exemplos:
    python cliente.py 1
    python cliente.py 7
"""

import sys
from multiprocessing.managers import BaseManager

# ── Configurações (devem coincidir com barbeiro.py) ────────────────────────────
CADEIRAS_ESPERA: int = 3            # nº de cadeiras de espera (para mensagem ao usuário)
GERENCIADOR_HOST: str = "127.0.0.1"
GERENCIADOR_PORTA: int = 50000
GERENCIADOR_SENHA: bytes = b"sonecabarber"


# ══════════════════════════════════════════════════════════════════════════════
# Proxy do servidor de mensagens
# ══════════════════════════════════════════════════════════════════════════════

class GerenciadorBarbearia(BaseManager):
    """
    Cliente do servidor de mensagens do Barbeiro.

    A chamada ``register`` sem ``callable`` indica ao Manager que este
    processo é um *cliente* — não cria o recurso, apenas se conecta.
    Os métodos disponíveis no proxy (``tentar_sentar``, ``clientes_aguardando``,
    ``esta_vazia``) são descobertos automaticamente ao conectar ao servidor,
    que informa quais métodos estão expostos.
    """
    pass


GerenciadorBarbearia.register("obter_barbearia")


# ══════════════════════════════════════════════════════════════════════════════
# Lógica do Cliente
# ══════════════════════════════════════════════════════════════════════════════

def executar_cliente(cliente_id: int) -> None:
    """
    Simula a chegada e tentativa de atendimento de um cliente.

    Fluxo
    -----
    1. Conecta ao servidor de mensagens do Barbeiro via TCP.
    2. Obtém o proxy do objeto ``Barbearia`` remoto.
    3. Chama ``tentar_sentar(cliente_id)`` — esta é a troca de mensagem IPC:
       o ``cliente_id`` é serializado e enviado pela rede ao servidor.
    4. Com base no retorno, reporta se ocupou uma cadeira ou foi embora.

    Parâmetros
    ----------
    cliente_id : int
        Identificador único do cliente, enviado como mensagem ao Barbeiro.
    """

    # ── 1. Conexão ao servidor de mensagens ───────────────────────────────────
    gerenciador = GerenciadorBarbearia(
        address=(GERENCIADOR_HOST, GERENCIADOR_PORTA),
        authkey=GERENCIADOR_SENHA,
    )
    try:
        gerenciador.connect()
    except ConnectionRefusedError:
        print(
            f"❌ Cliente {cliente_id}: barbearia fechada "
            f"(servidor indisponível em {GERENCIADOR_HOST}:{GERENCIADOR_PORTA}).",
            flush=True,
        )
        return

    # ── 2. Obtém proxy do objeto Barbearia ────────────────────────────────────
    # O proxy encaminha cada chamada de método ao servidor via TCP.
    barbearia = gerenciador.obter_barbearia()

    # ── 3. Chegada à barbearia ────────────────────────────────────────────────
    print(f"🚶 Cliente {cliente_id}: chegou na barbearia.", flush=True)

    # Troca de mensagem IPC: envia o cliente_id ao Barbeiro pela rede.
    # put_nowait() é executado no servidor; o resultado (bool) retorna aqui.
    conseguiu_sentar: bool = barbearia.tentar_sentar(cliente_id)

    # ── 4. Resultado da tentativa ─────────────────────────────────────────────
    if conseguiu_sentar:
        # Mensagem entregue: cliente está aguardando na fila de espera
        print(
            f"🪑 Cliente {cliente_id}: sentou em uma cadeira de espera.",
            flush=True,
        )
        n = barbearia.clientes_aguardando()
        if n >= 0:
            print(f"📋 Clientes aguardando: {n}", flush=True)

    else:
        # ── [SITUAÇÃO 3] Barbearia lotada: cliente vai embora ──────────────────
        # tentar_sentar retornou False → a queue.Queue estava cheia (3/3)
        print(
            f"❌ [SITUAÇÃO 3] Cliente {cliente_id}: "
            f"todas as {CADEIRAS_ESPERA} cadeiras de espera estão ocupadas. "
            "Indo embora!",
            flush=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Ponto de entrada
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python cliente.py <id_cliente>", flush=True)
        print("Exemplo: python cliente.py 1", flush=True)
        sys.exit(1)

    try:
        cid = int(sys.argv[1])
    except ValueError:
        print(
            f"Erro: id_cliente deve ser um número inteiro. "
            f"Recebido: '{sys.argv[1]}'",
            flush=True,
        )
        sys.exit(1)

    executar_cliente(cid)
