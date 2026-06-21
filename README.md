# 💈 Soneca Barber - Trabalho de Sistemas Distribuídos

Aplicação desenvolvida como trabalho prático da disciplina de **Sistemas Distribuídos**. O projeto implementa o problema clássico de concorrência conhecido como "Barbeiro Dorminhoco" (*Sleeping Barber*), utilizando a linguagem Python para demonstrar a comunicação e sincronização através da troca de mensagens entre processos independentes.

---

## 👥 Integrantes do Grupo

- Beatriz da Costa Lauro
- Brenda Bonaita de Oliveira

---

## 🎯 Objetivo do Projeto

Implementar a simulação da barbearia **Soneca Barber** através de troca de mensagens entre processos. O objetivo prático é aplicar conceitos de concorrência, comunicação interprocessos (IPC) e controle de filas para garantir que o barbeiro seja acordado quando há clientes, atenda o próximo da fila adequadamente, e que o limite de cadeiras de espera seja respeitado.

---

## 🧩 Funcionalidades Implementadas
### ✅ Situações Obrigatórias Demonstradas

- **[SITUAÇÃO 1] Abertura da barbearia**: O programa inicia com todas as cadeiras vazias e o processo do barbeiro entra em estado de dormência, tirando uma pestana.
- **[SITUAÇÃO 2] Atendimento e Espera**: Quando clientes chegam, o barbeiro atende um cliente, enquanto os demais ocupam as cadeiras de espera (representadas pela fila de mensagens).
- **[SITUAÇÃO 3] Desistência por Lotação**: Se a barbearia recebe um cliente e todas as 3 cadeiras de espera já estão ocupadas, o cliente vai embora imediatamente sem ser atendido.

> As três situações aparecem destacadas com essas mesmas etiquetas (`[SITUAÇÃO 1]`, `[SITUAÇÃO 2]`, `[SITUAÇÃO 3]`) tanto nos logs do terminal (`main.py`) quanto no registro de eventos da simulação visual (`soneca-barber-simulacao.html`), facilitando a identificação durante a correção.

### ✨ Aspectos Técnicos e Ferramentas

- **Multiprocessamento**: O barbeiro e cada cliente rodam em instâncias de processos de sistema operacional diferentes usando a biblioteca nativa `multiprocessing`.
- **Comunicação por Fila (Queue)**: Uma fila com tamanho máximo definido (`maxsize=3`) é utilizada para a troca segura de mensagens (IDs dos clientes) entre os processos, simulando fisicamente as cadeiras de espera.

---

## ▶️ Como Executar

### Script Python (`main.py`)

1. **Clone o repositório** para sua máquina local.
2. **Certifique-se** de ter o Python 3 instalado.
3. **Abra o terminal** na raiz do projeto.
4. **Execute a aplicação** com o comando `python main.py`.

Acompanhe os logs no terminal que detalham a chegada dos clientes, o estado do barbeiro e a ocupação das cadeiras.

### Simulação Visual (`soneca-barber-simulacao.html`)

Não requer instalação de nada. Basta **abrir o arquivo `soneca-barber-simulacao.html` diretamente em qualquer navegador moderno** (Chrome, Firefox, Edge), dando duplo clique nele ou arrastando-o para a janela do navegador.

---

## 🖥️ Simulação Interativa (HTML)

Além do script Python (entrega oficial do trabalho), o projeto inclui `soneca-barber-simulacao.html`: uma visualização interativa, escrita em HTML/CSS/JavaScript puro (sem dependências), que reproduz **a mesma lógica de fila com `maxsize=3`** usada em `main.py` — ou seja, as mesmas regras de concorrência, só que com uma interface gráfica para facilitar a apresentação do trabalho.

**Elementos da cena:**
- Uma placa giratória de barbearia (*barber pole*) que gira enquanto o barbeiro corta cabelo e exibe "Zzz" quando ele está dormindo.
- 3 cadeiras de espera, que se preenchem com o ID do cliente assim que ele chega.
- A cadeira do barbeiro, mostrando o cliente atual sendo atendido, com tesoura animada e barra de progresso do corte.
- Um console no estilo "rolo de senha" com o registro de todos os eventos em tempo real — as mesmas mensagens impressas por `main.py`, incluindo as etiquetas `[SITUAÇÃO 1]`, `[SITUAÇÃO 2]` e `[SITUAÇÃO 3]`.
- Um aviso (*toast*) vermelho sempre que um cliente é recusado por lotação.

**Controles disponíveis:**

| Botão | Ação |
|---|---|
| ▶ Rodar simulação completa | Dispara automaticamente a mesma sequência de chegadas do `main.py`: uma leva rápida de 5 clientes (gerando as Situações 2 e 3) seguida de um 6º cliente posterior, demonstrando que o sistema continua funcionando normalmente. |
| + Adicionar cliente | Adiciona manualmente um cliente por vez, a qualquer momento — útil para testar/demonstrar qualquer uma das três situações sob demanda. |
| 🔒 Encerrar expediente | Envia a mensagem de controle `"FIM"` para o barbeiro, encerrando o expediente manualmente. |
| ↺ Reiniciar | Restaura a cena para o estado inicial (cadeiras vazias, barbeiro dormindo). |
| Velocidade (0.5×/1×/2×) | Acelera ou desacelera todas as animações e tempos de corte proporcionalmente. |

> ⚠️ A simulação em HTML é apenas uma ferramenta de apoio visual para apresentação/estudo. Conforme o enunciado, **a entrega oficial do trabalho é o código Python documentado dos processos** (`main.py`).

---

## 🗂️ Estrutura do Código

O código-fonte está estruturado de forma modular e clara:

- **`processo_barbeiro`**: Função que mantém um loop contínuo gerenciando o estado do barbeiro (dormindo ou trabalhando). Ela retira clientes da fila e simula o tempo de corte de cabelo.
- **`processo_cliente`**: Função que representa a chegada de um cliente na barbearia. Ela tenta colocar uma mensagem (seu ID) na fila de espera e lida com a exceção caso a barbearia esteja lotada.
- **`_enviar_leva_de_clientes`**: Função auxiliar que dispara um lote de processos `processo_cliente` em sequência (com pequeno atraso entre chegadas) e aguarda todos terminarem.
- **`main` / `__main__`**: Responsável por instanciar a `Queue`, iniciar o processo do barbeiro e enviar levas de clientes em tempos calculados para forçar e demonstrar as três situações exigidas pelo problema.
- **`soneca-barber-simulacao.html`**: Visualização interativa e independente (não faz parte da entrega formal) que espelha a mesma lógica de fila/estados para fins de apresentação.

---

*Projeto desenvolvido para a disciplina de Sistemas Distribuídos do 7° Período do curso de Sistemas de Informação da Universidade do Estado de Minas Gerais (UEMG).*