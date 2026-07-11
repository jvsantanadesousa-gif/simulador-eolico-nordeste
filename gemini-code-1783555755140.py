import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.special import gamma
from scipy.stats import weibull_min

# Configuração da página
st.set_page_config(page_title="Dashboard de Potencial Eólico", layout="wide")

st.title("Simulador de Potencial Eólico - Tarefa 3.1")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA MANUAL ---
st.sidebar.header("Parâmetros de Entrada")
k = st.sidebar.number_input("Parâmetro de Forma (k)", min_value=0.1, value=2.5, step=0.1, format="%.2f")
c = st.sidebar.number_input("Parâmetro de Escala (c) [m/s]", min_value=0.1, value=8.5, step=0.1, format="%.2f")
rho = st.sidebar.number_input("Densidade do ar (ρ) [kg/m³]", value=1.225, format="%.3f")
raio_rotor = st.sidebar.number_input("Raio do rotor da turbina [m]", value=40.0, step=0.1)
cp = st.sidebar.number_input("Coeficiente de Potência (Cp)", min_value=0.01, max_value=0.59, value=0.40, step=0.01)

area_varredura = np.pi * (raio_rotor ** 2)

# --- CARGA E TRATAMENTO DOS DADOS ---
st.header("1. Análise Histórica (Dados INMET)")
uploaded_file = st.file_uploader("Carregue o CSV do INMET (Dados Reais)", type=["csv"])
dados_finais = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';', skiprows=8, engine='python')
        col_nome = "VENTO, VELOCIDADE HORARIA (m/s)"
        
        if col_nome in df.columns:
            dados = pd.to_numeric(df[col_nome].astype(str).str.replace(',', '.'), errors='coerce').dropna()
            if len(dados) > 0:
                dados_finais = dados.values
                st.success(f"Dados reais carregados com sucesso ({len(dados_finais)} registros).")
            else:
                st.warning("O arquivo foi carregado, mas a coluna de velocidade está vazia.")
    except Exception as e:
        st.error(f"Erro na leitura do arquivo: {e}")

if dados_finais is None:
    st.info("Modo de Simulação: Utilizando distribuição teórica de Weibull.")
    dados_finais = weibull_min.rvs(k, scale=c, size=1000)

# --- GRÁFICOS ---
col1, col2 = st.columns(2)

# PDF e Histograma
with col1:
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=dados_finais, histnorm='probability density', name='Dados', marker_color='#1f77b4'))
    fig_hist.update_layout(title="Distribuição das Velocidades (Histograma)", xaxis_title="Velocidade (m/s)", yaxis_title="Densidade")
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    v_teorico = np.linspace(0, 25, 200)
    pdf = (k / c) * (v_teorico / c)**(k - 1) * np.exp(-(v_teorico / c)**k)
    fig_weibull = go.Figure()
    fig_weibull.add_trace(go.Scatter(x=v_teorico, y=pdf, name='PDF', line=dict(color='red', width=3)))
    fig_weibull.update_layout(title="Função Densidade de Probabilidade (PDF)", xaxis_title="Velocidade (m/s)", yaxis_title="f(v)")
    st.plotly_chart(fig_weibull, use_container_width=True)

# --- TERCEIRO GRÁFICO: FDA (CDF) ---
st.subheader("Função de Distribuição Acumulada (FDA)")
cdf = 1 - np.exp(-(v_teorico / c)**k)

fig_cdf = go.Figure()
fig_cdf.add_trace(go.Scatter(x=v_teorico, y=cdf, name='FDA', line=dict(color='green', width=3)))
fig_cdf.update_layout(xaxis_title="Velocidade (m/s)", yaxis_title="F(v)", template="plotly_white")
st.plotly_chart(fig_cdf, use_container_width=True)

# --- RESULTADOS E VELOCIDADE MÉDIA ---
st.markdown("---")
st.header("Cálculos Estatísticos e Potência")

v_media_teorica = c * gamma(1 + 1/k)
potencia_media = 0.5 * rho * area_varredura * (c**3) * gamma(1 + 3/k)

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Velocidade Média (Teórica)", f"{v_media_teorica:.2f} m/s")
col_b.metric("Potência Disponível", f"{potencia_media/1000:.2f} kW")
col_c.metric("Potência Gerada", f"{(potencia_media * cp)/1000:.2f} kW")
col_d.metric("Área de Varredura", f"{area_varredura:.1f} m²")
