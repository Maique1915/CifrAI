import mido, math, os, json
from music21 import key, note, midi, pitch, stream, interval, converter
import pandas as pd

class Midi:
    __tempo = 0
    __nome = ""
    __estilo = ""
    __caminho = ""
    __notas = []

    def __init__(self, caminho="", nome="", estilo=""):
        self.__musica = {}
        self.nome = nome
        self.estilo = estilo
        self.caminho = caminho

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome):
        self.__nome = nome
        
    @property
    def estilo(self):
        return self.__estilo

    @estilo.setter
    def estilo(self, estilo):
        self.__estilo = estilo
            
    @property
    def caminho(self):
        return self.__caminho

    @caminho.setter
    def caminho(self, caminho):
        self.__caminho = caminho
        if caminho != "":
            self.__get_notes()


    def add(self, note, velocity=0, on=False, time=0):
        if f'{time+self.__tempo}' in self.__musica:
                self.__musica[f'{time+self.__tempo}'].append((note, velocity, on))
        else:
            self.__musica[f'{time+self.__tempo}'] = [(note, velocity, on)]
        self.__tempo += time
    

    def get_dist(self):
        return self.__musica
    

    def get_time(self):
        return self.__tempo
    
    
    def num2nota(numero):
        nota = note.Note(numero)
        return nota.nameWithOctave
    
    
    def nota2num(nota):
        nota = note.Note(step=nota[:-1], octave=int(nota[-1]))
        return nota.pitch.midi


    def get_min_time(self):
        min = 0
        ant = '0'
        for x in self.__musica:
            if min > math.abs(int(x) - ant):
                min = math.abs(int(x) - ant)
            ant = int(x)
        return min
    
    def int2hex(i):
        return hex(i)[2:].zfill(4)
    
    def hex2int(i):
        return int(i, 16)
    
    def mid2obj(caminho_arquivo_midi):
        return  converter.parse(caminho_arquivo_midi)

    def obj2mid(partitura):
        return midi.translate.music21ObjectToMidiFile(partitura)

    
    def salvar_arquivo(caminho_arquivo, arquivo):
        with open(caminho_arquivo, 'w') as ar:
            json.dump(arquivo, ar, indent=2)


    def abrir_arquivos(caminho_arquivo):
        with open(caminho_arquivo, 'r') as ar:
            conteudo = ar.read()
            return json.loads(conteudo)
    
    def transpose(caminho):
        song = Midi.mid2obj(caminho)
        parts = song.getElementsByClass(stream.Part)
        measures_part0 = parts[0].getElementsByClass(stream.Measure)
        key = measures_part0[0][4]

        if not isinstance(key, key.Key):
            key = song.analyze("key")

        if key.mode == "major":
            print("original:",key.tonic,"| transposta:",  pitch.Pitch("C"))
            interval = interval.Interval(key.tonic, pitch.Pitch("C"))
        elif key.mode == "minor":
            print("original:",key.tonic,"| transposta:",  pitch.Pitch("A"))
            interval = interval.Interval(key.tonic, pitch.Pitch("A"))

        tranposed_song = song.transpose(interval)
        
        return tranposed_song

    
    def get_midi(self, faixa):
        ant = 0
        for x in self.__musica:
            for i, nota in enumerate(self.__musica[x]):
                note, velocidade, on = nota
                tipo = 'note_on' if on else 'note_off'

                if i == 0:
                    faixa.append(mido.Message(tipo, note=note, velocity=velocidade, time=int(x)-ant))
                else:
                    faixa.append(mido.Message(tipo, note=note, velocity=velocidade, time=0))
            ant = int(x)
        return faixa


    def __get_notes(self):
        if self.__caminho != "":
            midi = mido.MidiFile(self.__caminho)

            for i, faixa in enumerate(midi.tracks):
                for msg in faixa:
                    time = msg.time
                    if 'note_' in msg.type:
                        on = True if msg.type == 'note_on' else False
                        self.add(note=msg.note, velocity=msg.velocity, on=on, time= time)
                        if msg.note not in self.__notas:
                            self.__notas.append(msg.note)

            self.__notas = sorted(self.__notas)

            return self.__musica
        
        print("sem caminho especificado")
        return {}

    
    def __add(self, dados):
        if self.__nome != "":
            dados["musica"] = self.__nome
        if self.__estilo != "":
            dados["estilo"] = self.__estilo

        return dados

        
    def to_data(self,pre=""):
        max = 0x3333
        res = []
        lbl = []
        menor = 6
        resultado = {}
        init = [[0]]

        self.__add(resultado)

        for x in range(self.__tempo):
            if len(res) > max:
                break

            aux = init
            
            if str(x) in self.__musica:
                b = False
                for item in self.__musica[str(x)]:
                    r = 1 if item[-1] else 0
                    b = True
                    aux = [[item[0]]]
                    if r == 0 and x%menor == 0:
                        res[-1] = [0]

                if not b and len(res)> 0 and x%menor == 0:
                    aux = [[0]]
                    res[-1] = [0]
                        
            init = aux
            if x%menor == 0:
                lbl = lbl + [ f"{pre}{Midi.int2hex(x)}"]
                res = res + aux

        for i, x in enumerate(lbl):
            resultado[x] = res[i]
        
        return resultado

    def from_data(self, data):
        ant = (0,0)
        res = {}
        for chave, valores in data.items():
            if isinstance(valores, list):
                tempo = str(Midi.hex2int(chave[-4:]))
                on = valores[0] > 0
                nota = valores[0] if on else ant[0]
                vel = 127 if on else 0
                if ant != (nota, vel):
                    if tempo not in res:
                        if on:
                            res[tempo] = [(nota, vel, on)]
                        else:
                            res[Midi.int2hex(Midi.hex2int(tempo)+6)] = [(nota, vel, on)]
                    else:
                        if on:
                            res[tempo].append((nota, vel, on))
                        else:
                            res[Midi.int2hex(Midi.hex2int(tempo)+6)] = [(nota, vel, on)]
                ant = (nota, vel)

        return res
    

    def salva_csv(self, nome_arquivo, nome, pre="", columns=None, axis=0):
        dados = self.to_data(pre)
        if os.path.exists(nome_arquivo):
            df = pd.read_csv(nome_arquivo)
        else:
            df = pd.DataFrame(columns=columns) if columns else pd.DataFrame()
        
        caminho = os.path.join("json","musicas."+nome+".json")
        musica = dados["musica"]
        dados = pd.DataFrame(dados)
        if "musica" in df.columns and musica not in df['musica'].values or len(df) == 0:
            
            if(axis == 1):
                df = pd.concat([df, dados], ignore_index=False, axis=1)
            else:
                df = pd.concat([df, dados], ignore_index=False)
            print("Salvando:", musica)
            df.to_csv(nome_arquivo, index=False)
            print("Salvo:", musica)
            conteudo = Midi.abrir_arquivos(caminho)
            conteudo = conteudo + [musica]
            Midi.salvar_arquivo(caminho, conteudo)
        elif "musica" in df.columns and nome in df['musica'].values:
            conteudo = Midi.abrir_arquivos(caminho)
            conteudo = conteudo + [nome]
            if nome not in json.loads(conteudo):
                Midi.salvar_arquivo(caminho, conteudo)

        return dados
        