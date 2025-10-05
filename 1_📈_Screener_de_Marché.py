# ==============================================================================
# PAGE D'ACCUEIL : SCREENER DE MARCHÉ (V1.0)
# ==============================================================================

import streamlit as st
import pandas as pd
import requests
import time

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Screener de Marché BRVM",
    page_icon="📈",
    layout="wide"
)

# --- Variables Globales ---
API_URL = "https://brvm-api-gateway.onrender.com"

# --- Fonctions Communes ---
@st.cache_data(ttl=300) # Cache de 5 minutes
def get_screener_data():
    """Récupère les données du screener depuis l'API."""
    try:
        response = requests.get(f"{API_URL}/screener/", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API pour charger les données du screener : {e}")
        return None

def color_signals(val):
    """Applique une couleur de fond en fonction du signal."""
    if isinstance(val, str):
        val_lower = val.lower()
        if 'achat' in val_lower:
            return 'background-color: #d4edda; color: #155724'  # Vert
        elif 'vente' in val_lower:
            return 'background-color: #f8d7da; color: #721c24'  # Rouge
        elif 'neutre' in val_lower:
            return 'background-color: #fff3cd; color: #856404'  # Jaune
    return ''

# --- Interface Utilisateur ---
st.title("📈 Screener de Marché BRVM")
st.markdown("Vue d'ensemble des signaux techniques pour toutes les sociétés cotées. Les données sont mises à jour quotidiennement.")

# Charger et afficher les données
screener_data = get_screener_data()

if screener_data:
    df = pd.DataFrame(screener_data)
    
    # Réorganiser et renommer les colonnes pour une meilleure lisibilité
    df = df.rename(columns={
        "symbol": "Symbole",
        "name": "Société",
        "last_price": "Dernier Cours (FCFA)",
        "signal_mm": "Moy. Mobiles",
        "signal_bollinger": "Bollinger",
        "signal_macd": "MACD",
        "signal_rsi": "RSI",
        "signal_stochastic": "Stochastique"
    })
    
    # Sélectionner l'ordre des colonnes
    display_columns = [
        "Symbole", "Société", "Dernier Cours (FCFA)", 
        "Moy. Mobiles", "Bollinger", "MACD", "RSI", "Stochastique"
    ]
    
    # Afficher le DataFrame avec le style
    st.dataframe(
        df[display_columns].style.apply(lambda col: col.map(color_signals), subset=['Moy. Mobiles', 'Bollinger', 'MACD', 'RSI', 'Stochastique']),
        use_container_width=True,
        height=800,
        hide_index=True
    )
    st.caption(f"{len(df)} sociétés analysées.")
else:
    st.warning("Impossible de charger les données du screener. L'API est peut-être en cours de démarrage. Veuillez réessayer dans un instant.")

st.markdown("---")
st.info("💡 Utilisez le menu de navigation à gauche pour accéder à l'analyse détaillée d'une société spécifique.")
