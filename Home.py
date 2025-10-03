# ==============================================================================
# BRVM ANALYSIS DASHBOARD (V0.1 - STREAMLIT)
# ==============================================================================

import streamlit as st
import requests
import pandas as pd

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Tableau de Bord BRVM",
    page_icon="📊",
    layout="wide"
)

# --- Variables Globales ---
API_URL = "https://brvm-api-gateway.onrender.com" # L'URL de votre API

# --- Fonctions de l'Application ---

@st.cache_data(ttl=3600) # Mettre en cache les données pendant 1 heure
def get_companies():
    """Récupère la liste des sociétés depuis l'API."""
    try:
        response = requests.get(f"{API_URL}/companies/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API : {e}")
        return []

@st.cache_data(ttl=600) # Mettre en cache les analyses pendant 10 minutes
def get_analysis(symbol):
    """Récupère l'analyse complète pour un symbole donné."""
    try:
        response = requests.get(f"{API_URL}/analysis/{symbol}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error(f"Impossible de récupérer l'analyse pour {symbol}.")
        return None

# --- Interface Utilisateur ---

st.title("📊 Tableau de Bord d'Analyse - BRVM")
st.markdown("Bienvenue sur votre tableau de bord personnel pour l'analyse des sociétés de la BRVM.")

companies = get_companies()

if companies:
    # Créer un dictionnaire pour trouver facilement le nom à partir du symbole
    company_map = {comp['symbol']: comp['name'] for comp in companies}
    
    # Menu déroulant pour sélectionner une société
    selected_symbol = st.selectbox(
        "Choisissez une société à analyser :",
        options=company_map.keys(),
        format_func=lambda symbol: f"{company_map[symbol]} ({symbol})" # Affiche "SONATEL (SNTS)"
    )

    if selected_symbol:
        st.markdown("---")
        
        # Afficher un indicateur de chargement
        with st.spinner(f"Chargement de l'analyse pour {selected_symbol}..."):
            analysis = get_analysis(selected_symbol)

        if analysis:
            st.header(f"Analyse pour {analysis.get('company_name', selected_symbol)}")
            st.caption(f"Dernières données du {analysis.get('last_trade_date')}")

            # Afficher le dernier cours
            st.metric(label="Dernier Cours", value=f"{analysis.get('last_price', 'N/A')} FCFA")

            # Afficher les analyses dans des colonnes
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Analyse Technique")
                st.write(analysis.get('technical_analysis', {}))

            with col2:
                st.subheader("Analyse Fondamentale")
                st.markdown(analysis.get('fundamental_analysis', "Aucune donnée."))
else:
    st.warning("Impossible de charger la liste des sociétés depuis l'API.")
