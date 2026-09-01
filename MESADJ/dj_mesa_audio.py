import os
import sys
import threading
from enum import Enum, auto

import pygame

PASTA_SONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")

ARQUIVOS_DE_AUDIO = {
    "bateria": "bateria.wav",
    "baixo":   "baixo.wav",
    "synth":   "synth.wav",
    "vocal":   "vocal.wav",
}

_cout_lock = threading.Lock()


def print_seguro(msg: str) -> None:
    with _cout_lock:
        print(msg)


class Estado(Enum):
    TOCANDO = auto()
    PAUSADO = auto()
    PARADO = auto()


class Instrumento(threading.Thread):

    def __init__(self, nome: str, caminho_audio: str, volume: float = 0.8):
        super().__init__(daemon=True)
        self.nome = nome
        self._caminho_audio = caminho_audio
        self._volume = volume

        self._cond = threading.Condition()
        self._estado = Estado.TOCANDO  
        self._som = pygame.mixer.Sound(caminho_audio)
        self._som.set_volume(volume)
        self._channel = None  

    def pausar(self) -> None:
        with self._cond:
            if self._estado == Estado.TOCANDO:
                self._estado = Estado.PAUSADO
                print_seguro(f"  -> {self.nome} PAUSADO.")
            else:
                print_seguro(f"  -> {self.nome} já não estava tocando.")
            self._cond.notify_all()

    def retomar(self) -> None:
        with self._cond:
            if self._estado == Estado.PAUSADO:
                self._estado = Estado.TOCANDO
                print_seguro(f"  -> {self.nome} RETOMANDO.")
            else:
                print_seguro(f"  -> {self.nome} já estava tocando.")
            self._cond.notify_all()

    def encerrar(self) -> None:
        with self._cond:
            self._estado = Estado.PARADO
            self._cond.notify_all()

    def get_estado(self) -> Estado:
        with self._cond:
            return self._estado

    def run(self) -> None:
        self._channel = self._som.play(loops=-1)
        print_seguro(f">> {self.nome} entrou na mesa ({self._caminho_audio}).")

        with self._cond:
            if self._estado == Estado.PAUSADO:
                self._channel.pause()

            while self._estado != Estado.PARADO:
                if self._estado == Estado.PAUSADO:
                    self._channel.pause()
                elif self._estado == Estado.TOCANDO:
                    self._channel.unpause()
                self._cond.wait()

        self._channel.stop()
        print_seguro(f"<< {self.nome} saiu da mesa.")


def imprimir_ajuda() -> None:
    print_seguro(
        "\nComandos disponiveis:\n"
        "  play <faixa>    - retoma a faixa\n"
        "  pause <faixa>   - pausa a faixa\n"
        "  status          - mostra o estado de todas as faixas\n"
        "  list            - lista os nomes das faixas\n"
        "  help            - mostra esta ajuda\n"
        "  exit / sair     - encerra o programa\n"
    )


def carregar_mesa() -> dict:
    mesa = {}
    for nome_chave, arquivo in ARQUIVOS_DE_AUDIO.items():
        caminho = os.path.join(PASTA_SONS, arquivo)
        if not os.path.isfile(caminho):
            print_seguro(f"[AVISO] Arquivo nao encontrado, pulando '{nome_chave}': {caminho}")
            continue
        mesa[nome_chave] = Instrumento(nome_chave.capitalize(), caminho)
    return mesa


def main() -> None:
    pygame.mixer.init()

    mesa = carregar_mesa()
    if not mesa:
        print_seguro(
            "Nenhum arquivo de audio encontrado em '" + PASTA_SONS + "'.\n"
            "Crie a pasta 'sons/' com os arquivos .wav/.ogg/.mp3 e ajuste "
            "ARQUIVOS_DE_AUDIO no topo do script."
        )
        return

    print_seguro("=== Mesa de DJ (Python / threading + pygame.mixer) ===")
    print_seguro("Faixas disponiveis: " + ", ".join(mesa.keys()))
    imprimir_ajuda()

    for inst in mesa.values():
        inst.start()

    try:
        while True:
            try:
                linha = input("\nDJ> ").strip()
            except EOFError:
                break

            if not linha:
                continue

            partes = linha.split()
            comando = partes[0].lower()
            alvo = partes[1].lower() if len(partes) > 1 else ""

            if comando in ("exit", "sair", "quit"):
                break
            elif comando in ("help", "ajuda"):
                imprimir_ajuda()
            elif comando in ("list", "listar"):
                print_seguro("Faixas: " + " ".join(mesa.keys()))
            elif comando == "status":
                linhas = ["\n--- Status da mesa ---"]
                for inst in mesa.values():
                    linhas.append(f"  {inst.nome}: {inst.get_estado().name}")
                print_seguro("\n".join(linhas))
            elif comando in ("pause", "pausar"):
                inst = mesa.get(alvo)
                if inst is None:
                    print_seguro(f"Faixa '{alvo}' nao encontrada. Use 'list'.")
                else:
                    inst.pausar()
            elif comando in ("play", "resume", "retomar"):
                inst = mesa.get(alvo)
                if inst is None:
                    print_seguro(f"Faixa '{alvo}' não encontrada. Use 'list'.")
                else:
                    inst.retomar()
            else:
                print_seguro("Comando desconhecido. Digite 'help' para ver as opcoes.")
    except KeyboardInterrupt:
        pass

    print_seguro("\nEncerrando a mesa de DJ...")
    for inst in mesa.values():
        inst.encerrar()
    for inst in mesa.values():
        inst.join(timeout=2)
    pygame.mixer.quit()
    print_seguro("Até a proxima!")


if __name__ == "__main__":
    sys.exit(main())
