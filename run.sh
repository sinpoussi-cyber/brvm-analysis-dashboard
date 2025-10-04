#!/bin/bash

# Mettre à jour pip et installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Lancer l'application Streamlit
streamlit run Home.py --server.port $PORT --server.address 0.0.0.0
