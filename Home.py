# ==============================================================================
# BRVM ANALYSIS DASHBOARD (V0.2 - DASHBOARD AMÉLIORÉ AVEC GRAPHIQUES ET ONGLETS)
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

# --- BARRE LATÉRALE (SIDEBAR) ---
st.sidebar.title("📈 Navigation")
st.sidebar.markdown("Sélectionnez une société pour afficher son analyse détaillée.")

companies = get_companies()

if companies:
    company_map = {comp['symbol']: comp['name'] for comp in companies}
    
    selected_symbol = st.sidebar.selectbox(
        label="Choisissez une société :",
        options=sorted(company_map.keys()),
        format_func=lambda symbol: f"{company_map[symbol]} ({symbol})"
    )
else:
    st.sidebar.warning("API non disponible.")
    selected_symbol = None


# --- PAGE PRINCIPALE ---
st.title("📊 Tableau de Bord d'Analyse - Marché BRVM")

if selected_symbol:
    with st.spinner(f"Chargement de l'analyse pour {selected_symbol}..."):
        analysis = get_analysis(selected_symbol)

    if analysis:
        st.header(f"Analyse pour {analysis.get('company_name', selected_symbol)}")
        st.caption(f"Dernières données du {analysis.get('last_trade_date', 'N/A')}")
        
        # --- GRAPHIQUE D'ÉVOLUTION DU COURS ---
        st.subheader("Évolution du Cours sur 50 Jours")
        price_data_df = pd.DataFrame(analysis.get('price_data', []))
        if not price_data_df.empty:
            price_data_df['trade_date'] = pd.to_datetime(price_data_df['trade_date'])
            price_data_df.set_index('trade_date', inplace=True)
            st.line_chart(price_data_df['price'])
        else:
            st.info("Données de prix non disponibles pour tracer le graphique.")

        st.markdown("---")

        # --- ONGLET D'ANALYSES ---
        tab1, tab2, tab3 = st.tabs(["💡 Synthèse IA", "📈 Analyse Technique Détaillée", "📄 Analyse Fondamentale"])

        with tab1:
            st.subheader("Synthèse Générale par l'IA")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(label="Dernier Cours", value=f"{analysis.get('last_price', 'N/A')} FCFA")
            
            # Ici, nous pourrions ajouter plus tard une conclusion générale de l'IA
            st.info("Cette section affichera bientôt une conclusion d'investissement globale générée par l'IA.")

        with tab2:
            st.subheader("Détails des Indicateurs Techniques")
            col1, col2 = st.columns([1, 2]) # Une colonne pour les données, une pour l'analyse

            with col1:
                tech_analysis_data = analysis.get('technical_analysis', {})
                if tech_analysis_data:
                    # Créer un DataFrame pour un affichage propre
                    df_tech = pd.DataFrame.from_dict(tech_analysis_data, orient='index', columns=['Valeur / Signal'])
                    st.dataframe(df_tech)
                else:
                    st.info("Données techniques non disponibles.")
            
            with col2:
                st.markdown("**Analyse des signaux par l'IA :**")
                # Ici, nous pourrions appeler l'IA pour analyser les signaux
                st.write("L'analyse textuelle des indicateurs techniques sera ajoutée ici.")


        with tab3:
            st.subheader("Synthèse des Derniers Rapports Financiers")
            fundamental_text = analysis.get('fundamental_analysis', "Aucune donnée.")
            st.markdown(fundamental_text if fundamental_text else "Aucune analyse fondamentale disponible.")

else:
    st.warning("Impossible de charger la liste des sociétés. Le service API est peut-être momentanément indisponible.")

# --- Pied de page ---
st.markdown("---")
st.info("Cette application est alimentée par l'API Gateway BRVM, connectée à une base de données d'analyses financières.")
