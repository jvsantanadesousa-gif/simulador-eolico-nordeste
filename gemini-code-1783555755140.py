import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.special import gamma
from scipy.stats import weibull_min

st.set_page_config(page_title="Dashboard de Potencial Eólico", layout="wide")
st.title("Simulador de Potencial Eólico - Tarefa 3.1")

# --- BARRA LATERAL COM CAMPOS DE DIGITAÇÃO ---
st.sidebar.header("Parâmetros de Entrada (Manuais)")

# Agora usamos number_input em vez de slider para permitir digitação livre
k = st.sidebar.number_input("Parâmetro de Forma (k)", min_value=0.1, value=2.5, step=0.1, format="%.2f")
c = st.sidebar.number_input("Parâmetro de Escala (c) [m/s]", min_value=0.1, value=8.5, step=0.1, format="%.2f")
rho = st.sidebar.number_input("Densidade do ar (ρ) [kg/m³]", value=1.225, format="%.3f")
raio_rotor = st.sidebar.number_input("Raio do rotor da turbina [m]", value=40.0, step=0.1)
cp = st.sidebar.number_input("Coeficiente de Potência (Cp)", min_value=0.01, max_value=0.59, value=0.40, step=0.01)

area_varredura = np.pi * (raio_rotor ** 2)

# --- CARGA E TRATAMENTO ---
uploaded_file = st.file_uploader("Suba o CSV do INMET", type=["csv"])
dados_finais = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';', skiprows=8, engine='python')
        col_nome = "VENTO, VELOCIDADE HORARIA (m/s)"
        if col_nome in df.columns:
            dados = pd.to_numeric(df[col_nome].astype(str).str.replace(',', '.'), errors='coerce').dropna()
            if len(dados) > 0:
                dados_finais = dados.values
                st.success(f"Dados carregados com sucesso ({len(dados_finais)} registros).")
    except Exception as e:
        st.error(f"Erro na leitura: {e}")

if dados_finais is None:
    st.warning("Usando dados sintéticos (Simulação).")
    dados_finais = weibull_min.rvs(k, scale=c, size=1000)

# --- GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=dados_finais, histnorm='probability density', name='Dados'))
    fig.update_layout(title="Distribuição das Velocidades", xaxis_title="Velocidade (m/s)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    v_teorico = np.linspace(0, 25, 200)
    pdf = (k / c) * (v_teorico / c)**(k - 1) * np.exp(-(v_teorico / c)**k)
    fig_weibull = go.Figure()
    fig_weibull.add_trace(go.Scatter(x=v_teorico, y=pdf, name='Weibull', line=dict(color='red', width=3)))
    fig_weibull.update_layout(title="Função Densidade de Probabilidade (Teórica)", xaxis_title="Velocidade (m/s)")
    st.plotly_chart(fig_weibull, use_container_width=True)

# --- RESULTADOS ---
st.header("Cálculo de Potência")
potencia_media = 0.5 * rho * area_varredura * (c**3) * gamma(1 + 3/k)
col_a, col_b = st.columns(2)
col_a.metric("Potência Disponível (Vento)", f"{potencia_media/1000:.2f} kW")
col_b.metric("Potência Gerada (Turbina)", f"{(potencia_media * cp)/1000:.2f} kW")
