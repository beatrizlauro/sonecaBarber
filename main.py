"""
Soneca Barber - Simulação do Problema do Barbeiro Dorminhoco (Sleeping Barber)
================================================================================

Trabalho de Sistemas Distribuídos (UEMG) — Implementação de uma barbearia
através de TROCA DE MENSAGENS entre processos independentes.

Modelagem do problema
----------------------
- 1 processo "Barbeiro": fica dormindo enquanto não há clientes. Ao receber
  uma mensagem, acorda (se estava dormindo) ou chama o próximo (se já
  estava acordado), atende um cliente por vez até terminar o corte.
- N processos "Cliente": cada cliente é um processo do sistema operacional
  independente que chega à barbearia e tenta ocupar uma cadeira de espera.

A comunicação entre os processos é feita exclusivamente através de uma
``multiprocessing.Queue`` (fila de mensagens), que cumpre dois papéis ao
mesmo tempo:

1. Canal de troca de mensagens: os clientes "avisam" o barbeiro de sua
   chegada enviando seu ID pela fila; o barbeiro recebe (`get`) essas
   mensagens para saber quem atender.
2. Cadeiras de espera físicas: o parâmetro ``maxsize=CADEIRAS_ESPERA``
   limita a fila a 3 mensagens pendentes. Se a fila está cheia, não há
   cadeira de espera livre e o cliente que chegar vai embora.

As 3 situações exigidas pelo enunciado ficam marcadas nos logs com as
etiquetas ``[SITUAÇÃO 1]``, ``[SITUAÇÃO 2]`` e ``[SITUAÇÃO 3]``:

1. Abertura da barbearia: todas as cadeiras vazias e o barbeiro dormindo.
2. Clientes chegam, o barbeiro atende um, e os demais ocupam as cadeiras
   de espera (a fila continua não-vazia quando um corte termina).
3. Um cliente chega com as 3 cadeiras de espera ocupadas e vai embora
   (``queue.Full`` ao tentar entrar na fila cheia).
"""

import multiprocessing
import time
import queue

CADEIRAS_ESPERA = 3        # Capacidade da fila = nº de cadeiras de espera
TEMPO_CORTE_SEGUNDOS = 2   # Duração simulada de cada corte de cabelo


def processo_barbeiro(fila_espera: multiprocessing.Queue) -> None:
    """
    Processo do Barbeiro.

    Mantém um loop infinito alternando entre dois estados:

    - ``dormindo=True``: a cadeira do barbeiro está livre; ele "tira uma
      pestana" até chegar uma mensagem pela fila.
    - ``dormindo=False``: o barbeiro está acordado; ao terminar um corte,
      verifica se há mais mensagens (clientes esperando) e chama o
      próximo, ou volta a dormir se a fila estiver vazia.

    A chamada ``fila_espera.get()`` bloqueia o processo até que uma
    mensagem esteja disponível — é exatamente essa troca de mensagens
    (e não variáveis compartilhadas) que sincroniza o barbeiro com os
    clientes.

    Parâmetros
    ----------
    fila_espera:
        Canal de mensagens compartilhado entre o barbeiro e os clientes.
        Cada mensagem é o ID (``int``) de um cliente, ou a string ``"FIM"``
        para sinalizar o encerramento do expediente.
    """
    dormindo = True

    while True:
        # [SITUAÇÃO 1] Barbearia vazia: barbeiro dormindo na cadeira.
        if dormindo:
            print(
                "\n[SITUAÇÃO 1] Barbearia vazia: "
                "o barbeiro senta na cadeira e tira uma pestana... Zzzzz",
                flush=True,
            )

        # Bloqueia até chegar uma mensagem (troca de mensagens entre processos)
        msg_cliente_id = fila_espera.get()

        # Mensagem de controle para encerrar o expediente
        if msg_cliente_id == "FIM":
            print("\n💈 Barbeiro: Encerrando expediente.", flush=True)
            break

        if dormindo:
            # O cliente que acabou de chegar precisa acordar o dorminhoco
            print(
                f"\n🗣️ Cliente {msg_cliente_id}: "
                "ACORDA! Hora de trabalhar seu dorminhoco!",
                flush=True,
            )
            dormindo = False
        else:
            # Barbeiro já estava acordado: terminou o corte anterior e
            # chama o próximo cliente que estava em uma cadeira de espera
            print(
                f"\n💈 Barbeiro: PRÓXIMO! "
                f"(chamando Cliente {msg_cliente_id})",
                flush=True,
            )

        print(f"💺 Cliente {msg_cliente_id}: sentou na cadeira do barbeiro.", flush=True)

        # --- Simulação do corte de cabelo ---
        print(f"✂️ Barbeiro: cortando o cabelo do Cliente {msg_cliente_id}...", flush=True)
        time.sleep(TEMPO_CORTE_SEGUNDOS)
        print(f"✅ Barbeiro: terminou o corte do Cliente {msg_cliente_id}.", flush=True)

        # [SITUAÇÃO 2] Se a fila ainda não está vazia, esses clientes
        # estavam sentados nas cadeiras de espera durante o corte acima.
        if fila_espera.empty():
            print("😴 Barbeiro: não há mais clientes. Vou voltar a dormir.", flush=True)
            dormindo = True
        else:
            print(
                f"[SITUAÇÃO 2] 📋 Ainda há clientes nas cadeiras de espera "
                f"({fila_espera.qsize()} aguardando).",
                flush=True,
            )
            dormindo = False


def processo_cliente(cliente_id: int, fila_espera: multiprocessing.Queue) -> None:
    """
    Processo de um Cliente chegando na barbearia.

    Cada cliente roda em um processo de SO independente e tenta colocar
    seu ID na fila (mensagem para o barbeiro) sem bloquear
    (``put_nowait``). Como a fila tem ``maxsize=CADEIRAS_ESPERA``, ela
    levanta ``queue.Full`` quando as 3 cadeiras de espera já estão
    ocupadas — nesse caso o cliente desiste e vai embora.

    Parâmetros
    ----------
    cliente_id:
        Identificador do cliente, usado nas mensagens trocadas.
    fila_espera:
        Canal de mensagens compartilhado com o processo do barbeiro.
    """
    print(f"🚶 Cliente {cliente_id}: chegou na barbearia.", flush=True)

    try:
        # Tenta ocupar uma cadeira de espera sem bloquear o processo
        fila_espera.put_nowait(cliente_id)
        print(f"🪑 Cliente {cliente_id}: sentou em uma cadeira de espera.", flush=True)

        try:
            print(f"📋 Clientes aguardando: {fila_espera.qsize()}", flush=True)
        except NotImplementedError:
            # qsize() não é garantida em todas as plataformas (ex.: macOS)
            pass

    except queue.Full:
        # [SITUAÇÃO 3] Todas as cadeiras de espera estão ocupadas
        print(
            f"❌ [SITUAÇÃO 3] Cliente {cliente_id}: "
            f"todas as {CADEIRAS_ESPERA} cadeiras de espera estão ocupadas. "
            f"Indo embora!",
            flush=True,
        )


def _enviar_leva_de_clientes(
    ids_clientes,
    fila_espera: multiprocessing.Queue,
    atraso_entre_chegadas: float = 0.1,
) -> None:
    """
    Dispara um processo Cliente para cada ID em ``ids_clientes`` e aguarda
    todos terminarem (``join``) antes de retornar.

    O ``atraso_entre_chegadas`` simula clientes chegando em sequência
    rápida — propositalmente bem menor que ``TEMPO_CORTE_SEGUNDOS`` para
    forçar o enchimento das cadeiras de espera (e, com clientes
    suficientes, a recusa por lotação).
    """
    processos = []
    for cliente_id in ids_clientes:
        p = multiprocessing.Process(
            target=processo_cliente, args=(cliente_id, fila_espera)
        )
        processos.append(p)
        p.start()
        time.sleep(atraso_entre_chegadas)

    for p in processos:
        p.join()


def main() -> None:
    fila_cadeiras_espera = multiprocessing.Queue(maxsize=CADEIRAS_ESPERA)

    # Inicia o processo do barbeiro. [SITUAÇÃO 1] é demonstrada logo de
    # cara: a barbearia abre com as cadeiras vazias e o barbeiro dormindo.
    barbeiro_proc = multiprocessing.Process(
        target=processo_barbeiro, args=(fila_cadeiras_espera,)
    )
    barbeiro_proc.start()

    print("\n==============================")
    print("Primeira leva de clientes")
    print("==============================")

    # 5 clientes chegando em sequência rápida (0.1s entre cada um). Como o
    # corte demora 2s — bem mais que o intervalo de chegada — as 3
    # cadeiras de espera enchem e o 5º cliente é recusado:
    # demonstra [SITUAÇÃO 2] (cadeiras ocupadas) e [SITUAÇÃO 3] (lotação).
    _enviar_leva_de_clientes(range(1, 6), fila_cadeiras_espera)

    # Aguarda alguns cortes acontecerem, liberando cadeiras de espera.
    time.sleep(5)

    print("\n==============================")
    print("Novo cliente chegando")
    print("==============================")

    # Demonstra que o sistema continua funcionando normalmente após o
    # pico inicial de clientes.
    _enviar_leva_de_clientes([6], fila_cadeiras_espera)

    # Aguarda o atendimento dos clientes restantes terminar.
    time.sleep(10)

    # Encerra o expediente: mensagem de controle "FIM" para o barbeiro.
    fila_cadeiras_espera.put("FIM")
    barbeiro_proc.join()

    print("\n🏁 Expediente encerrado. Soneca Barber fechada!")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
