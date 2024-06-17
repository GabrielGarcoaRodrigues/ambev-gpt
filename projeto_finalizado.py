import streamlit as st
import pandas as pd
import openpyxl
import openai
import os


from utils_openai import retorna_resposta_modelo
from utils_files import *

# st.write("API_KEY:", st.secrets["API_KEY"])

# INICIALIZAÇÃO ==================================================
def inicializacao():
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''
    if not 'modelo' in st.session_state:
        st.session_state.modelo = 'gpt-4o'
    if not 'api_key' in st.session_state:
        st.session_state.api_key = st.secrets["API_KEY"]


    chave = st.secrets["API_KEY"]
    # st.session_state['api_key'] = API_KEY
    if chave != st.session_state['api_key']:
         st.session_state['api_key'] = chave
         salva_chave(chave)
         st.sidebar.success('Chave salva com sucesso')
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

# def tab_configuracoes(tab):
#     st.session_state['modelo'] = 'gpt-4'
#     # tab.write('Modelo selecionado: GPT-4')	
#     tab.selectbox('Selecione o modelo', ['gpt-4'])

#     # chave = tab.text_input('Adicione sua api key', value=st.session_state['api_key'], type="password")
#     chave = st.secrets["API_KEY"]
#     # st.session_state['api_key'] = API_KEY
#     if chave != st.session_state['api_key']:
#          st.session_state['api_key'] = chave
#          salva_chave(chave)
#          tab.success('Chave salva com sucesso')

# PÁGINA PRINCIPAL ==================================================
def pagina_principal():
    st.set_page_config(page_title="Orbit AI", layout='centered')

    mensagens = ler_mensagens(st.session_state['mensagens'])

    st.header('🍺 Ambev Chatbot', divider=True)

    for mensagem in mensagens:
        chat = st.chat_message(mensagem['role'])
        chat.markdown(mensagem['content'])
    
    prompt = st.chat_input('Fale com o chat')
    if prompt:
        if st.session_state['api_key'] == '':
            st.error('Adicione uma chave de API na aba de configurações')
        else:
            nova_mensagem = {'role': 'user', 'content': prompt}
            chat = st.chat_message(nova_mensagem['role'])
            chat.markdown(nova_mensagem['content'])
            mensagens.append(nova_mensagem)

            chat = st.chat_message('assistant')
            placeholder = chat.empty()
            placeholder.markdown("▌")
            resposta_completa = ''
            try:
                respostas = retorna_resposta_modelo(mensagens, st.session_state['api_key'], modelo=st.session_state['modelo'], stream=True)
                for resposta in respostas:
                    resposta_completa += resposta.choices[0].delta.get('content', '')
                    placeholder.markdown(resposta_completa + "▌")
                placeholder.markdown(resposta_completa)
                nova_mensagem = {'role': 'assistant', 'content': resposta_completa}
                mensagens.append(nova_mensagem)

                st.session_state['mensagens'] = mensagens
                salvar_mensagens(mensagens)
            except Exception as e:
                st.error(f"Erro ao obter resposta do modelo: {e}")
    
    # Seção de upload de arquivos sempre na parte inferior
    # uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
    # if st.button('Processar Arquivo Excel'):
    #     if uploaded_file is not None:
    #         try:
    #             df = pd.read_excel(uploaded_file)
    #             st.write(df)
                
    #             df_text = df.to_string()
    #             st.session_state['mensagens'].append({'role': 'user', 'content': df_text})
    #             nova_mensagem = {'role': 'user', 'content': df_text}
    #             chat = st.chat_message(nova_mensagem['role'])
    #             chat.markdown(nova_mensagem['content'])
    #             mensagens.append(nova_mensagem)
                
    #             chat = st.chat_message('assistant')
    #             placeholder = chat.empty()
    #             placeholder.markdown("▌")
    #             resposta_completa = ''
    #             respostas = retorna_resposta_modelo(mensagens, st.session_state['api_key'], modelo=st.session_state['modelo'], stream=True)
    #             for resposta in respostas:
    #                 resposta_completa += resposta.choices[0].delta.get('content', '')
    #                 placeholder.markdown(resposta_completa + "▌")
    #             placeholder.markdown(resposta_completa)
    #             nova_mensagem = {'role': 'assistant', 'content': resposta_completa}
    #             mensagens.append(nova_mensagem)
    #             st.session_state['mensagens'] = mensagens
    #             salvar_mensagens(mensagens)
    #         except Exception as e:
    #             st.error(f"Erro ao processar o arquivo: {e}")
 

# MAIN ==================================================
def main():
    inicializacao()
    pagina_principal()
    # tab1 = st.sidebar.tabs(['Conversas'])
    # tab_conversas(tab1)
    # tab_configuracoes(tab2)
    tab_conversas()
    
if __name__ == '__main__':
    main()
