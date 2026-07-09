import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.special import gamma
from scipy.stats import weibull_min

st.set_page_config(layout="wide")
st.title("Simulador de Potencial Eólico - Tarefa 3.1")

# --- CARGA DE DADOS ---
uploaded_file = st.file_uploader("Suba o CSV do INMET", type=["csv"])
dados_vento = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';', skiprows=8, engine='python')
        nome_col = "VENTO, VELOCIDADE HORARIA (m/s)"
        
        if nome_col in df.columns:
            # Converte para numérico, substituindo vírgula por ponto
            col_limpa = df[nome_col].astype(str).str.replace(',', '.')
            dados_vento = pd.to_numeric(col_limpa, errors='coerce').dropna()
            
            if len(dados_vento) > 0:
                st.success(f"Sucesso! {len(dados_vento)} medições encontradas.")
            else:
                st.warning("Atenção: A coluna de velocidade está vazia no arquivo!")
        else:
            st.error("Coluna de velocidade não encontrada.")
    except Exception as e:
        st.error(f"Erro ao ler CSV: {e}")

# --- DECISÃO: USAR DADOS OU SIMULAR ---
if dados_vento is None or len(dados_vento) == 0:
    st.info("Utilizando dados simulados para demonstração.")
    k, c = 2.5, 8.5
    dados_vento = weibull_min.rvs(k, scale=c, size=1000)
else:
    # Se carregou dados, estimamos K e C via método dos momentos
    media = dados_vento.mean()
    desvio = dados_vento.std()
    k = (desvio / media) ** -1.086
    c = media / gamma(1 + 1/k)
    st.write(f"Parâmetros estimados: k={k:.2f}, c={c:.2f}")

# --- GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(x=dados_vento, nbins=30, title="Distribuição das Velocidades (Dados)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    v = np.linspace(0, 20, 100)
    pdf = (k / c) * (v / c)**(k - 1) * np.exp(-(v / c)**k)
    fig_weibull = px.line(x=v, y=pdf, title=f"Curva Teórica de Weibull (k={k:.2f}, c={c:.2f})")
    st.plotly_chart(fig_weibull, use_container_width=True)

# --- POTÊNCIA ---
st.header("Cálculo de Potência")
rho = 1.225
area = 5000 # Exemplo
potencia = 0.5 * rho * area * (c**3) * gamma(1 + 3/k)
st.metric("Potência Média Estimada (kW)", f"{potencia/1000:.2f}")
