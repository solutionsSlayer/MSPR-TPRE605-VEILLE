@echo off
echo ===== Configuration de l'environnement pour le projet de veille cryptographie quantique =====

:: Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installé ou n'est pas accessible depuis la ligne de commande.
    echo Veuillez installer Python 3.10 ou supérieur avant de continuer.
    exit /b 1
)

:: Créer l'environnement virtuel s'il n'existe pas
if not exist venv\ (
    echo Création de l'environnement virtuel...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Erreur lors de la création de l'environnement virtuel.
        exit /b 1
    )
) else (
    echo L'environnement virtuel existe déjà.
)

:: Activer l'environnement virtuel et installer les dépendances
echo Activation de l'environnement virtuel et installation des dépendances...
call venv\Scripts\activate.bat

:: Mettre à jour pip
python -m pip install --upgrade pip

:: Installer les dépendances principales
echo Installation des packages principaux...
pip install -r requirements.txt

:: Télécharger les ressources NLTK nécessaires
echo Téléchargement des ressources NLTK...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

:: Télécharger les modèles spaCy
echo Téléchargement des modèles spaCy...
python -m spacy download fr_core_news_sm

:: Créer les dossiers nécessaires
if not exist data\ mkdir data
if not exist analysis_results\ mkdir analysis_results
if not exist podcasts\ mkdir podcasts

:: Vérifier le fichier .env
if not exist .env (
    copy .env.template .env
    echo Fichier .env créé à partir du template. Veuillez le modifier avec vos clés API.
)

echo.
echo ===== Configuration terminée avec succès ! =====
echo.
echo Pour activer l'environnement virtuel:
echo   call venv\Scripts\activate.bat
echo.
echo Pour désactiver l'environnement virtuel:
echo   deactivate
echo.
echo Pour exécuter le projet:
echo   python main.py --run-once --tasks all
echo.

:: Laisser l'environnement virtuel activé
