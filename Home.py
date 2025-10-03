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
API_URL = "https://brvm-api-gateway.onrender.com" # L'URL de votre API sur Render

# --- Fonctions de l'Application ---

@st.cache_data(ttl=3600) # Mettre en cache la liste des sociétés pendant 1 heure
def get_companies():
    """Récupère la liste des sociétés depuis l'API."""
    try:
        response = requests.get(f"{API_URL}/companies/")
        response.raise_for_status() # Lève une exception si la requête échoue (ex: 404, 500)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API pour charger les sociétés : {e}")
        return []

@st.cache_data(ttl=600) # Mettre en cache l'analyse d'une société pendant 10 minutes
def get_analysis(symbol):
    """Récupère l'analyse complète pour un symbole donné depuis l'API."""
    if not symbol:
        return None
    try:
        response = requests.get(f"{API_URL}/analysis/{symbol}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Impossible de récupérer l'analyse pour {symbol} : {e}")
        return None

# --- Interface Utilisateur de l'Application ---

st.title("📊 Tableau de Bord d'Analyse - Marché BRVM")
st.markdown("Bienvenue sur votre tableau de bord personnel pour l'analyse des sociétés de la Bourse Régionale des Valeurs Mobilières.")

# Charger la liste des sociétés
companies = get_companies()

if companies:
    # Créer un dictionnaire pour trouver facilement le nom à partir du symbole
    # (ex: {'SNTS': 'SONATEL', 'SOGC': 'SOGB CI'})
    company_map = {comp['symbol']: comp['name'] for comp in companies}
    
    # Menu déroulant pour sélectionner une société
    selected_symbol = st.selectbox(
        label="Choisissez une société à analyser :",
        options=sorted(company_map.keys()), # Trier les symboles par ordre alphabétique
        format_func=lambda symbol: f"{company_map[symbol]} ({symbol})" # Affiche "SONATEL (SNTS)" dans la liste
    )

    if selected_symbol:
        st.markdown("---")
        
        # Afficher un indicateur de chargement pendant que les données sont récupérées
        with st.spinner(f"Chargement de l'analyse pour {selected_symbol}..."):
            analysis = get_analysis(selected_symbol)

        if analysis:
            # Afficher le titre de l'analyse
            st.header(f"Analyse pour {analysis.get('company_name', selected_symbol)}")
            st.caption(f"Dernières données disponibles du {analysis.get('last_trade_date', 'N/A')}")

            # Afficher le dernier cours mis en évidence
            st.metric(label="Dernier Cours de Clôture", value=f"{analysis.get('last_price', 'N/A')} FCFA")

            # Séparer les analyses en deux colonnes pour une meilleure lisibilité
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Synthèse Technique")
                tech_analysis = analysis.get('technical_analysis', {})
                if tech_analysis:
                    st.write(f"**Signaux des Moyennes Mobiles :** {tech_analysis.get('moving_average_signal', 'N/A')}")
                    st.write(f"**Signaux des Bandes de Bollinger :** {tech_analysis.get('bollinger_bands_signal', 'N/A')}")
                    st.write(f"**Signaux du MACD :** {tech_analysis.get('macd_signal', 'N/A')}")
                    st.write(f"**Signaux du RSI :** {tech_analysis.get('rsi_signal', 'N/A')}")
                    st.write(f"**Signaux du Stochastique :** {tech_analysis.get('stochastic_signal', 'N/A')}")
                else:
                    st.info("Aucune donnée d'analyse technique disponible.")

            with col2:
                st.subheader("Synthèse Fondamentale")
                fundamental_text = analysis.get('fundamental_analysis', "Aucune donnée.")
                st.markdown(fundamental_text if fundamental_text else "Aucune analyse fondamentale disponible.")
else:
    st.warning("Impossible de charger la liste des sociétés depuis l'API. Le service est peut-être momentanément indisponible.")

# Ajouter un pied de page
st.markdown("---")
st.info("Cette application est alimentée par une API personnalisée connectée à une base de données d'analyses financières.")
