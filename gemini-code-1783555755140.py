import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.special import gamma
from scipy.stats import weibull_min

st.set_page_config(page_title="Dashboard de Potencial Eólico", layout="wide")

st.title("Análise e Estimação de Potencial Eólico")

# --- MEMÓRIA DE SESSÃO (Para manter os dados carregados) ---
if 'dados' not in st.session_state:
    st.session_state.dados = weibull_min.rvs(2.5, scale=8.5, size=5000)

# --- BARRA LATERAL ---
st.sidebar.header("Parâmetros de Entrada")
k = st.sidebar.slider("Parâmetro de Forma (k)", 1.0, 4.0, 2.5, 0.1)
c = st.sidebar.slider("Parâmetro de Escala (c) [m/s]", 4.0, 12.0, 8.5, 0.1)
rho = st.sidebar.number_input("Densidade do ar (ρ) [kg/m³]", value=1.225)
raio_rotor = st.sidebar.number_input("Raio do rotor da turbina [m]", value=40.0)
area_varredura = np.pi * (raio_rotor ** 2)
cp = st.sidebar.slider("Coeficiente de Potência (Cp)", 0.1, 0.59, 0.40, 0.01)

# --- CARGA DE DADOS ---
uploaded_file = st.file_uploader("Carregue o CSV do INMET", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';', skiprows=8, engine='python')
        col_nome = "VENTO, VELOCIDADE HORARIA (m/s)"
        
        if col_nome in df.columns:
            # Tratamento de dados: converte, limpa e remove vazios
            dados_temp = pd.to_numeric(df[col_nome].astype(str).str.replace(',', '.'), errors='coerce')
            dados_limpos = dados_temp.dropna().values
            
            if len(dados_limpos) > 0:
                st.session_state.dados = dados_limpos
                st.success(f"Dados carregados! {len(dados_limpos)} pontos processados.")
            else:
                st.error("O arquivo foi lido, mas a coluna de velocidade está vazia!")
        else:
            st.error("Coluna de velocidade não encontrada no CSV.")
    except Exception as e:
        st.error(f"Erro na leitura: {e}")

# --- GRÁFICO (Usa st.session_state.dados) ---
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(x=st.session_state.dados, histnorm='probability density', name='Dados'))
fig_hist.update_layout(title="Distribuição das Velocidades (Dados Atuais)", xaxis_title="m/s")
st.plotly_chart(fig_hist, use_container_width=True)

# --- MODELAGEM E POTÊNCIA ---
st.header("2. Estimação Teórica")
v_array = np.linspace(0, 25, 500)
pdf_weibull = (k / c) * ((v_array / c) ** (k - 1)) * np.exp(-((v_array / c) ** k))
v_media = c * gamma(1 + (1 / k))

col1, col2 = st.columns(2)
with col1:
    fig_pdf = go.Figure()
    fig_pdf.add_trace(go.Scatter(x=v_array, y=pdf_weibull, name='Weibull', line=dict(color='red')))
    st.plotly_chart(fig_pdf, use_container_width=True)

with col2:
    densidade_potencia = 0.5 * rho * (c ** 3) * gamma(1 + (3 / k))
    potencia_total = densidade_potencia * area_varredura
    st.metric("Velocidade Média (Teórica)", f"{v_media:.2f} m/s")
    st.metric("Potência Disponível", f"{potencia_total / 1000:.2f} kW")
    st.metric("Potência Gerada (Turbina)", f"{(potencia_total * cp) / 1000:.2f} kW")
