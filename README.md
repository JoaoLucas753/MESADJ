# MESADJ

Simulador de uma mesa de DJ onde diferentes faixas musicais (instrumentos)
tocam simultaneamente, cada uma em sua própria thread, de forma
independente. O DJ controla cada faixa através de comandos de texto,
pausando e retomando a reprodução sem afetar as demais.

## Conceitos aplicados

- **Threads**: cada instrumento (Bateria, Baixo, Synth, Vocal) roda em uma
  thread própria, tocando em loop contínuo, independente das outras.
- **Início e encerramento controlado**: cada thread é iniciada de forma
  explícita e encerrada de maneira segura (aguardando o ciclo atual
  terminar e dando *join*), nunca é interrompida à força.
- **Sincronização de estado**: o estado de cada instrumento
  (`TOCANDO` / `PAUSADO` / `PARADO`) é protegido por um
  `threading.Condition`, garantindo que apenas uma thread modifique esse
  estado por vez — sem *race conditions* e sem *busy waiting* (a thread
  dorme enquanto pausada, em vez de ficar checando o tempo todo).

## Como rodar (Python)
1. Tenha o **Python 3.10 ou superior** instalado.
2. Abra o terminal na pasta do projeto.
3. Instale o Pygame:

```bash
pip install pygame

## Comandos disponíveis

| Comando           | O que faz                                  |
|--------------------|---------------------------------------------|
| `play <faixa>`     | Retoma a faixa (ex: `play bateria`)          |
| `pause <faixa>`    | Pausa a faixa (ex: `pause synth`)            |
| `status`           | Mostra o estado atual de todas as faixas     |
| `list`             | Lista os nomes das faixas disponíveis        |
| `help`             | Mostra a lista de comandos                   |
| `exit` / `sair`    | Encerra o programa, parando todas as threads |

Faixas padrão: `bateria`, `baixo`, `synth`, `vocal`.
