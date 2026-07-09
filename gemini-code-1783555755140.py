import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.special import gamma
from scipy.stats import weibull_min

st.set_page_config(layout="wide")
st.title("Simulador de Potencial Eólico - Tarefa 3.1")

# --- CARGA E TRATAMENTO ---
uploaded_file = st.file_uploader("Suba o CSV do INMET", type=["csv"])
dados_processados = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='latin1', sep=';', skiprows=8, engine='python')
    col_nome = "VENTO, VELOCIDADE HORARIA (m/s)"
    
    if col_nome in df.columns:
        # Converte para numérico e remove vazios
        dados = pd.to_numeric(df[col_nome].astype(str).str.replace(',', '.'), errors='coerce').dropna()
        if len(dados) > 0:
            dados_processados = dados.values
            st.success(f"Dados carregados: {len(dados_processados)} medições válidas.")
        else:
            st.error("ERRO: A coluna de velocidade está VAZIA neste arquivo do INMET.")
    else:
        st.error("Coluna 'VENTO, VELOCIDADE HORARIA (m/s)' não encontrada.")

# --- DADOS PARA O DASHBOARD ---
if dados_processados is not None:
    dados_finais = dados_processados
else:
    st.warning("Usando dados sintéticos (Simulação).")
    dados_finais = weibull_min.rvs(2.5, scale=8.5, size=1000)

# --- CÁLCULOS E GRÁFICOS ---
k = 2.5 # Ajuste conforme necessário
c = 8.5 # Ajuste conforme necessário
rho = 1.225
area = 5000 

fig = go.Figure()
fig.add_trace(go.Histogram(x=dados_finais, histnorm='probability density', name='Dados'))
st.plotly_chart(fig, use_container_width=True)

st.metric("Potência Média Estimada (kW)", f"{ (0.5 * rho * area * (c**3) * gamma(1 + 3/k)) / 1000:.2f}")
