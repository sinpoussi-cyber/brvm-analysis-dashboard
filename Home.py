# ==============================================================================
# BRVM ANALYSIS DASHBOARD (V0.2 - AVEC GRAPHIQUES)
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Tableau de Bord BRVM",
    page_icon="📊",
    layout="wide"
)

# --- Variables Globales ---
API_URL = "https://brvm-api-gateway.onrender.com"

# --- Fonctions de l'Application ---

@st.cache_data(ttl=3600)
def get_companies():
    """Récupère la liste des sociétés depuis l'API."""
    try:
        response = requests.get(f"{API_URL}/companies/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API pour charger les sociétés : {e}")
        return []

@st.cache_data(ttl=600)
def get_analysis(symbol):
    """Récupère l'analyse complète pour un symbole donné."""
    if not symbol:
        return None
    try:
        response = requests.get(f"{API_URL}/analysis/{symbol}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Impossible de récupérer l'analyse pour {symbol} : {e}")
        return None

# --- Interface Utilisateur ---

st.title("📊 Tableau de Bord d'Analyse - Marché BRVM")
st.markdown("Bienvenue sur votre tableau de bord personnel pour l'analyse des sociétés de la Bourse Régionale des Valeurs Mobilières.")

companies = get_companies()

if companies:
    company_map = {comp['symbol']: comp['name'] for comp in companies}
    
    selected_symbol = st.selectbox(
        label="Choisissez une société à analyser :",
        options=sorted(company_map.keys()),
        format_func=lambda symbol: f"{company_map[symbol]} ({symbol})"
    )

    if selected_symbol:
        st.markdown("---")
        
        with st.spinner(f"Chargement de l'analyse pour {selected_symbol}..."):
            analysis = get_analysis(selected_symbol)

        if analysis:
            st.header(f"Analyse pour {analysis.get('company_name', selected_symbol)}")
            st.caption(f"Dernières données disponibles du {analysis.get('last_trade_date', 'N/A')}")

            st.metric(label="Dernier Cours de Clôture", value=f"{analysis.get('last_price', 'N/A')} FCFA")

            # --- NOUVEAU : GRAPHIQUE INTERACTIF ---
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


            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Synthèse Technique")
                tech_analysis = analysis.get('technical_analysis', {})
                if tech_analysis:
                    st.write(f"**Moyennes Mobiles :** {tech_analysis.get('mm_decision', 'N/A')}")
                    st.write(f"**Bandes de Bollinger :** {tech_analysis.get('bollinger_decision', 'N/A')}")
                    st.write(f"**MACD :** {tech_analysis.get('macd_decision', 'N/A')}")
                    st.write(f"**RSI :** {tech_analysis.get('rsi_decision', 'N/A')}")
                    st.write(f"**Stochastique :** {tech_analysis.get('stochastic_decision', 'N/A')}")
                else:
                    st.info("Aucune donnée d'analyse technique disponible.")

            with col2:
                st.subheader("Synthèse Fondamentale")
                fundamental_text = analysis.get('fundamental_analysis', "Aucune donnée.")
                st.markdown(fundamental_text if fundamental_text else "Aucune analyse fondamentale disponible.")
else:
    st.warning("Impossible de charger la liste des sociétés depuis l'API. Le service est peut-être momentanément indisponible.")

st.markdown("---")
st.info("Cette application est alimentée par l'API BRVM Analysis Gateway. Les données sont fournies à titre indicatif.")
