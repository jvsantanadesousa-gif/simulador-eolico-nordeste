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

# --- BARRA LATERAL (CONTROLES DO USUÁRIO) ---
st.sidebar.header("Parâmetros de Entrada")
st.sidebar.markdown("Manipule os dados para estimar o potencial.")

# Parâmetros de Weibull
st.sidebar.subheader("Parâmetros de Weibull")
k = st.sidebar.slider("Parâmetro de Forma (k)", min_value=1.0, max_value=4.0, value=2.5, step=0.1)
c = st.sidebar.slider("Parâmetro de Escala (c) [m/s]", min_value=4.0, max_value=12.0, value=8.5, step=0.1)

# Parâmetros da Turbina e Ambiente
st.sidebar.subheader("Parâmetros Físicos e da Turbina")
rho = st.sidebar.number_input("Densidade do ar (ρ) [kg/m³]", value=1.225)
raio_rotor = st.sidebar.number_input("Raio do rotor da turbina [m]", value=40.0)
area_varredura = np.pi * (raio_rotor ** 2)
st.sidebar.text(f"Área de varredura: {area_varredura:.2f} m²")

# Coeficiente de potência (Cp)
cp = st.sidebar.slider("Coeficiente de Potência da Turbina (Cp)", min_value=0.1, max_value=0.59, value=0.40, step=0.01)

# --- SEÇÃO 1: DADOS HISTÓRICOS ---
st.header("1. Análise Histórica de Regiões")
uploaded_file = st.file_uploader("Carregue o arquivo CSV com os dados da série histórica", type=["csv"])

if uploaded_file is not None:
    # CORREÇÃO APLICADA: encoding latin1 e separador por ponto e vírgula
    df = pd.read_csv(uploaded_file, encoding='latin1', sep=';')
    st.success("Dados carregados com sucesso!")
    
    # Busca flexível pela coluna 'Velocidade'
    coluna_alvo = None
    for col in df.columns:
        if 'velocidade' in col.strip().lower():
            coluna_alvo = col
            break

    if coluna_alvo:
        # Tratamento de dados: converte vírgula para ponto e transforma em número
        velocidades_brutas = df[coluna_alvo].astype(str).str.replace(',', '.')
        velocidades_historicas = pd.to_numeric(velocidades_brutas, errors='coerce').dropna().values
    else:
        st.warning("O arquivo CSV deve conter uma coluna com o nome 'Velocidade'.")
        velocidades_historicas = np.random.weibull(k, 1000) * c
else:
    st.info("Utilizando dados sintéticos simulados. Carregue um arquivo CSV para utilizar dados reais.")
    velocidades_historicas = weibull_min.rvs(k, scale=c, size=5000)

# Gráfico do Histograma dos Dados
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(x=velocidades_historicas, histnorm='probability density', name='Dados Históricos', marker_color='#1f77b4'))
fig_hist.update_layout(title="Distribuição das Velocidades do Vento", xaxis_title="Velocidade (m/s)", yaxis_title="Densidade de Probabilidade")
st.plotly_chart(fig_hist, use_container_width=True)

# --- SEÇÃO 2: MODELAGEM E ESTIMAÇÃO DE POTENCIAL ---
st.header("2. Estimação de Potencial Eólico (Modelo de Weibull)")

v_array = np.linspace(0, 25, 500)
pdf_weibull = (k / c) * ((v_array / c) ** (k - 1)) * np.exp(-((v_array / c) ** k))
v_media = c * gamma(1 + (1 / k))

col1, col2 = st.columns(2)

with col1:
    st.subheader("Curva de Probabilidade de Weibull")
    fig_pdf = go.Figure()
    fig_pdf.add_trace(go.Scatter(x=v_array, y=pdf_weibull, mode='lines', name=f'Weibull (k={k}, c={c})', line=dict(color='red', width=3)))
    fig_pdf.add_vline(x=v_media, line_dash="dash", line_color="green", annotation_text="V. Média")
    fig_pdf.update_layout(xaxis_title="Velocidade (m/s)", yaxis_title="f(v)", showlegend=True)
    st.plotly_chart(fig_pdf, use_container_width=True)

with col2:
    st.subheader("Conversão Energética")
    
    densidade_potencia_vento = 0.5 * rho * (c ** 3) * gamma(1 + (3 / k))
    potencia_total_vento_media = densidade_potencia_vento * area_varredura
    potencia_gerada_turbina = potencia_total_vento_media * cp
    
    st.metric(label="Velocidade Média Teórica (m/s)", value=f"{v_media:.2f}")
    
    st.markdown("### Resultados de Potência Média")
    st.metric(label="1. Potência Disponível no Vento", value=f"{potencia_total_vento_media / 1000:.2f} kW")
    st.metric(label="2. Potência Gerada pela Turbina", value=f"{potencia_gerada_turbina / 1000:.2f} kW")
