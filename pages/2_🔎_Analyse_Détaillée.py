# ==============================================================================
# PAGE SECONDAIRE : ANALYSE DÉTAILLÉE (V0.3 - GESTION AMÉLIORÉE DES TIMEOUTS)
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Analyse Détaillée BRVM",
    page_icon="🔎",
    layout="wide"
)

# --- Variables Globales ---
API_URL = "https://brvm-api-gateway.onrender.com"

# --- Fonction de Requête API avec Retry ---
def api_request_with_retry(url: str, retries: int = 3, delay: int = 15, timeout: int = 45):
    """
    Effectue une requête GET avec plusieurs tentatives, en laissant le temps
    à une API "endormie" de se réveiller.
    """
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            # Affiche un avertissement dans la barre latérale pour ne pas polluer la page
            st.sidebar.warning(f"Tentative {i + 1}/{retries} pour joindre l'API...")
            time.sleep(delay)
    
    st.error(f"Impossible de joindre l'API après {retries} tentatives. Le service est peut-être indisponible.")
    return None

# --- Fonctions de Chargement ---
@st.cache_data(ttl=3600)
def get_companies():
    """Récupère la liste des sociétés depuis l'API avec des tentatives multiples."""
    data = api_request_with_retry(f"{API_URL}/companies/")
    return data if data else []

@st.cache_data(ttl=600)
def get_analysis(symbol):
    """Récupère l'analyse complète pour un symbole donné avec des tentatives multiples."""
    if not symbol:
        return None
    return api_request_with_retry(f"{API_URL}/analysis/{symbol}")

# --- Interface Utilisateur ---
st.title("🔎 Analyse Détaillée par Société")

companies = get_companies()

if companies:
    company_map = {comp['symbol']: comp['name'] for comp in companies}
    
    # Placer le sélecteur dans la barre latérale pour une meilleure ergonomie
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
            st.caption(f"Dernières données disponibles du {analysis.get('last_trade_date', 'N/A')}")

            st.metric(label="Dernier Cours de Clôture", value=f"{analysis.get('last_price', 'N/A')} FCFA")

            # Graphique
            if 'price_history' in analysis and analysis['price_history']:
                df_history = pd.DataFrame(analysis['price_history'])
                df_history['date'] = pd.to_datetime(df_history['date'])
                fig = px.line(
                    df_history, 
                    x='date', 
                    y='price', 
                    title=f"Historique du Cours de {analysis['company_name']} sur 50 jours",
                    labels={'date': 'Date', 'price': 'Cours (FCFA)'}
                )
                fig.update_layout(
                    xaxis_title='',
                    yaxis_title='Cours (FCFA)',
                    title_x=0.5,
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun historique de prix disponible pour générer le graphique.")

            # Analyses
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Synthèse Technique")
                tech = analysis.get('technical_analysis', {})
                if tech and any(tech.values()):
                    st.write(f"**Moyennes Mobiles :** {tech.get('moving_average_signal', 'N/A')}")
                    st.write(f"**Bandes Bollinger :** {tech.get('bollinger_bands_signal', 'N/A')}")
                    st.write(f"**MACD :** {tech.get('macd_signal', 'N/A')}")
                    st.write(f"**RSI :** {tech.get('rsi_signal', 'N/A')}")
                    st.write(f"**Stochastique :** {tech.get('stochastic_signal', 'N/A')}")
                else:
                    st.info("Aucune donnée d'analyse technique disponible pour cette date.")
            with col2:
                st.subheader("Synthèse Fondamentale (IA)")
                fundamental_text = analysis.get('fundamental_analysis')
                if fundamental_text and "Aucune analyse" not in fundamental_text:
                    st.markdown(fundamental_text)
                else:
                    st.info("Aucune analyse fondamentale disponible dans la base de données.")
        else:
            st.error(f"Impossible de charger l'analyse détaillée pour {selected_symbol}.")
else:
    st.warning("Impossible de charger la liste des sociétés depuis l'API.")

st.markdown("---")
st.sidebar.info("Application alimentée par l'API BRVM Analysis Gateway.")
