import streamlit as st
import pandas as pd

from utils_openai import retorna_resposta_modelo
from utils_files import *

# Configurações fixas
API_KEY = "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"  # Substitua pela sua chave de API
MODELO = 'gpt-4'

# INICIALIZAÇÃO ==================================================
def inicializacao():
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''

# TABS ==================================================
def tab_conversas():
    st.sidebar.button('➕ Nova conversa',
                      on_click=seleciona_conversa,
                      args=('', ),
                      use_container_width=True)
    st.sidebar.markdown('')
    conversas = listar_conversas()
    for nome_arquivo in conversas:
        nome_mensagem = desconverte_nome_mensagem(nome_arquivo).capitalize()
        if len(nome_mensagem) == 30:
            nome_mensagem += '...'
        st.sidebar.button(nome_mensagem,
                          on_click=seleciona_conversa,
                          args=(nome_arquivo, ),
                          disabled=nome_arquivo == st.session_state['conversa_atual'],
                          use_container_width=True)

def seleciona_conversa(nome_arquivo):
    if nome_arquivo == '':
        st.session_state['mensagens'] = []
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo)
        st.session_state['mensagens'] = mensagem
    st.session_state['conversa_atual'] = nome_arquivo

# PÁGINA PRINCIPAL ==================================================
def pagina_principal():
    mensagens = ler_mensagens(st.session_state['mensagens'])

    st.header('🤖 Ambev Chatbot', divider=True)

    for mensagem in mensagens:
        chat = st.chat_message(mensagem['role'])
        chat.markdown(mensagem['content'])
    
    prompt = st.chat_input('Fale com o chat')
    if prompt:
        nova_mensagem = {'role': 'user', 'content': prompt}
        chat = st.chat_message(nova_mensagem['role'])
        chat.markdown(nova_mensagem['content'])
        mensagens.append(nova_mensagem)

        chat = st.chat_message('assistant')
        placeholder = chat.empty()
        placeholder.markdown("▌")
        resposta_completa = ''
        respostas = retorna_resposta_modelo(mensagens, API_KEY, modelo=MODELO, stream=True)
        for resposta in respostas:
            resposta_completa += resposta.choices[0].delta.get('content', '')
            placeholder.markdown(resposta_completa + "▌")
        placeholder.markdown(resposta_completa)
        nova_mensagem = {'role': 'assistant', 'content': resposta_completa}
        mensagens.append(nova_mensagem)

        st.session_state['mensagens'] = mensagens
        salvar_mensagens(mensagens)
    
    # Seção de upload de arquivos sempre na parte inferior
    st.subheader("Envio de Arquivos")
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
    if st.button('Processar Arquivo Excel'):
        if uploaded_file is not None:
            # Lê o conteúdo do arquivo
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(file_details)
            
            try:
                # Converte o arquivo Excel em um DataFrame
                df = pd.read_excel(uploaded_file)
                st.write(df)
                
                # Converte o DataFrame em texto para enviar para a API
                df_text = df.to_string()
                st.session_state['mensagens'].append({'role': 'user', 'content': df_text})
                nova_mensagem = {'role': 'user', 'content': df_text}
                chat = st.chat_message(nova_mensagem['role'])
                chat.markdown(nova_mensagem['content'])
                mensagens.append(nova_mensagem)
                
                # Envia a mensagem para a API
                chat = st.chat_message('assistant')
                placeholder = chat.empty()
                placeholder.markdown("▌")
                resposta_completa = ''
                respostas = retorna_resposta_modelo(mensagens, API_KEY, modelo=MODELO, stream=True)
                for resposta in respostas:
                    resposta_completa += resposta.choices[0].delta.get('content', '')
                    placeholder.markdown(resposta_completa + "▌")
                placeholder.markdown(resposta_completa)
                nova_mensagem = {'role': 'assistant', 'content': resposta_completa}
                mensagens.append(nova_mensagem)
                st.session_state['mensagens'] = mensagens
                salvar_mensagens(mensagens)
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

# MAIN ==================================================
def main():
    inicializacao()
    pagina_principal()
    tab_conversas()

if __name__ == '__main__':
    main()
