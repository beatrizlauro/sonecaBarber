# 💈 Soneca Barber

> Trabalho prático da disciplina de **Sistemas Distribuídos** — implementação do problema clássico de concorrência **Barbeiro Dorminhoco** (*Sleeping Barber*) com comunicação via sockets TCP em Python.

---

## 👥 Integrantes do Grupo

- Beatriz da Costa Lauro
- Brenda Bonaita de Oliveira

**Curso:** Sistemas de Informação — 7° Período  
**Instituição:** Universidade do Estado de Minas Gerais (UEMG)

---

## 🎯 Objetivo do Projeto

Implementar a simulação da barbearia **Soneca Barber** através de troca de mensagens real entre processos isolados, aplicando conceitos de:

- Comunicação interprocessos (IPC) em rede
- Controle de filas remotas
- Concorrência distribuída

O barbeiro é acordado quando há clientes, atende o próximo da fila adequadamente através de chamadas remotas e respeita rigidamente o limite das cadeiras de espera.

---

## 🧩 Situações Obrigatórias Demonstradas

| Etiqueta | Situação |
|----------|----------|
| `[SITUAÇÃO 1]` | **Abertura da barbearia** — O programa inicia com todas as cadeiras vazias e o processo do barbeiro entra em estado de dormência (Zzzzz). |
| `[SITUAÇÃO 2]` | **Atendimento e Espera** — Novos clientes chegam enquanto o barbeiro está ocupado e ocupam as cadeiras de espera disponíveis (fila remota com limite de 3). |
| `[SITUAÇÃO 3]` | **Desistência por Lotação** — Cliente chega com todas as 3 cadeiras já ocupadas; a mensagem é recusada e o cliente vai embora imediatamente. |

As três situações aparecem destacadas com as etiquetas exatas nos logs dos scripts Python **e** no registro de eventos da simulação visual (`soneca-barber-simulacao.html`).

---

## ✨ Aspectos Técnicos e IPC

- **Processos Isolados no S.O.** — O barbeiro e cada cliente rodam em instâncias totalmente independentes, com espaços de memória próprios e PIDs distintos (sem threads ou memória compartilhada global).
- **Servidor de Mensagens TCP (`BaseManager`)** — O processo do barbeiro disponibiliza um servidor via `multiprocessing.managers.BaseManager`, expondo o objeto `Barbearia` remotamente por proxy TCP autenticado.
- **Comunicação por Clientes Distribuídos** — Cada execução do cliente conecta-se ao servidor via sockets TCP e invoca métodos remotos (`barbearia.tentar_sentar(id)`) para enviar a mensagem de chegada.
- **Fila Protegida (`Queue`)** — As 3 cadeiras de espera são gerenciadas por `queue.Queue(maxsize=3)`, garantindo atomicidade e comportamento síncrono das requisições.

---

## 🗂️ Estrutura do Código

```
sonecaBarber/
├── barbeiro.py                   # Servidor TCP + loop consumidor da fila
├── cliente.py                    # Processo cliente isolado (recebe ID via argv)
├── demonstracao.py               # Script orquestrador automático
└── soneca-barber-simulacao.html  # Interface visual interativa (abre no navegador)
```

### Descrição dos arquivos

**`barbeiro.py`**  
Gerencia o processo principal do Barbeiro e a infraestrutura de rede. Cria a classe `Barbearia` protegida por travas, inicializa a thread do servidor de mensagens TCP na porta `50000` e executa o loop consumidor que retira IDs da fila distribuída para processar os cortes.

**`cliente.py`**  
Representa a unidade isolada de um cliente. É invocado com um ID via argumento de linha de comando (`sys.argv`), estabelece conexão TCP com o `BaseManager` do barbeiro, obtém o proxy da barbearia e faz a postagem síncrona da chegada — tratando retorno de sucesso ou rejeição por lotação.

**`demonstracao.py`**  
O script maestro do projeto. Automatiza o setup dos sockets, injeta atrasos controlados com `time.sleep`, dispara lotes sequenciais de processos via `subprocess.Popen` e encerra com a mensagem de controle `"FIM"`.

**`soneca-barber-simulacao.html`**  
Camada visual independente em JavaScript Vanilla, com fila de promessas assíncronas que espelha fielmente as regras e restrições dos scripts Python — incluindo a comunicação com o servidor local em `127.0.0.1:50000`.

---

## ▶️ Como Executar

### Opção 1 — Script Orquestrador (recomendado)

```bash
python demonstracao.py
```

O script inicia automaticamente o servidor em plano de fundo (`barbeiro.py`), aguarda a inicialização do socket TCP e dispara lotes sequenciais de processos (`cliente.py`) simulando picos de chegada e o encerramento do expediente.

---

### Opção 2 — Simulação Visual

Abra o arquivo `soneca-barber-simulacao.html` diretamente no navegador (Chrome, Firefox, Edge ou Safari). Não requer instalação de dependências.

---

## 🖥️ Simulação Interativa (HTML)

A interface gráfica espelha a mesma cadência de temporização e lógica de fila distribuída com `maxsize=3`, simulando inclusive a comunicação com o servidor local em `127.0.0.1:50000`.

### Elementos visuais

- **3 Cadeiras de Espera** — Exibem slots livres ou ocupados com o número do cliente na fila.
- **Cadeira de Corte** — Mostra o cliente em atendimento e barra de progresso em tempo real.
- **Console de Eventos** — Log idêntico ao terminal Python, com as marcações `[SITUAÇÃO 1]`, `[SITUAÇÃO 2]` e `[SITUAÇÃO 3]`.

### Controles

| Botão | Ação |
|-------|------|
| ▶ Rodar simulação completa | Executa a sequência programada: onda de 5 clientes simultâneos + pausa + cliente 6 + encerramento. |
| + Adicionar cliente | Dispara manualmente um novo processo cliente. |
| 🔒 Encerrar expediente | Transmite a mensagem `"FIM"` — barbeiro conclui atendimentos e encerra o servidor. |
| ↺ Reiniciar | Limpa conexões, esvazia a fila e recoloca o barbeiro em repouso. |
| Velocidade (0.5×/1×/2×) | Ajusta a escala de tempo das animações e rotinas assíncronas. |

---

## 🔧 Requisitos

- Python 3.8+
- Módulos da biblioteca padrão: `multiprocessing`, `queue`, `subprocess`, `socket`, `time`, `sys`
- Navegador moderno para a simulação visual (sem dependências externas)
