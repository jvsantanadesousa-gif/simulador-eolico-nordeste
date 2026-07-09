import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.special import gamma
from scipy.stats import weibull_min

# Configuração da página
st.set_page_config(page_title="Dashboard de Potencial Eólico", layout="wide")

st.title("Análise e Estimação de Potencial Eólico - Tarefa 3.1")
st.markdown("Dashboard interativo para modelagem da velocidade do vento utilizando a Distribuição de Weibull.")

# --- BARRA LATERAL ---
st.sidebar.header("Parâmetros de Entrada")
k = st.sidebar.slider("Parâmetro de Forma (k)", 1.0, 4.0, 2.5, 0.1)
c = st.sidebar.slider("Parâmetro de Escala (c) [m/s]", 4.0, 12.0, 8.5, 0.1)
rho = st.sidebar.number_input("Densidade do ar (ρ) [kg/m³]", value=1.225)
raio_rotor = st.sidebar.number_input("Raio do rotor da turbina [m]", value=40.0)
area_varredura = np.pi * (raio_rotor ** 2)
cp = st.sidebar.slider("Coeficiente de Potência (Cp)", 0.1, 0.59, 0.40, 0.01)

# --- SEÇÃO 1: DADOS HISTÓRICOS ---
st.header("1. Análise Histórica (Dados INMET)")
uploaded_file = st.file_uploader("Carregue o CSV do INMET", type=["csv"])

if uploaded_file is not None:
    try:
        # skiprows=8 ignora o cabeçalho técnico do arquivo do INMET
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';', skiprows=8, engine='python')
        
        # Nome da coluna conforme seu arquivo CSV
        coluna_velocidade = "VENTO, VELOCIDADE HORARIA (m/s)"
        
        if coluna_velocidade in df.columns:
            # Tratamento: substitui vírgula por ponto decimal
            velocidades_brutas = df[coluna_velocidade].astype(str).str.replace(',', '.')
            velocidades_historicas = pd.to_numeric(velocidades_brutas, errors='coerce').dropna().values
            st.success("Dados carregados com sucesso!")
        else:
            st.error(f"Coluna não encontrada. As colunas disponíveis são: {df.columns.tolist()}")
            velocidades_historicas = np.random.weibull(k, 1000) * c
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        velocidades_historicas = np.random.weibull(k, 1000) * c
else:
    st.info("Utilizando dados sintéticos. Carregue um CSV do INMET para dados reais.")
    velocidades_historicas = weibull_min.rvs(k, scale=c, size=5000)

# Gráfico
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(x=velocidades_historicas, histnorm='probability density', name='Dados Históricos'))
st.plotly_chart(fig_hist, use_container_width=True)

# --- SEÇÃO 2: MODELAGEM ---
st.header("2. Estimação de Potencial Eólico")
v_array = np.linspace(0, 25, 500)
pdf_weibull = (k / c) * ((v_array / c) ** (k - 1)) * np.exp(-((v_array / c) ** k))
v_media = c * gamma(1 + (1 / k))

col1, col2 = st.columns(2)
with col1:
    fig_pdf = go.Figure()
    fig_pdf.add_trace(go.Scatter(x=v_array, y=pdf_weibull, name=f'Weibull (k={k}, c={c})'))
    st.plotly_chart(fig_pdf, use_container_width=True)

with col2:
    densidade_potencia = 0.5 * rho * (c ** 3) * gamma(1 + (3 / k))
    potencia_total = densidade_potencia * area_varredura
    st.metric("Velocidade Média", f"{v_media:.2f} m/s")
    st.metric("Potência Disponível", f"{potencia_total / 1000:.2f} kW")
    st.metric("Potência Gerada (Turbina)", f"{(potencia_total * cp) / 1000:.2f} kW")
