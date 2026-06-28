"""
Responsabilidade deste script
-------------------------------
Orquestrar a demonstração das 3 situações exigidas pelo enunciado,
disparando ``barbeiro.py`` e múltiplos ``cliente.py`` como processos
independentes do sistema operacional via ``subprocess.Popen``.

Cada processo tem seu próprio PID, espaço de memória e se comunica
exclusivamente via troca de mensagens TCP (o servidor de mensagens
do Barbeiro), sem variáveis globais compartilhadas.

Situações demonstradas
-----------------------
[SITUAÇÃO 1] Abertura: barbearia vazia e barbeiro dormindo.
             → O 1º cliente a chegar precisa acordá-lo.

[SITUAÇÃO 2] Cadeiras de espera ocupadas.
             → Clientes 2, 3 e 4 chegam enquanto o corte do 1º ainda
               está em andamento (corte=2s, intervalo entre chegadas=0.1s).

[SITUAÇÃO 3] Barbearia lotada.
             → O 5º cliente chega e todas as 3 cadeiras estão ocupadas;
               ``tentar_sentar`` retorna False e ele vai embora.

Uso
----
    python demonstracao.py

Pré-requisito
--------------
    barbeiro.py e cliente.py devem estar no mesmo diretório.
"""

import os
import subprocess
import sys
import time
from multiprocessing.managers import BaseManager

# ── Diretório do próprio script ────────────────────────────────────────────────
# Garante que barbeiro.py e cliente.py são encontrados mesmo quando o
# demonstracao.py é executado a partir de outro diretório de trabalho.
_BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

def _script(nome: str) -> str:
    """Retorna o caminho absoluto de um script no mesmo diretório deste arquivo."""
    return os.path.join(_BASE_DIR, nome)

# ── Configurações ──────────────────────────────────────────────────────────────
PYTHON: str = sys.executable        # mesmo interpretador Python do ambiente atual
ATRASO_ENTRE_CHEGADAS: float = 0.1  # segundos entre chegadas consecutivas (< TEMPO_CORTE)
ESPERA_ENTRE_LEVAS: float = 7.0     # aguarda cortes da 1ª leva antes da 2ª
ESPERA_FINAL: float = 8.0           # aguarda término dos atendimentos restantes

# Credenciais do servidor de mensagens (devem coincidir com barbeiro.py)
GERENCIADOR_HOST: str = "127.0.0.1"
GERENCIADOR_PORTA: int = 50000
GERENCIADOR_SENHA: bytes = b"sonecabarber"


# ── Proxy para envio do sinal de encerramento ──────────────────────────────────

class GerenciadorBarbearia(BaseManager):
    """Proxy-cliente usado apenas para enviar o sinal de encerramento."""
    pass


GerenciadorBarbearia.register("obter_barbearia")


# ══════════════════════════════════════════════════════════════════════════════
# Funções auxiliares
# ══════════════════════════════════════════════════════════════════════════════

def disparar_cliente(cliente_id: int) -> subprocess.Popen:
    """
    Dispara ``cliente.py`` como um processo de SO independente.

    stdout e stderr são herdados do processo pai, portanto os prints de
    cada cliente aparecem intercalados no mesmo terminal — comportamento
    esperado em sistemas distribuídos concorrentes.

    Parâmetros
    ----------
    cliente_id : int
        ID passado como argumento de linha de comando ao ``cliente.py``.

    Retorna
    -------
    subprocess.Popen
        Handle do processo filho; use ``.wait()`` para aguardá-lo terminar.
    """
    return subprocess.Popen([PYTHON, _script("cliente.py"), str(cliente_id)])


def encerrar_expediente() -> None:
    """
    Conecta ao servidor de mensagens e envia a mensagem de controle ``"FIM"``.

    O Barbeiro recebe essa mensagem na sua fila e encerra o loop
    graciosamente, sem forçar kill no processo.
    """
    gerenciador = GerenciadorBarbearia(
        address=(GERENCIADOR_HOST, GERENCIADOR_PORTA),
        authkey=GERENCIADOR_SENHA,
    )
    gerenciador.connect()
    gerenciador.obter_barbearia().encerrar_expediente()
    print("📴 Sinal de encerramento enviado ao Barbeiro.", flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# Demonstração principal
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Orquestra a demonstração completa das 3 situações.

    Sequência de eventos
    ---------------------
    1. Inicia ``barbeiro.py`` (servidor + loop do Barbeiro).
    2. Aguarda 1.5s para o servidor de mensagens ficar disponível.
    3. Dispara 5 clientes com intervalo de 0.1s entre eles:
       - Cliente 1  → acorda o Barbeiro [SITUAÇÃO 1]
       - Clientes 2-4 → ocupam as 3 cadeiras de espera [SITUAÇÃO 2]
       - Cliente 5  → barbearia lotada, vai embora [SITUAÇÃO 3]
    4. Aguarda 7s para os cortes da 1ª leva ocorrerem.
    5. Dispara o Cliente 6 para demonstrar funcionamento contínuo.
    6. Aguarda atendimentos finais e encerra o expediente.
    """

    print("🚀 Iniciando Soneca Barber...\n", flush=True)

    # ── Passo 1: inicia o processo do Barbeiro ─────────────────────────────────
    # ``barbeiro.py`` sobe o servidor de mensagens e começa a aguardar clientes
    barbeiro_proc = subprocess.Popen([PYTHON, _script("barbeiro.py")])

    # ── Passo 2: aguarda o servidor TCP ficar disponível ──────────────────────
    time.sleep(1.5)

    # ── Passo 3: primeira leva — 5 clientes em sequência rápida ───────────────
    #
    # Com TEMPO_CORTE=2s e ATRASO=0.1s, todos os 5 chegam antes do
    # primeiro corte terminar, garantindo a demonstração das situações 2 e 3:
    #
    #   t=0.0s → Cliente 1 chega: acorda o Barbeiro        [SITUAÇÃO 1]
    #   t=0.1s → Cliente 2 chega: senta na cadeira 1 de espera
    #   t=0.2s → Cliente 3 chega: senta na cadeira 2 de espera  [SITUAÇÃO 2]
    #   t=0.3s → Cliente 4 chega: senta na cadeira 3 de espera
    #   t=0.4s → Cliente 5 chega: barbearia lotada, vai embora  [SITUAÇÃO 3]
    #   t=2.0s → Corte do Cliente 1 termina; Barbeiro chama o próximo
    #
    print("=" * 55)
    print("Primeira leva: 5 clientes chegando em sequência rápida")
    print("=" * 55, flush=True)

    processos_leva1 = []
    for i in range(1, 6):
        p = disparar_cliente(i)
        processos_leva1.append(p)
        time.sleep(ATRASO_ENTRE_CHEGADAS)  # simula chegadas espaçadas

    # Aguarda todos os processos da 1ª leva encerrarem
    for p in processos_leva1:
        p.wait()

    # ── Passo 4: aguarda os cortes da primeira leva ────────────────────────────
    time.sleep(ESPERA_ENTRE_LEVAS)

    # ── Passo 5: segunda leva — demonstra funcionamento contínuo ──────────────
    print("\n" + "=" * 55)
    print("Segunda leva: novo cliente após o pico inicial")
    print("=" * 55, flush=True)

    p6 = disparar_cliente(6)
    p6.wait()

    # ── Passo 6: aguarda atendimento final e encerra expediente ────────────────
    time.sleep(ESPERA_FINAL)

    encerrar_expediente()
    barbeiro_proc.wait()  # aguarda o processo do Barbeiro terminar

    print("\n🏁 Demonstração concluída. Soneca Barber fechada!", flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# Ponto de entrada
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
