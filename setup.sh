#!/bin/bash

echo "===== Configuration de l'environnement pour le projet de veille cryptographie quantique ====="

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python n'est pas installé ou n'est pas accessible depuis la ligne de commande."
    echo "Veuillez installer Python 3.10 ou supérieur avant de continuer."
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Erreur lors de la création de l'environnement virtuel."
        exit 1
    fi
else
    echo "L'environnement virtuel existe déjà."
fi

# Activer l'environnement virtuel et installer les dépendances
echo "Activation de l'environnement virtuel et installation des dépendances..."
source venv/bin/activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances principales
echo "Installation des packages principaux..."
pip install -r requirements.txt

# Télécharger les ressources NLTK nécessaires
echo "Téléchargement des ressources NLTK..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Télécharger les modèles spaCy
echo "Téléchargement des modèles spaCy..."
python -m spacy download fr_core_news_sm

# Créer les dossiers nécessaires
mkdir -p data
mkdir -p analysis_results
mkdir -p podcasts

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "Fichier .env créé à partir du template. Veuillez le modifier avec vos clés API."
fi

echo
echo "===== Configuration terminée avec succès ! ====="
echo
echo "Pour activer l'environnement virtuel:"
echo "  source venv/bin/activate"
echo
echo "Pour désactiver l'environnement virtuel:"
echo "  deactivate"
echo
echo "Pour exécuter le projet:"
echo "  python main.py --run-once --tasks all"
echo

# Laisser l'environnement virtuel activé
