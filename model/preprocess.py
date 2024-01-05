import os, sys
'''
from pathlib import Path
caminho_original = "C:\\Users\\BRAYAN\\Documents\\Projects\\python\\ia melody\\src\\model\\preprocess.py"
caminho_formatado = os.path.join(*caminho_original.split('\\'))
file =  Path(caminho_formatado).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
'''
from model.convert import *
from model.midi import Midi

MIDI_DATASET_IN = "midis"
MIDI_DATASET_OUT = "trat"
SAVE_DIR = "dataset"

def transpose_all(entrada, nome):
    for path, subdirs, files in os.walk(MIDI_DATASET_IN):
        for file in files:
            if file.endswith("mid"):
                if file[:-4] == entrada:
                    list_nomes = abre_arquivos(os.path.join("json", "musicas."+nome+".json"))
                    partes = path.split(os.path.sep)[1:]
                    if partes[-1] not in list_nomes:
                        caminho = os.path.join("trat", *partes)
                        caminho_completo = os.path.join(caminho, file)

                        if not (os.path.exists(caminho) and os.path.exists(caminho_completo)):
                            print("traduzindo:",path, file)

                            partes =  path.split(os.path.sep)
                            if not os.path.isdir(caminho):
                                os.makedirs(caminho)

                            c = os.path.join(path, file)
                            t = Midi.transpose(c)
                            musica = os.path.join(caminho, file)
                            t.write('midi', fp=musica)
                            

def gera_dataset(entrada):
    songs = []
    m = 0
    nome = "saida" if entrada != "h0" else "entrada"
    pre = "s" if entrada != "h0" else "e"
    columns = ["musica", "estilo"]
    nomes = []
    estilos = []

    transpose_all(entrada, nome)

    for path, subdirs, files in os.walk(MIDI_DATASET_OUT):
        
        for file in files:
            if file.endswith("mid"):
                if file[:-4] == entrada:
                    
                    list_nomes = abre_arquivos(os.path.join("json", "musicas."+nome+".json"))
                    partes = path.split(os.path.sep)[1:]
                    if partes[-1] not in list_nomes:
                        print("abrindo:", partes[-1])
                        caminho = os.path.join(MIDI_DATASET_OUT, *partes, file)
                        musica = Midi(caminho=caminho, nome=partes[-1], estilo=partes[-2])

                        songs.append(musica)

    for i, arquivo in enumerate(songs):
        caminho = os.path.join(SAVE_DIR, nome+".csv")
        arquivo.salva_csv(nome_arquivo=caminho, nome=nome, pre=pre)

    return songs

def preprocess():
    print("teste")
    #gera_dataset("h1")
    gera_dataset("h0")

def main():
    preprocess()

if __name__ == "__main__":
    preprocess()