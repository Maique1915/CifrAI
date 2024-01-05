from unittest import result
import mido, os, json, glob
import music21 as m21
from music21 import scale
import pandas as pd
from model.midi import Midi

SAVE_DIR = "dataset"

def meta(tipo=None, time=None, tempo=None, note=None, name=None, velocity=None, numerator=None, denominator=None, clocks_per_click=None, notated_32nd_notes_per_beat=None):
    ret = {}
    if tipo is not None:
        ret['tipo'] = tipo
    if time is not None:
        ret['time'] = time
    if tempo is not None:
        ret['tempo'] = tempo
    if note is not None:
        ret['note'] = note
    if name is not None:
        ret['name'] = name
    if velocity is not None:
        ret['velocity'] = velocity
    if numerator is not None:
        ret['numerator'] = numerator
    if denominator is not None:
        ret['denominator'] = denominator
    if clocks_per_click is not None:
        ret['clocks_per_click'] = clocks_per_click
    if notated_32nd_notes_per_beat is not None:
        ret['notated_32nd_notes_per_beat'] = notated_32nd_notes_per_beat

    return ret

def abre_dados(pasta, sub_pasta=None, excecao=None):
    arquivos_midi = []
    aux = []
    # Lista todas as pastas
    if sub_pasta == None:
        pastas = glob.glob(os.path.join(os.getcwd(), pasta))
    else:
        pastas = glob.glob(os.path.join(os.getcwd(), pasta, sub_pasta+'*'))

    # Loop sobre as pastas encontradas
    for pasta in pastas:
        # Lista todos os arquivos MIDI na pasta
        if excecao != None:
            if excecao not in pasta:
                aux = glob.glob(os.path.join(pasta, '*.mid'))
        else:
            aux = glob.glob(os.path.join(pasta, '*.mid'))

        for arquivo_midi in aux:
            arquivos_midi.append(arquivo_midi)

    return arquivos_midi

def lista_notas(caminho_arquivo):
    midi = mido.MidiFile(caminho_arquivo)
    notas = []
    velocidades = []

    for faixa in midi.tracks:
        for mensagem in faixa:
            time = mensagem.time
            if mensagem.type == 'note_on':
                notas.append(mensagem.note)
                velocidades.append(mensagem.velocity)

    return list(set(notas)), list(set(velocidades))


def salvar_arquivo(caminho_arquivo, arquivo):
    with open(caminho_arquivo, 'w') as ar:
        json.dump(arquivo, ar)


def abre_arquivos(caminho_arquivo):
    with open(caminho_arquivo, 'r') as ar:
        conteudo = ar.read()
        return json.loads(conteudo)
    

def midi2dict(caminho_arquivo):
    midi = mido.MidiFile(caminho_arquivo)
    head = []
    notas = []
    notas.append(midi.ticks_per_beat)
    #print(midi)
    # Iterar sobre as mensagens MIDI em cada faixa (track) do arquivo MIDI
    for faixa in midi.tracks:
        for mensagem in faixa:
            time = mensagem.time
            if mensagem.type == 'set_tempo':
                tempo = mensagem.tempo
                head.append(meta(tipo=mensagem.type, tempo=tempo, time=time))
            elif mensagem.type == 'time_signature':
                numerator = mensagem.numerator
                denominator = mensagem.denominator
                clocks_per_click = mensagem.clocks_per_click
                notated_32nd_notes_per_beat = mensagem.notated_32nd_notes_per_beat
                head.append(meta(tipo=mensagem.type, numerator=numerator, denominator=denominator, clocks_per_click=clocks_per_click, notated_32nd_notes_per_beat=notated_32nd_notes_per_beat, time=time))
            elif mensagem.type == 'track_name':
                name = mensagem.name
                notas.append(meta(tipo=mensagem.type, name=name, time=time))
            elif mensagem.type == 'note_on' or mensagem.type == 'note_off':
                # Extrair as informações relevantes da mensagem 'note_on'
                note = mensagem.note
                velocity = mensagem.velocity
                # Chamar a função set_nota para armazenar as informações da nota
                notas.append(meta(tipo=mensagem.type, time=time, note=note, velocity=velocity))
    notas.append({'tipo': 'end_of_track', 'time': 0})
    notas.insert(0, head)
    return notas


def dict2midi(notas):
    midi = mido.MidiFile()
    faixa = mido.MidiTrack()

    '''---------head------------'''
    for head in notas[0]:
        if head['tipo'] == 'set_tempo':
            faixa.append(mido.MetaMessage(head['tipo'], tempo=head['tempo'], time=head['time']))
        else:
            faixa.append(mido.MetaMessage(head['tipo'], numerator=head['numerator'], denominator=head['denominator'], clocks_per_click=head['clocks_per_click'], notated_32nd_notes_per_beat=head['notated_32nd_notes_per_beat'], time=head['time']))
        
    midi.tracks.append(faixa)

    '''---------body------------'''
    faixa = mido.MidiTrack()
    midi.ticks_per_beat = notas[1]
    faixa.append(mido.MetaMessage(notas[2]['tipo'], name=notas[2]['name'], time=notas[2]['time']))

    notas = notas[3:-1]
    flag = False
    count = 0
    # Iterar sobre as notas do dicionário
    for nota in notas:
        # Criar mensagens 'note_on' e 'note_off' a partir das informações da nota
        if 'note' not in nota:
            break
        mensagem = mido.Message(nota['tipo'], note=nota['note'], velocity=nota['velocity'], time=nota['time'])

        # Adicionar as mensagens à faixa
        faixa.append(mensagem)
        
    faixa.append(mido.Message(notas[-1]['tipo'], time=notas[-1]['time'])) 
    # Adicionar a faixa ao arquivo MIDI
    midi.tracks.append(faixa)
    return midi
    #midi.save(caminho_arquivo)


def midi2list(arquivo_midi,zero=False):
    midi = mido.MidiFile(arquivo_midi)
    #midi.save("asd5.mid")
    #print(midi)
    #print("-----------")
    head = []
    neck = {}
    notas = []
    channel = 0
    
    # Percorrer todas as mensagens do arquivo MIDI
    for faixa in midi.tracks:
        for msg in faixa:
            time = msg.time
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                head.append(meta(tipo=msg.type, tempo=tempo, time=time))
            elif msg.type == 'time_signature':
                numerator = msg.numerator
                denominator = msg.denominator
                clocks_per_click = msg.clocks_per_click
                notated_32nd_notes_per_beat = msg.notated_32nd_notes_per_beat
                head.append(meta(tipo=msg.type, numerator=numerator, denominator=denominator, clocks_per_click=clocks_per_click, notated_32nd_notes_per_beat=notated_32nd_notes_per_beat, time=time))
            elif msg.type == 'track_name':
                name = msg.name
                neck = meta(tipo=msg.type, name=name, time=time)
            else:
                break

    # Retornar as notas ativas no tempo especificado
    return ({'ticks_per_beat': midi.ticks_per_beat, 'channel': channel, 'head': head, 'neck': neck, 'body': Midi(arquivo_midi).get_dist()})


def list2midi(lista_midi: Midi):
    # Criar um novo objeto MidiFile
    midi = mido.MidiFile()
    # Criar uma nova faixa (track)
    faixa = mido.MidiTrack()
    
    midi.ticks_per_beat = lista_midi['ticks_per_beat']
    channel = lista_midi['channel']

    '''---------head------------'''
    for head in lista_midi['head']:
        if head['tipo'] == 'set_tempo':
            faixa.append(mido.MetaMessage(head['tipo'], tempo=head['tempo'], time=head['time']))
        else:
            faixa.append(mido.MetaMessage(head['tipo'], numerator=head['numerator'], denominator=head['denominator'], clocks_per_click=head['clocks_per_click'], notated_32nd_notes_per_beat=head['notated_32nd_notes_per_beat'], time=head['time']))
        
    midi.tracks.append(faixa)

    '''---------body------------'''
    faixa = mido.MidiTrack()
    faixa.append(mido.MetaMessage(lista_midi['neck']['tipo'], name=lista_midi['neck']['name'], time=lista_midi['neck']['time']))
    
    faixa = lista_midi["body"].get_midi(faixa)
    faixa.append(mido.MetaMessage('end_of_track', time=0))
    # Adicionar a faixa ao arquivo MIDI
    midi.tracks.append(faixa)
    
    return midi

def list2dict(lista_notas, n):
    # Defina as notas e velocidades possíveis
    notas_possiveis = list(range(110))  # Notas de 24 a 109 (intervalo dado)
    velocidades_possiveis = list(range(128))  # Velocidades de 1 a 127
    
    print("entrou no result, n =", n)
    result = {}
    for j, a in enumerate(lista_notas):
        for b in a:
            if f"n{b[0]}" in result:
                result[f"n{b[0]}"][j] = 1
                result[f"v{b[0]}"][j] = b[1] 
            else:
                result[f"n{b[0]}"] = [1 if x == j else 0 for x in range(n)]
                result[f"v{b[0]}"] = [b[1] if x == j else 0 for x in range(n)]
                
    print("saiu do result, tam:", len(result))


    # Percorra todas as mensagens do arquivo MIDI
    print("saiu do list2dict")
    return result

def mids2objs(dataset_path):
    songs = []
    for path, subdirs, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == "mid":
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs




if __name__ == '__main__':
    # Exemplo de uso:
    #entrada = 'midis/pop/5ive_-_Dont_Wanna_Let_You_Go/h1.mid'
    entrada = 'midis/pop/5ive_-_Dont_Wanna_Let_You_Go/h1.mid'
    l = Midi(caminho=entrada,nome="in", estilo="teste")
    ln = l.to_data("s")
    '''for i, x in enumerate(ln):
        print(f"{x}\t",ln[x], end="\t")
        if i%7==6:
            print()
    '''
    print("------------------")
    ln = l.from_data(ln)
    for x in ln:
        print(f"{x}\t",ln[x])

    #ln = list2midi(ln)
    #
    #print(ln)
    #ln.save("qwe.mid")
    #ln = dict2midi(ln)s
    #print(ln)
    #print("------------------")
    #print()
    #csv2midi(entrada, ln)

    
