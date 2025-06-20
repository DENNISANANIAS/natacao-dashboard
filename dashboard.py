import streamlit as st
import pandas as pd

# Ajuste para leitura correta de encoding
@st.cache_data
def load_data():
    # Troque pelo caminho correto do seu CSV se necessário
    df = pd.read_csv("resultados.csv", sep=";", encoding="latin1")
    # Remove colunas A e B (C�digo1 e C�digo2)
    df = df.iloc[:, 2:]
    # Corrige possíveis nomes de colunas com erro de encoding
    df.columns = [col.encode('latin1').decode('utf-8') for col in df.columns]
    return df

st.title("Classificação da Competição de Natação")

df = load_data()

# Filtros
sexo_options = df["Sexo"].unique()
modalidade_options = df["Modalidade"].unique()

sexo = st.selectbox("Selecione o Sexo", options=sexo_options)
modalidade = st.selectbox("Selecione a Modalidade", options=modalidade_options)

df_filtered = df[(df["Sexo"] == sexo) & (df["Modalidade"] == modalidade)]

# Exibe os campeões gerais por categoria (top 3 por categoria)
st.header(f"Top 3 por Categoria - {modalidade} - {sexo}")

categorias = df_filtered["Categoria"].unique()
for categoria in sorted(categorias):
    st.subheader(f"Categoria: {categoria}")
    cat_df = df_filtered[df_filtered["Categoria"] == categoria].sort_values("Posição Geral", key=pd.to_numeric)
    st.table(cat_df.head(3)[["Nome", "Equipe", "Tempo", "Posição Geral"]])

# Exibe classificação geral (todos atletas do filtro, ordenado por posição geral)
st.header("Classificação Geral")
df_filtered_ordenado = df_filtered.sort_values("Posição Geral", key=pd.to_numeric)
st.dataframe(df_filtered_ordenado.reset_index(drop=True).drop(columns=["Posição Categoria"]), use_container_width=True)