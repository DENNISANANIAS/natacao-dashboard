import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import io
import chardet
import base64

# Configuração da página
st.set_page_config(
    page_title="Classificação de Natação",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para detectar encoding
def detect_encoding(file_path):
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    except Exception as e:
        st.error(f"Erro ao detectar encoding: {str(e)}")
        return 'utf-8'

# Função para converter tempo
def convert_time(t):
    if isinstance(t, time):
        return t
    elif isinstance(t, str):
        try:
            # Tentar converter HH:MM:SS
            parts = t.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(float(parts[2]))
                return time(hours, minutes, seconds)
            # Tentar converter HH:MM:SS.micros
            elif '.' in parts[2]:
                seconds, micros = parts[2].split('.')
                return time(int(parts[0]), int(parts[1]), int(seconds), int(micros))
        except:
            return None
    return None

# Carregar dados
@st.cache_data
def load_data():
    try:
        # Tenta carregar do arquivo local
        encoding = detect_encoding('resultados.csv')
        df = pd.read_csv('resultados.csv', encoding=encoding)
        st.sidebar.success("Dados carregados do arquivo local")
        return df
    except Exception as e:
        st.sidebar.warning(f"Não foi possível carregar dados locais: {str(e)}")
        return pd.DataFrame()

# Inicializar dados
df = load_data()

# Se não carregou dados, permite upload
if df.empty:
    with st.sidebar:
        st.header("📤 Upload de Arquivo")
        uploaded_file = st.file_uploader("Envie o arquivo resultados.csv", type="csv")
        
        if uploaded_file is not None:
            try:
                # Tenta detectar encoding do arquivo enviado
                raw_data = uploaded_file.getvalue()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                # Ler o arquivo
                df = pd.read_csv(io.BytesIO(raw_data), encoding=encoding)
                st.sidebar.success("Arquivo carregado com sucesso!")
            except Exception as e:
                st.sidebar.error(f"Erro ao ler arquivo: {e}")
                st.stop()
        else:
            st.warning("Por favor, envie o arquivo de resultados")
            st.stop()

# Renomear colunas conforme estrutura real do arquivo
colunas_esperadas = [
    'Código1', 'Código2', 'Nome', 'Categoria', 'Sexo', 
    'Chegada', 'Partida', 'Tempo', 'Modalidade', 
    'Equipe', 'Posição Geral', 'Posição Categoria'
]

# Verificar número de colunas
if len(df.columns) < len(colunas_esperadas):
    st.error(f"O arquivo tem apenas {len(df.columns)} colunas, mas esperamos {len(colunas_esperadas)}")
    st.stop()

# Renomear apenas as colunas existentes
novos_nomes = {}
for i, nome_esperado in enumerate(colunas_esperadas):
    if i < len(df.columns):
        novos_nomes[df.columns[i]] = nome_esperado

df = df.rename(columns=novos_nomes)

# Converter tempo
if 'Tempo' in df.columns:
    df['Tempo'] = df['Tempo'].apply(convert_time)
else:
    st.error("Coluna 'Tempo' não encontrada no arquivo")
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
    if 'Sexo' in df.columns:
        sexo = st.selectbox(
            "Selecione o sexo:",
            options=df['Sexo'].unique(),
            index=0
        )
    else:
        st.error("Coluna 'Sexo' não encontrada")
        st.stop()
    
    # Filtro de modalidade baseado no sexo selecionado
    if 'Modalidade' in df.columns:
        modalidades_disponiveis = df[df['Sexo'] == sexo]['Modalidade'].unique()
        modalidade = st.selectbox(
            "Selecione a modalidade:",
            options=modalidades_disponiveis,
            index=0
        )
    else:
        st.error("Coluna 'Modalidade' não encontrada")
        st.stop()
    
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
dados_filtrados = df[(df['Sexo'] == sexo) & (df['Modalidade'] == modalidade)].copy()

# Top 3 campeões
st.header(f"Top 3 - {modalidade} ({sexo})")
st.markdown("Os primeiros colocados nesta categoria:")

if not dados_filtrados.empty:
    # Verificar se temos coluna de posição geral
    if 'Posição Geral' not in dados_filtrados.columns:
        st.error("Coluna 'Posição Geral' não encontrada")
        st.stop()
    
    # Ordenar por posição geral
    dados_filtrados = dados_filtrados.sort_values('Posição Geral')
    top3 = dados_filtrados.head(3)
    
    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            medalha = get_medal(i+1)
            st.subheader(f"{medalha} {i+1}º Lugar")
            st.markdown(f"**Nome:** {row['Nome']}")
            
            if 'Equipe' in row:
                st.markdown(f"**Equipe:** {row['Equipe']}")
                
            if 'Categoria' in row:
                st.markdown(f"**Categoria:** {row['Categoria']}")
                
            if 'Tempo' in row:
                st.markdown(f"**Tempo:** {str(row['Tempo'])}")
                
            st.markdown(f"**Posição Geral:** #{int(row['Posição Geral'])}")
else:
    st.warning("Nenhum resultado encontrado para os filtros selecionados")

# Classificação completa
st.header("📊 Classificação Completa")
st.markdown(f"Todos os participantes de {modalidade} ({sexo})")

if not dados_filtrados.empty:
    # Criar DataFrame para exibição
    colunas_exibicao = []
    if 'Posição Geral' in dados_filtrados.columns:
        colunas_exibicao.append('Posição Geral')
    if 'Nome' in dados_filtrados.columns:
        colunas_exibicao.append('Nome')
    if 'Categoria' in dados_filtrados.columns:
        colunas_exibicao.append('Categoria')
    if 'Posição Categoria' in dados_filtrados.columns:
        colunas_exibicao.append('Posição Categoria')
    if 'Equipe' in dados_filtrados.columns:
        colunas_exibicao.append('Equipe')
    if 'Tempo' in dados_filtrados.columns:
        colunas_exibicao.append('Tempo')
    
    dados_exibicao = dados_filtrados[colunas_exibicao].copy()
    
    # Adicionar medalhas
    if 'Posição Geral' in dados_exibicao.columns:
        dados_exibicao['Medalha'] = dados_exibicao['Posição Geral'].apply(
            lambda x: get_medal(x) if x <= 3 else ""
        )
        colunas_exibicao.insert(0, 'Medalha')
    
    # Renomear colunas
    dados_exibicao = dados_exibicao.rename(columns={
        'Posição Geral': 'Pos. Geral',
        'Posição Categoria': 'Pos. Categoria'
    })
    
    # Ordenar
    if 'Pos. Geral' in dados_exibicao.columns:
        dados_exibicao = dados_exibicao.sort_values('Pos. Geral')
    
    # Destaque para busca por nome
    if nome_busca and 'Nome' in dados_exibicao.columns:
        mask = dados_exibicao['Nome'].str.contains(nome_busca, case=False, na=False)
        st.success(f"Mostrando resultados para: '{nome_busca}'")
        
        if any(mask):
            st.dataframe(
                dados_exibicao[mask],
                height=400,
                use_container_width=True
            )
        else:
            st.warning("Nenhum atleta encontrado com esse nome")
            st.dataframe(dados_exibicao, height=400, use_container_width=True)
    else:
        st.dataframe(dados_exibicao, height=400, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para exibição")

# Estatísticas
st.header("📈 Estatísticas da Prova")
if not dados_filtrados.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Participantes", len(dados_filtrados))
    
    if 'Categoria' in dados_filtrados.columns:
        col2.metric("Categorias Diferentes", dados_filtrados['Categoria'].nunique())
    else:
        col2.metric("Categorias Diferentes", "N/A")
    
    # Calcular tempo médio
    if 'Tempo' in dados_filtrados.columns:
        try:
            # Converter tempo para segundos
            tempos = []
            for t in dados_filtrados['Tempo']:
                if isinstance(t, time):
                    tempos.append(t.hour * 3600 + t.minute * 60 + t.second)
            
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
    else:
        col3.metric("Tempo Médio", "N/A")
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
    
    **Dicas:**
    - A coluna "Pos. Categoria" mostra sua colocação dentro da sua faixa etária
    - As colunas "Pos. Geral" mostra sua colocação geral na prova
    - Use a busca por nome para encontrar rapidamente seu resultado
    """)

# Rodapé
st.divider()
st.markdown("""
**Competição de Natação 2025** | [Contato](mailto:info@natacao.com) | [Termos de Uso](#)
""")