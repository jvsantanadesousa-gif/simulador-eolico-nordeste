import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.special import gamma
from scipy.stats import weibull_min

# Configuração da página
st.set_page_config(page_title="Dashboard de Potencial Eólico", layout="wide")

st.title("Análise e Estimação de Potencial Eólico - Tarefa 3.1")
st.markdown("Dashboard interactivo para modelagem da velocidade do vento utilizando a Distribuição de Weibull.")

# --- BARRA LATERAL (CONTROLES DO UTILIZADOR) ---
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

# Coeficiente de potência (Cp) - Limite de Betz é 0.59, turbinas reais ~0.35 a 0.45
cp = st.sidebar.slider("Coeficiente de Potência da Turbina (Cp)", min_value=0.1, max_value=0.59, value=0.40, step=0.01)

# --- SECÇÃO 1: DADOS HISTÓRICOS (CRESESB) ---
st.header("1. Análise Histórica de Regiões (Dados CRESESB)")
uploaded_file = st.file_uploader("Carregue o ficheiro CSV com os dados do CRESESB (Série histórica de velocidade do vento)", type=["csv"])

if uploaded_file is not None:
    # Lógica para ler os dados reais do utilizador
    df = pd.read_csv(uploaded_file)
    st.success("Dados carregados com sucesso!")
    # Assumindo que a coluna de velocidade se chama 'Velocidade'
    if 'Velocidade' in df.columns:
        velocidades_historicas = df['Velocidade'].values
    else:
        st.warning("O ficheiro CSV deve conter uma coluna chamada 'Velocidade'.")
        velocidades_historicas = np.random.weibull(k, 1000) * c # Fallback
else:
    st.info("A utilizar dados sintéticos simulados para a região Nordeste (baseado nos parâmetros k e c actuais). Carregue um ficheiro CSV para utilizar dados reais.")
    # Geração de série sintética usando o método da transformada inversa (simulação Monte Carlo simples)
    velocidades_historicas = weibull_min.rvs(k, scale=c, size=5000)

# Gráfico do Histograma dos Dados
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(x=velocidades_historicas, histnorm='probability density', name='Dados Históricos', marker_color='#1f77b4'))
fig_hist.update_layout(title="Distribuição das Velocidades do Vento", xaxis_title="Velocidade (m/s)", yaxis_title="Densidade de Probabilidade")
st.plotly_chart(fig_hist, use_container_width=True)

# --- SECÇÃO 2: MODELAGEM E ESTIMAÇÃO DE POTENCIAL ---
st.header("2. Estimação de Potencial Eólico (Modelo de Weibull)")

# Cálculo das Fórmulas do PDF
v_array = np.linspace(0, 25, 500)
# Função Densidade de Probabilidade (PDF) de Weibull
pdf_weibull = (k / c) * ((v_array / c) ** (k - 1)) * np.exp(-((v_array / c) ** k))

# Momentos Estatísticos
v_media = c * gamma(1 + (1 / k))
v_moda = c * ((1 - 1/k) ** (1/k)) if k > 1 else 0

col1, col2 = st.columns(2)

with col1:
    st.subheader("Curva de Probabilidade de Weibull")
    fig_pdf = go.Figure()
    fig_pdf.add_trace(go.Scatter(x=v_array, y=pdf_weibull, mode='lines', name=f'Weibull (k={k}, c={c})', line=dict(color='red', width=3)))
    fig_pdf.add_vline(x=v_media, line_dash="dash", line_color="green", annotation_text="V. Média")
    fig_pdf.update_layout(xaxis_title="Velocidade (m/s)", yaxis_title="f(v)", showlegend=True)
    st.plotly_chart(fig_pdf, use_container_width=True)

# --- SECÇÃO 3: POTÊNCIA DO VENTO VS POTÊNCIA DA TURBINA ---
with col2:
    st.subheader("Conversão Energética")
    
    # 1. Potência média disponível no vento (Densidade de potência * Área)
    # P_media = 0.5 * rho * c^3 * Gamma(1 + 3/k)
    densidade_potencia_vento = 0.5 * rho * (c ** 3) * gamma(1 + (3 / k))
    potencia_total_vento_media = densidade_potencia_vento * area_varredura
    
    # 2. Potência eléctrica gerada na turbina (Considerando o rendimento Cp)
    potencia_gerada_turbina = potencia_total_vento_media * cp
    
    st.metric(label="Velocidade Média Teórica (m/s)", value=f"{v_media:.2f}")
    
    st.markdown("### Resultados de Potência Média")
    st.metric(label="1. Potência Disponível no Vento (Total)", value=f"{potencia_total_vento_media / 1000:.2f} kW", 
              help="Calculada utilizando o 3º momento da distribuição de Weibull.")
    
    st.metric(label="2. Potência Gerada pela Turbina Eólica", value=f"{potencia_gerada_turbina / 1000:.2f} kW",
              help="Potência mecânica/eléctrica útil extraída, limitada pelo coeficiente Cp.")

st.markdown("---")
st.markdown("**Nota:** As estimativas dependem directamente do ajuste preciso dos parâmetros $k$ e $c$ extraídos dos dados do anemómetro de cada sítio específico do Nordeste.")