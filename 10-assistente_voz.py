from playsound3 import playsound
import speech_recognition as sr
from pathlib import Path
from io import BytesIO
import os
import ssl
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
http_client = httpx.Client(verify=False)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY2"), http_client=http_client)

arquivo_audio = "hello.mp3"

recognizer = sr.Recognizer()

def grava_audio():
    """Captura áudio do microfone e retorna o áudio gravado"""
    with sr.Microphone(0) as source:
        print("Ouvindo...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    return audio

def transcricao_audio(audio):
    """Transcreve o áudio utilizando o modelo Whisper"""
    try:
        wav_data = BytesIO(audio.get_wav_data())
        wav_data.name = "audio.wav"
        transcricao = client.audio.transcriptions.create(
            model="whisper-1",
            file=wav_data
        )
        return transcricao.text
    except Exception as e:
        print(f"Erro na transcrição do audio {e}")
        return ""
    
def completa_texto(mensagens):
    """Completa o texto utilizando o modelo GPT-4o-mini"""
    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=mensagens,
            max_tokens=1000,
            temperature=0
        )
        return resposta.choices[0].message.content
    except Exception as e:
        print(f"Erro na completação do texto {e}")
        return "Desculpe, não consegui entender"

def cria_audio(texto):
    """Cria um arquivo de áudio a partir do texto usando a API do TTS"""
    if Path(arquivo_audio).exists():
        Path(arquivo_audio).unlink()
    try:
        resposta = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=texto
        )
        resposta.write_to_file(arquivo_audio)
    except Exception as e:
        print(f"Erro na criação de áudio {e}")

def roda_audio():
    """Reproduz o arquivo de áudio gerado"""
    if Path(arquivo_audio).exists():
        playsound(arquivo_audio)
    else:
        print("Erro: O arquivo de áudio não foi encontrado.")

def main():
    """Função principal para executar o assistente de voz"""
    mensagens = []
    while True:
        audio = grava_audio()
        transcricao = transcricao_audio(audio)
        if not transcricao:
            print("Não foi possível transcrever o áudio. Tente novamente")
            continue
        mensagens.append({"role":"user", "content":transcricao})
        #print(f"User: {mensagens[-1]["content"]}")
        resposta_texto = completa_texto(mensagens)
        mensagens.append({"role":"assistant", "content": resposta_texto})
        #print(f"Assistant: {mensagens[-1]["content"]}")
        cria_audio(resposta_texto)
        roda_audio()

if __name__ == "__main__":
    main()