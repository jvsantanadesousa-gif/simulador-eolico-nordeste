import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.special import gamma
from scipy.stats import weibull_min

# Configuração da página
st.set_page_config(page_title="Dashboard de Potencial Eólico", layout="wide")

st.title("Simulador de Potencial Eólico - Comparativo")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA MANUAL E UPLOAD ---
st.sidebar.header("1. Upload dos Dados de Vento (Opcional)")
arquivo_carregado = st.sidebar.file_uploader(
    "Selecione um arquivo Excel (.xlsx) ou CSV", 
    type=["xlsx", "csv"]
)

st.sidebar.header("2. Parâmetros Manuais (Teóricos)")
k_manual = st.sidebar.number_input("Parâmetro de Forma (k) manual", min_value=0.1, value=2.5, step=0.1, format="%.2f")
c_manual = st.sidebar.number_input("Parâmetro de Escala (c) manual [m/s]", min_value=0.1, value=8.5, step=0.1, format="%.2f")

st.sidebar.header("3. Parâmetros da Turbina")
rho = st.sidebar.number_input("Densidade do ar (ρ) [kg/m³]", value=1.225, format="%.3f")
raio_rotor = st.sidebar.number_input("Raio do rotor da turbina [m]", value=40.0, step=0.1)
cp = st.sidebar.number_input("Coeficiente de Potência (Cp)", min_value=0.01, max_value=0.59, value=0.40, step=0.01)

area_varredura = np.pi * (raio_rotor ** 2)

# --- GERAÇÃO DOS DADOS TEÓRICOS (MANUAIS) ---
v_teorico = np.linspace(0, 25, 200)
pdf_manual = (k_manual / c_manual) * (v_teorico / c_manual)**(k_manual - 1) * np.exp(-(v_teorico / c_manual)**k_manual)
cdf_manual = 1 - np.exp(-(v_teorico / c_manual)**k_manual)

# Inicialização de variáveis de controle para o arquivo
dados_reais = None
k_auto, c_auto = None, None

# --- PROCESSAMENTO DO ARQUIVO SE HOUVER UPLOAD ---
if arquivo_carregado is not None:
    try:
        if arquivo_carregado.name.endswith('.xlsx'):
            df = pd.read_excel(arquivo_carregado)
        else:
            df = pd.read_csv(arquivo_carregado, sep=None, engine='python', encoding='utf-8')
        
        # Correção: Garante que o DataFrame possui colunas antes de renderizar o selectbox
        if len(df.columns) > 0:
            coluna_velocidade = st.sidebar.selectbox("Selecione a coluna de velocidade do vento", options=list(df.columns))
            dados_reais = df[coluna_velocidade].dropna().values
            
            # Ajuste automático de Weibull nos dados reais
            k_auto, loc, c_auto = weibull_min.fit(dados_reais, floc=0)
            
            if k_auto > 0 and c_auto > 0:
                max_velocidade_dados = float(np.max(dados_reais))
                limite_superior_grafico = max(max_velocidade_dados + 5.0, 25.0)
                
                v_teorico = np.linspace(0.01, limite_superior_grafico, 200)
                
                # Recalcula curvas teóricas manuais e adiciona as automáticas
                pdf_manual = (k_manual / c_manual) * (v_teorico / c_manual)**(k_manual - 1) * np.exp(-(v_teorico / c_manual)**k_manual)
                cdf_manual = 1 - np.exp(-(v_teorico / c_manual)**k_manual)
                
                pdf_auto = (k_auto / c_auto) * (v_teorico / c_auto)**(k_auto - 1) * np.exp(-(v_teorico / c_auto)**k_auto)
                cdf_auto = 1 - np.exp(-(v_teorico / c_auto)**k_auto)
            else:
                st.error("Não foi possível ajustar os parâmetros de Weibull para os dados fornecidos.")
                dados_reais = None
        else:
            st.error("O arquivo carregado não contém colunas válidas.")
        
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        dados_reais = None

# --- CONFIGURAÇÃO DOS GRÁFICOS ---
col1, col2, col3 = st.columns(3)

with col1:
    fig_hist = go.Figure()
    if dados_reais is not None:
        fig_hist.add_trace(go.Histogram(x=dados_reais, histnorm='probability density', name='Dados Reais', marker_color='#5DADE2', opacity=0.7))
    else:
        dados_simulados = weibull_min.rvs(k_manual, scale=c_manual, size=5000)
        fig_hist.add_trace(go.Histogram(x=dados_simulados, histnorm='probability density', name='Simulado (Manual)', marker_color='#5DADE2', opacity=0.7))
    fig_hist.update_layout(title="Distribuição (Histograma)", xaxis_title="Velocidade (m/s)", yaxis_title="Densidade", plot_bgcolor='white', template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_pdf = go.Figure()
    fig_pdf.add_trace(go.Scatter(x=v_teorico, y=pdf_manual, name='FDP Manual', line=dict(color='#E74C3C', width=3, dash='dash')))
    if dados_reais is not None:
        fig_pdf.add_trace(go.Scatter(x=v_teorico, y=pdf_auto, name='FDP Real', line=dict(color='#943126', width=3)))
    fig_pdf.update_layout(title="Função Densidade (PDF)", xaxis_title="Velocidade (m/s)", yaxis_title="f(v)", plot_bgcolor='white', template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_pdf, use_container_width=True)

with col3:
    fig_cdf = go.Figure()
    fig_cdf.add_trace(go.Scatter(x=v_teorico, y=cdf_manual, name='FDA Manual', line=dict(color='#27AE60', width=3, dash='dash')))
    if dados_reais is not None:
        fig_cdf.add_trace(go.Scatter(x=v_teorico, y=cdf_auto, name='FDA Real', line=dict(color='#145A32', width=3)))
    fig_cdf.update_layout(title="Distribuição Acumulada (FDA)", xaxis_title="Velocidade (m/s)", yaxis_title="F(v)", plot_bgcolor='white', template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_cdf, use_container_width=True)

# --- RESULTADOS ---
st.markdown("---")
st.subheader("Resultados Calculados")

v_media_manual = c_manual * gamma(1 + 1/k_manual)
potencia_media_manual = 0.5 * rho * area_varredura * (c_manual**3) * gamma(1 + 3/k_manual)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Velocidade Média (Manual)", f"{v_media_manual:.2f} m/s")
c2.metric("Potência Disponível (Manual)", f"{potencia_media_manual/1000:.2f} kW")
c3.metric("Potência Gerada (Manual)", f"{(potencia_media_manual * cp)/1000:.2f} kW")
c4.metric("Área de Varredura", f"{area_varredura:.1f} m²")

# --- EXIBIÇÃO AUTOMÁTICA DOS VALORES DO ARQUIVO ABAIXO DOS RESULTADOS ---
if dados_reais is not None and k_auto is not None and c_auto is not None:
    st.markdown("---")
    st.subheader("Parâmetros Identificados no Histórico Real")
    
    v_media_real = np.mean(dados_reais)
    potencia_media_real = 0.5 * rho * area_varredura * (c_auto**3) * gamma(1 + 3/k_auto)
    
    ca1, ca2, ca3, ca4 = st.columns(4)
    ca1.metric("Parâmetro de Forma (k)", f"{k_auto:.2f}")
    ca2.metric("Parâmetro de Escala (c)", f"{c_auto:.2f} m/s")
    ca3.metric("Velocidade Média Real", f"{v_media_real:.2f} m/s")
    ca4.metric("Potência Gerada Real", f"{(potencia_media_real * cp)/1000:.2f} kW")
