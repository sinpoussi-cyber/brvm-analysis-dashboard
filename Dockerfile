# syntax=docker/dockerfile:1

# Étape 1: Utiliser une image de base Python officielle et légère
FROM python:3.11-slim

# Étape 2: Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3: Copier le fichier des dépendances
COPY requirements.txt ./

# Étape 4: Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5: Copier tout le reste du code de l'application
COPY . .

# Étape 6: Exposer le port que Streamlit utilisera (8501 est le port standard)
EXPOSE 8501

# Étape 7: La commande pour lancer l'application avec le NOM DE FICHIER CORRECT
CMD ["streamlit", "run", "1_📈_Screener_de_Marché.py", "--server.port=8501", "--server.address=0.0.0.0"]
