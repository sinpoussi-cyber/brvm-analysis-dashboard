# ==============================================================================
# PAGE D'ACCUEIL : SCREENER DE MARCHÉ (V0.3 - GESTION AMÉLIORÉE DES TIMEOUTS)
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
import time

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Screener BRVM",
    page_icon="📈",
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
            response.raise_for_status() # Lève une exception si la requête échoue (ex: 404, 502, 503)
            return response.json()
        except requests.exceptions.RequestException as e:
            st.warning(f"L'API est peut-être en cours de démarrage... Tentative {i + 1}/{retries}. Réessai dans {delay} secondes.")
            time.sleep(delay) # Attendre plus longtemps entre les tentatives
    
    st.error(f"Impossible de joindre l'API après {retries} tentatives. Le service est peut-être indisponible ou en maintenance.")
    return None

# --- Chargement des Données ---
@st.cache_data(ttl=300) # Mettre en cache les données du screener pour 5 minutes
def get_screener_data():
    """Récupère les données du screener depuis l'API."""
    return api_request_with_retry(f"{API_URL}/screener/")

# --- Interface Utilisateur ---
st.title("📈 Screener de Marché BRVM")
st.markdown("Vue d'ensemble des derniers signaux techniques pour toutes les sociétés cotées.")

# Afficher un message de chargement pendant la récupération des données
with st.spinner("Connexion à l'API et chargement des données du marché..."):
    screener_data = get_screener_data()

if screener_data:
    # Créer un DataFrame Pandas à partir des données JSON de l'API
    df = pd.DataFrame(screener_data)
    
    # Renommer les colonnes pour un affichage plus convivial
    df = df.rename(columns={
        "symbol": "Symbole",
        "name": "Société",
        "last_price": "Dernier Cours (FCFA)",
        "signal_mm": "Moyennes Mobiles",
        "signal_bollinger": "Bandes Bollinger",
        "signal_macd": "MACD",
        "signal_rsi": "RSI",
        "signal_stochastic": "Stochastique"
    })
    
    # Ordonner les colonnes pour une meilleure lecture
    column_order = [
        "Symbole", "Société", "Dernier Cours (FCFA)", "Moyennes Mobiles", 
        "Bandes Bollinger", "MACD", "RSI", "Stochastique"
    ]
    df = df[column_order]

    # Fonction pour colorer les cellules en fonction du signal
    def color_signals(val):
        if isinstance(val, str):
            val_lower = val.lower()
            if 'achat' in val_lower:
                return 'background-color: #d4edda; color: #155724' # Vert
            elif 'vente' in val_lower:
                return 'background-color: #f8d7da; color: #721c24' # Rouge
            elif 'neutre' in val_lower:
                return 'background-color: #fff3cd; color: #856404' # Jaune
        return ''

    # Afficher le tableau interactif avec la mise en forme conditionnelle
    st.dataframe(
        df.style.apply(lambda s: s.map(color_signals), subset=['Moyennes Mobiles', 'Bandes Bollinger', 'MACD', 'RSI', 'Stochastique']),
        use_container_width=True,
        height=800,
        hide_index=True
    )
    
    st.info("💡 **Astuce :** Cliquez sur les en-têtes de colonnes pour trier le tableau. Utilisez la page 'Analyse Détaillée' dans le menu de gauche pour approfondir l'analyse d'une société.")
else:
    st.error("Impossible de charger les données du screener. L'API n'a pas répondu. Veuillez réessayer de rafraîchir la page dans une minute.")

st.markdown("---")
st.caption("Données fournies par l'API BRVM Analysis Gateway.")
