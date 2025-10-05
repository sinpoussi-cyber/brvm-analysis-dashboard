# ==============================================================================
# PAGE D'ACCUEIL : SCREENER DE MARCHÉ
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
def api_request_with_retry(url: str, retries: int = 3, delay: int = 5, timeout: int = 30):
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.warning(f"Tentative {i + 1}/{retries} échouée. Réessai...")
            time.sleep(delay)
    st.error(f"Impossible de joindre l'API après {retries} tentatives.")
    return None

# --- Chargement des Données ---
st.title("📈 Screener de Marché BRVM")
st.markdown("Vue d'ensemble des signaux techniques pour toutes les sociétés cotées.")

@st.cache_data(ttl=300) # Cache de 5 minutes
def get_screener_data():
    return api_request_with_retry(f"{API_URL}/screener/")

screener_data = get_screener_data()

if screener_data:
    # Créer un DataFrame Pandas
    df = pd.DataFrame(screener_data)
    
    # Renommer les colonnes pour l'affichage
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

    # Afficher le tableau interactif avec mise en forme conditionnelle
    st.dataframe(
        df.style.applymap(color_signals, subset=['Moyennes Mobiles', 'Bandes Bollinger', 'MACD', 'RSI', 'Stochastique']),
        use_container_width=True,
        height=800, # Ajuster la hauteur
        hide_index=True # Cacher l'index numérique
    )
    
    st.info("💡 **Astuce :** Cliquez sur les en-têtes de colonnes pour trier le tableau. Utilisez la page 'Analyse Détaillée' dans le menu pour voir les détails d'une société.")

else:
    st.warning("Impossible de charger les données du screener. Veuillez réessayer plus tard.")

st.markdown("---")
st.caption("Données fournies par l'API BRVM Analysis Gateway.")
