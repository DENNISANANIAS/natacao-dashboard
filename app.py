import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Classificação de Natação",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_excel('resultados.xlsx')
    df.columns = ['Código1', 'Código2', 'Nome', 'Categoria', 'Sexo', 
                  'Chegada', 'Partida', 'Tempo', 'Modalidade', 
                  'Equipe', 'Posição Geral', 'Posição Categoria']
    df['Tempo'] = pd.to_datetime(df['Tempo'], format='%H:%M:%S').dt.time
    return df

df = load_data()

def get_medal(position):
    if position == 1: return "🥇"
    elif position == 2: return "🥈"
    elif position == 3: return "🥉"
    return ""

st.title("🏊 Dashboard de Classificação de Natação")
st.markdown("**Encontre sua posição na competição**")

with st.sidebar:
    st.header("🔍 Filtros")
    sexo = st.selectbox("Sexo", df['Sexo'].unique())
    modalidades = df[df['Sexo'] == sexo]['Modalidade'].unique()
    modalidade = st.selectbox("Modalidade", modalidades)
    nome_busca = st.text_input("Buscar por nome:")
    st.divider()
    st.markdown("Desenvolvido para competições aquáticas")

dados = df[(df['Sexo'] == sexo) & (df['Modalidade'] == modalidade)]

st.header(f"Top 3 - {modalidade} ({sexo})")
if not dados.empty:
    top3 = dados.nsmallest(3, 'Posição Geral')
    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            medalha = get_medal(i+1)
            st.subheader(f"{medalha} {i+1}º Lugar")
            st.write(f"**Nome:** {row['Nome']}")
            st.write(f"**Equipe:** {row['Equipe']}")
            st.write(f"**Tempo:** {str(row['Tempo'])}")

st.header("📊 Classificação Completa")
if not dados.empty:
    dados_exibicao = dados.sort_values('Posição Geral')[['Posição Geral', 'Nome', 'Categoria', 'Equipe', 'Tempo']]
    dados_exibicao['Medalha'] = dados_exibicao['Posição Geral'].apply(get_medal)
    dados_exibicao = dados_exibicao[['Medalha', 'Posição Geral', 'Nome', 'Categoria', 'Equipe', 'Tempo']]
    
    if nome_busca:
        mask = dados_exibicao['Nome'].str.contains(nome_busca, case=False)
        st.success(f"Resultados para: '{nome_busca}'")
        st.dataframe(dados_exibicao[mask], height=300)
    else:
        st.dataframe(dados_exibicao, height=300)
else:
    st.warning("Nenhum dado encontrado")

st.divider()
st.markdown("**Competição de Natação 2025** | [Contato](mailto:exemplo@email.com)")