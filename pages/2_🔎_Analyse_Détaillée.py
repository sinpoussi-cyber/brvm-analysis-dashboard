# ==============================================================================
# PAGE SECONDAIRE : ANALYSE DÉTAILLÉE (V1.0)
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Analyse Détaillée", page_icon="🔎", layout="wide")

API_URL = "https://brvm-api-gateway.onrender.com"

# --- Fonctions de l'Application ---
@st.cache_data(ttl=3600)
def get_companies():
    try:
        response = requests.get(f"{API_URL}/companies/", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API : {e}")
        return []

@st.cache_data(ttl=600)
def get_analysis(symbol):
    if not symbol: return None
    try:
        response = requests.get(f"{API_URL}/analysis/{symbol}", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Impossible de récupérer l'analyse pour {symbol} : {e}")
        return None

# --- Interface Utilisateur ---
st.title("🔎 Analyse Détaillée par Société")

companies = get_companies()

if companies:
    company_map = {comp['symbol']: comp['name'] for comp in companies}
    
    # Le sélecteur est maintenant dans la barre latérale pour une meilleure ergonomie
    st.sidebar.header("Navigation")
    selected_symbol = st.sidebar.selectbox(
        label="Choisissez une société :",
        options=sorted(company_map.keys()),
        format_func=lambda symbol: f"{company_map[symbol]} ({symbol})"
    )

    if selected_symbol:
        with st.spinner(f"Chargement de l'analyse complète pour {selected_symbol}..."):
            analysis = get_analysis(selected_symbol)

        if analysis:
            st.header(f"{analysis.get('company_name', selected_symbol)}")
            st.caption(f"Données au {analysis.get('last_trade_date', 'N/A')}")
            st.metric(label="Dernier Cours de Clôture", value=f"{analysis.get('last_price', 'N/A')} FCFA")

            if 'price_history' in analysis and analysis['price_history']:
                df_history = pd.DataFrame(analysis['price_history'])
                df_history['date'] = pd.to_datetime(df_history['date'])
                fig = px.line(
                    df_history, x='date', y='price', 
                    title=f"Historique du Cours de {analysis['company_name']} sur 50 jours",
                    labels={'date': 'Date', 'price': 'Cours (FCFA)'}
                )
                fig.update_layout(xaxis_title='', yaxis_title='Cours (FCFA)', title_x=0.5)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun historique de prix disponible pour générer le graphique.")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Synthèse Technique")
                tech_analysis = analysis.get('technical_analysis', {})
                if tech_analysis:
                    st.write(f"**Moyennes Mobiles:** {tech_analysis.get('mm_decision', 'N/A')}")
                    st.write(f"**Bandes Bollinger:** {tech_analysis.get('bollinger_decision', 'N/A')}")
                    st.write(f"**MACD:** {tech_analysis.get('macd_decision', 'N/A')}")
                    st.write(f"**RSI:** {tech_analysis.get('rsi_signal', 'N/A')}")
                    st.write(f"**Stochastique:** {tech_analysis.get('stochastic_decision', 'N/A')}")
                else:
                    st.info("Pas de données techniques disponibles.")
            with col2:
                st.subheader("Synthèse Fondamentale (IA)")
                fundamental_text = analysis.get('fundamental_analysis')
                if fundamental_text and "Erreur" not in fundamental_text:
                    st.markdown(fundamental_text)
                else:
                    st.info("Pas d'analyse fondamentale disponible actuellement.")
        else:
            st.error("Impossible de charger l'analyse pour cette société.")
else:
    st.warning("Impossible de charger la liste des sociétés depuis l'API.")
