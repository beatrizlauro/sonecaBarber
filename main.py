import multiprocessing
import time
import queue

def processo_barbeiro(fila_espera):
    """
    Processo que representa o Barbeiro.
    Gerencia o estado de dormir, acordar e cortar cabelo com base nas mensagens recebidas.
    """
    dormindo = True

    while True:
        # Situação 1: Se o barbeiro está sem clientes, ele dorme [cite: 11, 16]
        if dormindo:
            print("\n[SITUAÇÃO 1] Abertura/Vazia: Todas as cadeiras vazias. O barbeiro senta e tira uma pestana... Zzzzz")

        # O método .get() é bloqueante. O processo "dorme" até receber uma mensagem (um cliente).
        msg_cliente_id = fila_espera.get()

        # Condição de parada para encerrar o programa
        if msg_cliente_id == "FIM":
            break

        # Verifica se o barbeiro estava dormindo quando o cliente chegou
        if dormindo:
            print(f"\n🗣️ Cliente {msg_cliente_id}: ACORDA! Hora de trabalhar seu dorminhoco! [cite: 12]")
            dormindo = False
        else:
            # Se não estava dormindo, apenas chama o próximo da fila de espera [cite: 14]
            print(f"\n💈 Barbeiro: PRÓXIMO! (Chamando Cliente {msg_cliente_id})")

        # Simula o tempo de atendimento do corte de cabelo
        print(f"✂️ Barbeiro: Cortando o cabelo do Cliente {msg_cliente_id}...")
        time.sleep(2) 
        print(f"✅ Barbeiro: Terminou o corte do Cliente {msg_cliente_id}.")

        # Após terminar, verifica se a fila de espera está vazia para voltar a dormir
        if fila_espera.empty():
            dormindo = True


def processo_cliente(cliente_id, fila_espera):
    """
    Processo que representa um Cliente chegando na barbearia.
    Tenta enviar uma mensagem (seu ID) para a fila de espera (as cadeiras).
    """
    print(f"🚶 Cliente {cliente_id}: Chegou na barbearia.")
    try:
        # O put_nowait tenta inserir a mensagem na fila sem bloquear.
        # Se a fila (3 cadeiras de espera) já estiver no limite, ele lança a exceção queue.Full.
        fila_espera.put_nowait(cliente_id)
        
        # O cliente conseguiu entrar: ou foi direto para a cadeira do barbeiro ou sentou na espera.
        print(f"🪑 Cliente {cliente_id}: Entrou (Foi atendido ou sentou em uma das cadeiras de espera).")
    
    except queue.Full:
        # Situação 3: Todas as cadeiras de espera ocupadas. O cliente vai embora.
        print(f"❌ [SITUAÇÃO 3] Cliente {cliente_id}: Todas as 3 cadeiras de espera estão ocupadas. Indo embora!")


if __name__ == '__main__':
    # Inicializa a fila de mensagens (IPC) que atuará como as cadeiras de espera 
    fila_cadeiras_espera = multiprocessing.Queue(maxsize=3)

    # Inicia o processo independente do Barbeiro
    barbeiro_proc = multiprocessing.Process(target=processo_barbeiro, args=(fila_cadeiras_espera,))
    barbeiro_proc.start()

    # Delay para demonstrar a Situação 1 com clareza no terminal
    time.sleep(1)

    print("\n--- [SITUAÇÃO 2] Chegada de múltiplos clientes simultaneamente ---")
    clientes_procs = []

    # Enviamos 5 clientes quase ao mesmo tempo para lotar a barbearia.
    # - O Cliente 1 acordará o barbeiro.
    # - Os Clientes 2, 3 e 4 ocuparão as 3 cadeiras de espera.
    # - O Cliente 5 encontrará a barbearia cheia e irá embora (Situação 3).
    for i in range(1, 6):
        p_cliente = multiprocessing.Process(target=processo_cliente, args=(i, fila_cadeiras_espera))
        clientes_procs.append(p_cliente)
        p_cliente.start()
        # Delay minúsculo apenas para a impressão no terminal não embaralhar
        time.sleep(0.1)

    # Aguarda todos os processos dos clientes da primeira leva finalizarem seu fluxo
    for p in clientes_procs:
        p.join()

    # Dá tempo para o barbeiro atender alguns clientes e liberar cadeiras
    time.sleep(5)
    
    print("\n--- Chega mais um cliente mais tarde (com o barbeiro já trabalhando) ---")
    p_cliente6 = multiprocessing.Process(target=processo_cliente, args=(6, fila_cadeiras_espera))
    p_cliente6.start()
    p_cliente6.join()

    # Aguarda o barbeiro concluir o serviço de todos na fila
    time.sleep(10)

    # Envia a mensagem de encerramento e fecha o processo
    fila_cadeiras_espera.put("FIM")
    barbeiro_proc.join()
    print("\nExpediente encerrado. Soneca Barber fechada!")