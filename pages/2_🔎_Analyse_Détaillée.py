# ==============================================================================
# PAGE SECONDAIRE : ANALYSE DÉTAILLÉE
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Analyse Détaillée BRVM", page_icon="🔎", layout="wide")

API_URL = "https://brvm-api-gateway.onrender.com"

# --- Fonction de Requête API avec Retry (à dupliquer ou mettre dans un module partagé) ---
def api_request_with_retry(url: str, retries: int = 3, delay: int = 5, timeout: int = 30):
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            time.sleep(delay)
    return None

# --- Fonctions de Chargement ---
@st.cache_data(ttl=3600)
def get_companies():
    data = api_request_with_retry(f"{API_URL}/companies/")
    return data if data else []

@st.cache_data(ttl=600)
def get_analysis(symbol):
    if not symbol: return None
    return api_request_with_retry(f"{API_URL}/analysis/{symbol}")

# --- Interface ---
st.title("🔎 Analyse Détaillée par Société")

companies = get_companies()

if companies:
    company_map = {comp['symbol']: comp['name'] for comp in companies}
    
    # Utiliser un selectbox dans la barre latérale pour le choix
    selected_symbol = st.sidebar.selectbox(
        label="Choisissez une société :",
        options=sorted(company_map.keys()),
        format_func=lambda symbol: f"{company_map[symbol]} ({symbol})"
    )

    if selected_symbol:
        with st.spinner(f"Chargement de l'analyse pour {selected_symbol}..."):
            analysis = get_analysis(selected_symbol)

        if analysis:
            st.header(f"{analysis.get('company_name')} ({selected_symbol})")
            st.caption(f"Données au {analysis.get('last_trade_date', 'N/A')}")
            st.metric(label="Dernier Cours", value=f"{analysis.get('last_price', 'N/A')} FCFA")

            # Graphique
            if 'price_history' in analysis and analysis['price_history']:
                df_history = pd.DataFrame(analysis['price_history'])
                df_history['date'] = pd.to_datetime(df_history['date'])
                fig = px.line(df_history, x='date', y='price', title="Historique du Cours (50 jours)", labels={'date': 'Date', 'price': 'Cours (FCFA)'})
                fig.update_layout(xaxis_title='', yaxis_title='Cours (FCFA)', margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)

            # Analyses
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Synthèse Technique")
                tech = analysis.get('technical_analysis', {})
                if tech:
                    st.write(f"**Moyennes Mobiles:** {tech.get('moving_average_signal')}")
                    st.write(f"**Bandes Bollinger:** {tech.get('bollinger_bands_signal')}")
                    st.write(f"**MACD:** {tech.get('macd_signal')}")
                    st.write(f"**RSI:** {tech.get('rsi_signal')}")
                    st.write(f"**Stochastique:** {tech.get('stochastic_signal')}")
                else:
                    st.info("Pas de données techniques.")
            with col2:
                st.subheader("Synthèse Fondamentale (IA)")
                st.markdown(analysis.get('fundamental_analysis') or "Pas d'analyse fondamentale.")
        else:
            st.error("Impossible de charger l'analyse pour cette société.")
else:
    st.warning("Impossible de charger la liste des sociétés.")
