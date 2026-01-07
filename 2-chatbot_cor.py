import os
import ssl
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Inicializando o colorama
init(autoreset=True)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar cliente com verificação SSL desabilitada
def criar_cliente_openai_ssl_desabilitado():
    # Criar um contexto SSL que não verifica certificados
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Criar cliente httpx com SSL desabilitado
    http_client = httpx.Client(verify=False)
    
    # Configurar cliente Groq
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  # Certifique-se de ter sua chave API configurada
        http_client=http_client
    )
    
    return client

client = criar_cliente_openai_ssl_desabilitado()

def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        temperature=0,
        max_tokens=1000,
        stream=True
    )
    print(f"{Fore.CYAN}Bot:", end="")
    texto_completo = ""
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            print(texto, end="")
            texto_completo += texto
    print()
    mensagens.append({"role":"assistant", "content": texto_completo})
    return mensagens

if __name__ == "__main__":
    print(f"{Fore.YELLOW}Bem Vindo ao Chatbot🤖{Style.RESET_ALL}")
    mensagens = []
    while True:
        in_user = input(f"{Fore.GREEN}User: {Style.RESET_ALL}")
        mensagens.append({"role":"user", "content": in_user})
        mensagens = geracao_texto(mensagens)