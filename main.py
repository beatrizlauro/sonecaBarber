import multiprocessing
import time
import queue

CADEIRAS_ESPERA = 3


def processo_barbeiro(fila_espera):
    """
    Processo que representa o Barbeiro.
    Gerencia o estado de dormir, acordar e cortar cabelo com base nos clientes recebidos.
    """
    dormindo = True

    while True:
        # Situação 1: barbeiro dormindo
        if dormindo:
            print(
                "\n[SITUAÇÃO 1] Barbearia vazia: "
                "O barbeiro senta e tira uma pestana... Zzzzz"
            )

        # Espera até chegar um cliente
        msg_cliente_id = fila_espera.get()

        # Encerramento do programa
        if msg_cliente_id == "FIM":
            print("\n💈 Barbeiro: Encerrando expediente.")
            break

        # Cliente acorda o barbeiro
        if dormindo:
            print(
                f"\n🗣️ Cliente {msg_cliente_id}: "
                "ACORDA! Hora de trabalhar!"
            )
            dormindo = False
        else:
            print(
                f"\n💈 Barbeiro: PRÓXIMO! "
                f"(Chamando Cliente {msg_cliente_id})"
            )

        print(f"💺 Cliente {msg_cliente_id}: Sentou na cadeira do barbeiro.")

        # Simulação do corte
        print(f"✂️ Barbeiro: Cortando o cabelo do Cliente {msg_cliente_id}...")
        time.sleep(2)
        print(f"✅ Barbeiro: Terminou o corte do Cliente {msg_cliente_id}.")

        # Verifica se ainda existem clientes aguardando
        if fila_espera.empty():
            print("😴 Barbeiro: Não há mais clientes. Vou voltar a dormir.")
            dormindo = True
        else:
            dormindo = False


def processo_cliente(cliente_id, fila_espera):
    """
    Processo que representa um cliente chegando na barbearia.
    """
    print(f"🚶 Cliente {cliente_id}: Chegou na barbearia.")

    try:
        fila_espera.put_nowait(cliente_id)

        print(f"🪑 Cliente {cliente_id}: Sentou em uma cadeira de espera.")

        try:
            print(f"📋 Clientes aguardando: {fila_espera.qsize()}")
        except NotImplementedError:
            pass

    except queue.Full:
        print(
            f"❌ [SITUAÇÃO 3] Cliente {cliente_id}: "
            f"Todas as {CADEIRAS_ESPERA} cadeiras de espera estão ocupadas. "
            f"Indo embora!"
        )


if __name__ == "__main__":
    multiprocessing.freeze_support()

    fila_cadeiras_espera = multiprocessing.Queue(
        maxsize=CADEIRAS_ESPERA
    )

    # Inicia o barbeiro
    barbeiro_proc = multiprocessing.Process(
        target=processo_barbeiro,
        args=(fila_cadeiras_espera,)
    )
    barbeiro_proc.start()

    clientes_procs = []

    print("\n==============================")
    print("Primeira leva de clientes")
    print("==============================")

    # Envia 5 clientes
    for i in range(1, 6):
        p_cliente = multiprocessing.Process(
            target=processo_cliente,
            args=(i, fila_cadeiras_espera)
        )

        clientes_procs.append(p_cliente)
        p_cliente.start()

        # Pequeno atraso entre chegadas
        time.sleep(0.1)

    # Aguarda todos os clientes terminarem
    for p in clientes_procs:
        p.join()

    # Aguarda alguns cortes acontecerem
    time.sleep(5)

    print("\n==============================")
    print("Novo cliente chegando")
    print("==============================")

    p_cliente6 = multiprocessing.Process(
        target=processo_cliente,
        args=(6, fila_cadeiras_espera)
    )

    p_cliente6.start()
    p_cliente6.join()

    # Aguarda atendimento terminar
    time.sleep(10)

    # Encerra o barbeiro
    fila_cadeiras_espera.put("FIM")
    barbeiro_proc.join()

    print("\n🏁 Expediente encerrado. Soneca Barber fechada!")