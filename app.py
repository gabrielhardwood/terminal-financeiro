import streamlit as st
import yfinance as ticker_data
import google.generativeai as genai
import pandas as pd

# Configuração da Interface
st.set_page_config(page_title="Terminal Financeiro IA", layout="wide")
st.title("📊 Terminal de Equity Research - IA")

# Barra Lateral - Configurações
st.sidebar.header("Configurações do Sistema")
api_key = st.sidebar.text_input("Insira sua Gemini API Key", type="password")
selected_method = st.sidebar.selectbox("Método de Valuation", ["Graham", "DCF"])

# Entrada de Dados
ticker = st.text_input("Digite o Ticker do Ativo (ex: PETR4.SA ou AAPL)", "PETR4.SA")

if st.button("ANALISAR ATIVO"):
    if not api_key:
        st.error("Erro: A Chave API é obrigatória.")
    else:
        try:
            # 1. Coleta de Dados Financeiros
            asset = ticker_data.Ticker(ticker)
            info = asset.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            # 2. Cálculos de Valuation (Backend)
            lpa = info.get('trailingEps', 0)
            vpa = info.get('bookValue', 0)
            
            # Fórmula de Graham: Vi = sqrt(22.5 * LPA * VPA)
            graham_price = (22.5 * lpa * vpa)**0.5 if lpa > 0 and vpa > 0 else 0
            
            # Cálculo de Upside
            valuation_target = graham_price if selected_method == "Graham" else (current_price * 1.2) # DCF Simplificado para protótipo
            upside = ((valuation_target / current_price) - 1) * 100

            # 3. Exibição de Indicadores
            col1, col2, col3 = st.columns(3)
            col1.metric("Preço Atual", f"R$ {current_price:.2f}")
            col2.metric("Preço Justo (Graham)", f"R$ {graham_price:.2f}")
            col3.metric("Potencial (Upside)", f"{upside:.2f}%")

            # 4. Chamada da Inteligência Artificial
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.1-pro-preview')
            
            prompt = f"""
            Aja como um analista sênior. Analise o ativo {ticker}.
            Preço Atual: {current_price}. Preço Justo: {graham_price}. 
            Forneça:
            1. Análise Fundamentalista (Saúde financeira e múltiplos).
            2. Análise Técnica (Tendência de curto prazo).
            3. Recomendação Final (Compra, Venda ou Neutro) com justificativa técnica.
            """
            
            with st.spinner('Processando Relatório de IA...'):
                response = model.generate_content(prompt)
                st.subheader("Relatório de Análise Profissional")
                st.write(response.text)

        except Exception as e:
            st.error(f"Erro ao processar ativo: {e}")
