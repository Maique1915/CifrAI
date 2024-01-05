import os
import json
import music21 as m21
from music21 import stream, converter, chord, note, duration
from fractions import Fraction
from track import *

KERN_DATASET_PATH = "midis"
SAVE_DIR = "dataset"
SINGLE_FILE_DATASET = "file_dataset"
MAPPING_PATH = "mapping.json"
SEQUENCE_LENGTH = 64

def has_acceptable_durations(song, acceptable_durations):
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True

def transpose(song):
    parts = song.getElementsByClass(m21.stream.Part)
    measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)
    key = measures_part0[0][4]

    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")

    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    tranposed_song = song.transpose(interval)
    return tranposed_song

def encode_song(song, time_step=0.25):
    encoded_song = []

    for event in song.flat.notesAndRests:

        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi # 60

        elif isinstance(event, m21.note.Rest):
            symbol = "r"

        steps = int(event.duration.quarterLength / time_step)
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")

    encoded_song = " ".join(map(str, encoded_song))

    return encoded_song


def frac2str(g, h):
    nota = 0
    if not isinstance(g, tuple):
        nota = g.midi

    duracao = h.quarterLength
    return (nota, f"{duracao}")

def encode_song(song):
    notas_e_acordes = song.flat.getElementsByClass([chord.Chord, note.Note, note.Rest])

    # Criando um vetor numérico para a harmonia
    notas = []

    # Iterando sobre as notas e acordes
    for nota_ou_acorde in notas_e_acordes:
        # Se for um acorde, adiciona o número de cada nota do acorde ao vetor
        if isinstance(nota_ou_acorde, chord.Chord):
            aux = []
            for pitch in nota_ou_acorde.pitches:
                if(pitch.midi not in aux):
                    aux.append(pitch.midi)
            notas.append((aux, f"{nota_ou_acorde.duration.quarterLength}"))

        # Se for uma nota única, adiciona o número da nota ao vetor
        elif isinstance(nota_ou_acorde, note.Note):
            notas.append(frac2str(nota_ou_acorde.pitch, nota_ou_acorde.duration))
        elif  isinstance(nota_ou_acorde, note.Rest):
            notas.append(frac2str(nota_ou_acorde.pitches, nota_ou_acorde.duration))

    return notas

def preprocess(dataset_path):
    print("Loading songs...")
    songs = load_songs_in_kern(dataset_path)
    print(f"Loaded {len(songs)} songs.")

    for i, song in enumerate(songs):
        #song = transpose(song)
        encoded_song = encode_song(song)
        save_path = os.path.join(SAVE_DIR, str(i))
        print(encoded_song)
        print()
        '''
        with open(save_path, "w") as fp:
            fp.write(song)
        '''

def load(file_path):
    with open(file_path, "r") as fp:
        song = fp.read()
    return song

def create_single_file_dataset(dataset_path, file_dataset_path, sequence_length):
    new_song_delimiter = "/ " * sequence_length
    songs = ""

    # load encoded songs and add delimiters
    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load(file_path)
            songs = songs + song + " " + new_song_delimiter

    songs = songs[:-1]
    with open(file_dataset_path, "w") as fp:
        fp.write(songs)

    return songs

def cria_mapas():
    caminhos_notas = abre_dados("midis", "inst_", "inst_0")
    caminhos_drums = abre_dados("midis", "inst_0")

    lista_nota = []
    lista_velocidade = []

    for caminho_arquivo in caminhos_notas:
        notas, velocidades = lista_notas(caminho_arquivo)
        lista_nota += notas
        lista_velocidade += velocidades

    salvar_arquivo("json/notas.json",sorted(list(set(lista_nota))))
    salvar_arquivo("json/velocidade.json",sorted(list(set(lista_velocidade))))

    lista_nota = []

    for caminho_arquivo in caminhos_drums:
        notas, velocidades = lista_notas(caminho_arquivo)
        lista_nota += notas

    salvar_arquivo("json/drums.json",sorted(list(set(lista_nota))))


def main():
    preprocess(KERN_DATASET_PATH)
    #songs = create_single_file_dataset(SAVE_DIR, SINGLE_FILE_DATASET, SEQUENCE_LENGTH)
    #create_mapping(songs, MAPPING_PATH)

if __name__ == "__main__":
    main()