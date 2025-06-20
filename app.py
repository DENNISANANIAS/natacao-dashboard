import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import io

# Configuração da página
st.set_page_config(
    page_title="Classificação de Natação",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados
@st.cache_data
def load_data():
    # Carregar o arquivo CSV
    df = pd.read_csv('resultados.csv')
    
    # Renomear colunas
    df.columns = ['Código1', 'Código2', 'Nome', 'Categoria', 'Sexo', 
                  'Chegada', 'Partida', 'Tempo', 'Modalidade', 
                  'Equipe', 'Posição Geral', 'Posição Categoria']
    
    # Converter tempo para formato de tempo
    try:
        # Se o tempo estiver em formato de string
        if isinstance(df['Tempo'].iloc[0], str):
            df['Tempo'] = pd.to_datetime(df['Tempo'], format='%H:%M:%S').dt.time
        # Se já for datetime.time
        elif isinstance(df['Tempo'].iloc[0], time):
            pass  # Já está no formato correto
    except Exception as e:
        st.error(f"Erro ao converter tempo: {e}")
        # Tentar converter manualmente
        try:
            df['Tempo'] = df['Tempo'].apply(
                lambda x: time(int(x.split(':')[0]), int(x.split(':')[1]), int(x.split(':')[2])) 
                if isinstance(x, str) else x
            )
        except:
            st.error("Não foi possível converter a coluna de tempo")
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.stop()

# Função para medalhas
def get_medal(position):
    if position == 1:
        return "🥇"
    elif position == 2:
        return "🥈"
    elif position == 3:
        return "🥉"
    return ""

# Header
st.title("🏊 Dashboard de Classificação de Natação")
st.markdown("""
**Encontre sua posição na competição** - Filtre por sexo e modalidade para ver os resultados
""")

# Sidebar para filtros
with st.sidebar:
    st.header("🔍 Filtros")
    
    # Filtro de sexo
    sexo = st.selectbox(
        "Selecione o sexo:",
        options=df['Sexo'].unique(),
        index=0
    )
    
    # Filtro de modalidade baseado no sexo selecionado
    modalidades_disponiveis = df[df['Sexo'] == sexo]['Modalidade'].unique()
    modalidade = st.selectbox(
        "Selecione a modalidade:",
        options=modalidades_disponiveis,
        index=0
    )
    
    # Busca por nome
    nome_busca = st.text_input("Buscar por nome:")
    
    st.divider()
    st.markdown("### Sobre esta competição")
    st.markdown("""
    - **Provas:** Aquathlon, Natação 2.5Km, Natação 500m
    - **Categorias:** Por faixa etária
    - **Dados atualizados em:** 21/06/2025
    """)
    
    st.divider()
    st.markdown("Desenvolvido com ❤️ para competições aquáticas")

# Filtrar dados
dados_filtrados = df[(df['Sexo'] == sexo) & (df['Modalidade'] == modalidade)]

# Top 3 campeões
st.header(f"Top 3 - {modalidade} ({sexo})")
st.markdown("Os primeiros colocados nesta categoria:")

if not dados_filtrados.empty:
    top3 = dados_filtrados.nsmallest(3, 'Posição Geral')
    
    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            medalha = get_medal(i+1)
            st.subheader(f"{medalha} {i+1}º Lugar")
            st.markdown(f"**Nome:** {row['Nome']}")
            st.markdown(f"**Equipe:** {row['Equipe']}")
            st.markdown(f"**Categoria:** {row['Categoria']}")
            st.markdown(f"**Tempo:** {str(row['Tempo'])}")
            st.markdown(f"**Posição Geral:** #{row['Posição Geral']}")
else:
    st.warning("Nenhum resultado encontrado para os filtros selecionados")

# Classificação completa
st.header("📊 Classificação Completa")
st.markdown(f"Todos os participantes de {modalidade} ({sexo})")

if not dados_filtrados.empty:
    # Formatar dados para exibição
    dados_exibicao = dados_filtrados.sort_values('Posição Geral').copy()
    dados_exibicao['Medalha'] = dados_exibicao['Posição Geral'].apply(get_medal)
    dados_exibicao = dados_exibicao[['Medalha', 'Posição Geral', 'Nome', 'Categoria', 'Posição Categoria', 'Equipe', 'Tempo']]
    dados_exibicao = dados_exibicao.rename(columns={'Posição Categoria': 'Pos. Categoria'})
    
    # Destaque para busca por nome
    if nome_busca:
        mask = dados_exibicao['Nome'].str.contains(nome_busca, case=False, na=False)
        st.success(f"Mostrando resultados para: '{nome_busca}'")
        st.dataframe(
            dados_exibicao[mask],
            height=400,
            use_container_width=True
        )
    else:
        st.dataframe(dados_exibicao, height=400, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para exibição")

# Estatísticas
st.header("📈 Estatísticas da Prova")
if not dados_filtrados.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Participantes", len(dados_filtrados))
    col2.metric("Categorias Diferentes", dados_filtrados['Categoria'].nunique())
    
    # Calcular tempo médio
    try:
        # Converter tempo para segundos
        tempos = []
        for t in dados_filtrados['Tempo']:
            if isinstance(t, time):
                tempos.append(t.hour * 3600 + t.minute * 60 + t.second)
            elif isinstance(t, str) and ':' in t:
                parts = t.split(':')
                if len(parts) == 3:
                    tempos.append(int(parts[0])*3600 + int(parts[1])*60 + int(parts[2]))
        
        if tempos:
            tempo_medio_sec = np.mean(tempos)
            horas = int(tempo_medio_sec // 3600)
            minutos = int((tempo_medio_sec % 3600) // 60)
            segundos = int(tempo_medio_sec % 60)
            tempo_medio = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            col3.metric("Tempo Médio", tempo_medio)
        else:
            col3.metric("Tempo Médio", "N/A")
    except Exception as e:
        col3.metric("Tempo Médio", "Erro")
        st.error(f"Erro ao calcular tempo médio: {e}")
else:
    st.write("Nenhum dado para estatísticas.")

# Como usar
with st.expander("ℹ️ Como usar este dashboard"):
    st.markdown("""
    1. **Selecione o sexo** no menu lateral
    2. **Escolha a modalidade** que deseja visualizar
    3. **Veja os 3 primeiros colocados** no topo da página
    4. **Consulte a classificação completa** na tabela principal
    5. **Busque por seu nome** para encontrar sua posição
    
    **Dica:** A coluna "Pos. Categoria" mostra sua colocação dentro da sua faixa etária!
    """)

# Rodapé
st.divider()
st.markdown("""
**Competição de Natação 2025** | [Contato](mailto:info@natacao.com) | [Termos de Uso](#)
""")