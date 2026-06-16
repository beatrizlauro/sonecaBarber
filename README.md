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

- **Abertura da barbearia**: O programa inicia com todas as cadeiras vazias e o processo do barbeiro entra em estado de dormência, tirando uma pestana.
- **Atendimento e Espera**: Quando clientes chegam, o barbeiro atende um cliente, enquanto os demais ocupam as cadeiras de espera (representadas pela fila de mensagens).
- **Desistência por Lotação**: Se a barbearia recebe um cliente e todas as 3 cadeiras de espera já estão ocupadas, o cliente vai embora imediatamente sem ser atendido.

### ✨ Aspectos Técnicos e Ferramentas

- **Multiprocessamento**: O barbeiro e cada cliente rodam em instâncias de processos de sistema operacional diferentes usando a biblioteca nativa `multiprocessing`.
- **Comunicação por Fila (Queue)**: Uma fila com tamanho máximo definido (`maxsize=3`) é utilizada para a troca segura de mensagens (IDs dos clientes) entre os processos, simulando fisicamente as cadeiras de espera.

---

## ▶️ Como Executar

1. **Clone o repositório** para sua máquina local.
2. **Certifique-se** de ter o Python 3 instalado.
3. **Abra o terminal** na raiz do projeto.
4. **Execute a aplicação** com o comando `python main.py`.

Acompanhe os logs no terminal que detalham a chegada dos clientes, o estado do barbeiro e a ocupação das cadeiras.

---

## 🗂️ Estrutura do Código

O código-fonte está estruturado de forma modular e clara:

- **`processo_barbeiro`**: Função que mantém um loop contínuo gerenciando o estado do barbeiro (dormindo ou trabalhando). Ela retira clientes da fila e simula o tempo de corte de cabelo.
- **`processo_cliente`**: Função que representa a chegada de um cliente na barbearia. Ela tenta colocar uma mensagem (seu ID) na fila de espera e lida com a exceção caso a barbearia esteja lotada.
- **`Bloco Principal (__main__)`**: Responsável por instanciar a `Queue`, iniciar o processo do barbeiro e enviar blocos de clientes em tempos calculados para forçar e demonstrar as três situações exigidas pelo problema.

---

*Projeto desenvolvido para a disciplina de Sistemas Distribuídos do 7° Período do curso de Sistemas de Informação da Universidade do Estado de Minas Gerais (UEMG).*