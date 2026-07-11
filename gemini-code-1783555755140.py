import streamlit as st
import numpy as np
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

# O usuário define a velocidade média, o 'c' é calculado em função dela
v_media_desejada = st.sidebar.number_input("Velocidade Média Desejada [m/s]", min_value=1.0, value=8.5, step=0.1)

# Cálculo do parâmetro de escala 'c' baseado na média desejada: c = v_media / gamma(1 + 1/k)
c = v_media_desejada / gamma(1 + 1/k)

rho = st.sidebar.number_input("Densidade do ar (ρ) [kg/m³]", value=1.225, format="%.3f")
raio_rotor = st.sidebar.number_input("Raio do rotor da turbina [m]", value=40.0, step=0.1)
cp = st.sidebar.number_input("Coeficiente de Potência (Cp)", min_value=0.01, max_value=0.59, value=0.40, step=0.01)

area_varredura = np.pi * (raio_rotor ** 2)

# Gerar dados teóricos
dados_simulados = weibull_min.rvs(k, scale=c, size=5000)
v_teorico = np.linspace(0, 25, 200)
pdf = (k / c) * (v_teorico / c)**(k - 1) * np.exp(-(v_teorico / c)**k)
cdf = 1 - np.exp(-(v_teorico / c)**k)

# --- GRÁFICOS ---
col1, col2, col3 = st.columns(3)

with col1:
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=dados_simulados, histnorm='probability density', marker_color='#5DADE2', opacity=0.7))
    fig_hist.update_layout(title="Distribuição (Histograma)", xaxis_title="Velocidade (m/s)", yaxis_title="Densidade", plot_bgcolor='white', template='plotly_white')
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_weibull = go.Figure()
    fig_weibull.add_trace(go.Scatter(x=v_teorico, y=pdf, line=dict(color='#E74C3C', width=3)))
    fig_weibull.update_layout(title="Função Densidade (PDF)", xaxis_title="Velocidade (m/s)", yaxis_title="f(v)", plot_bgcolor='white', template='plotly_white')
    st.plotly_chart(fig_weibull, use_container_width=True)

with col3:
    fig_cdf = go.Figure()
    fig_cdf.add_trace(go.Scatter(x=v_teorico, y=cdf, line=dict(color='#27AE60', width=3)))
    fig_cdf.update_layout(title="Distribuição Acumulada (FDA)", xaxis_title="Velocidade (m/s)", yaxis_title="F(v)", plot_bgcolor='white', template='plotly_white')
    st.plotly_chart(fig_cdf, use_container_width=True)

# --- RESULTADOS ---
st.markdown("---")
st.subheader("Resultados Calculados")

# Cálculo da potência usando o 'c' derivado da velocidade média do usuário
potencia_media = 0.5 * rho * area_varredura * (c**3) * gamma(1 + 3/k)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Velocidade Média Alvo", f"{v_media_desejada:.2f} m/s")
c2.metric("Potência Disponível", f"{potencia_media/1000:.2f} kW")
c3.metric("Potência Gerada", f"{(potencia_media * cp)/1000:.2f} kW")
c4.metric("Área de Varredura", f"{area_varredura:.1f} m²")
