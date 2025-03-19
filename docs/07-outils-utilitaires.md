# Outils et Scripts Utilitaires

## Présentation générale

Le système de veille sur la cryptographie quantique inclut plusieurs outils et scripts utilitaires qui permettent de gérer, maintenir et améliorer le fonctionnement du système. Ces outils sont principalement situés dans le dossier `tools/` et le module `src/utils/`.

## Module de journalisation (Logger)

Le module de journalisation (`src/utils/logger.py`) fournit un système avancé pour enregistrer les événements et les erreurs du système.

### Classe QuantumVeilleLogger

La classe `QuantumVeilleLogger` implémente un système de journalisation personnalisé :

```python
class QuantumVeilleLogger:
    """
    Gestionnaire de logs avancé pour le système de veille.
    Crée des fichiers de logs avec une nomenclature par date et heure.
    """
    
    def __init__(self, log_level=logging.INFO):
        """Initialise le gestionnaire de logs"""
        self.logger = logging.getLogger("quantum_veille")
        self.logger.setLevel(log_level)
        
        # Créer le dossier logs s'il n'existe pas
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Formateur de logs
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(module)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler pour le fichier de log avec nomenclature temporelle
        self.current_log_file = self._create_log_file()
        file_handler = logging.FileHandler(self.current_log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
```

### Méthodes de journalisation spécialisées

Le logger offre plusieurs méthodes spécialisées pour les différentes parties du système :

```python
def log_exception(self, e, context=""):
    """Enregistre une exception avec ses détails complets"""
    error_msg = f"{context}: {str(e)}" if context else str(e)
    self.logger.error(error_msg)
    
    # Enregistrer la trace complète
    tb = traceback.format_exc()
    self.logger.debug(f"Traceback complète: {tb}")

def log_api_error(self, service_name, error_details):
    """Enregistre une erreur d'API externe de manière structurée"""
    self.logger.error(f"Erreur API {service_name}: {error_details}")

def log_stage_start(self, stage_name):
    """Enregistre le début d'une étape du pipeline"""
    self.logger.info(f"DÉBUT ÉTAPE: {stage_name} {'='*40}")

def log_stage_end(self, stage_name, success=True):
    """Enregistre la fin d'une étape du pipeline"""
    status = "RÉUSSIE" if success else "ÉCHOUÉE"
    self.logger.info(f"FIN ÉTAPE: {stage_name} - {status} {'='*40}")

def log_data_stats(self, stats_dict):
    """Enregistre des statistiques sur les données collectées/analysées"""
    self.logger.info("Statistiques des données:")
    for key, value in stats_dict.items():
        self.logger.info(f"  - {key}: {value}")

def log_config_status(self):
    """Vérifie et enregistre l'état des configurations principales"""
    self.logger.info("Vérification des configurations:")
    
    # Vérifier les dossiers
    for folder in ["data", "analysis_results", "podcasts"]:
        status = "✓" if os.path.isdir(folder) else "✗"
        self.logger.info(f"  - Dossier {folder}: {status}")
    
    # Vérifier les clés API
    # ...
```

## Outil de gestion des fichiers

L'outil de gestion des fichiers (`tools/file_manager_tool.py`) permet de gérer manuellement les fichiers du système.

### Commandes disponibles

```
python tools/file_manager_tool.py info         # Afficher des informations sur les fichiers
python tools/file_manager_tool.py archive      # Archiver les anciennes données
python tools/file_manager_tool.py rebuild      # Reconstruire l'index
python tools/file_manager_tool.py search KEYWORD  # Rechercher des fichiers par mot-clé
python tools/file_manager_tool.py organize     # Organiser les fichiers selon la nouvelle structure
python tools/file_manager_tool.py cleanup      # Nettoyer les fichiers temporaires et duplicats
```

### Exemple de la commande info

```python
def display_info(file_manager):
    """Affiche des informations sur les fichiers"""
    stats = file_manager.get_stats()
    
    print("\n=== Informations sur les fichiers ===\n")
    print(f"Nombre total de fichiers de données: {stats['total_data_files']}")
    print(f"  - Fichiers courants: {stats['current_data_files']}")
    print(f"  - Fichiers archivés: {stats['archived_data_files']}")
    print(f"\nNombre total de résultats d'analyse: {stats['total_analysis_results']}")
    print(f"Nombre total de podcasts: {stats['total_podcasts']}")
    
    print("\nDernières analyses:")
    print(f"  - Dernier digest quotidien: {stats['analysis_metrics']['last_daily_digest'] or 'Aucun'}")
    print(f"  - Dernier résumé hebdomadaire: {stats['analysis_metrics']['last_weekly_summary'] or 'Aucun'}")
    print(f"  - Dernier rapport mensuel: {stats['analysis_metrics']['last_monthly_report'] or 'Aucun'}")
    
    print(f"\nDernière mise à jour de l'index: {stats['last_update']}")
```

## Script de mise à jour du système

Le script de mise à jour (`tools/update_files.py`) permet d'appliquer des modifications au système, comme l'intégration du gestionnaire de fichiers :

```python
def update_main_py():
    """Met à jour le fichier main.py pour utiliser le nouveau gestionnaire de fichiers"""
    # Créer une copie de sauvegarde
    backup_path = os.path.join(base_path, f"main.py.backup.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(main_py_path, backup_path)
    
    # Lire le contenu du fichier
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Appliquer les modifications
    # ...
    
    # Écrire le contenu modifié
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
```

## Script de test du système

Le script de test (`run_tests.py`) permet de tester les différents composants du système de manière indépendante :

```python
def main():
    """Fonction principale qui gère les différents tests"""
    
    parser = argparse.ArgumentParser(description="Tests du système de veille cryptographie quantique")
    parser.add_argument("--component", choices=["collector", "analyzer", "telegram", "podcast", "all"],
                        default="all", help="Composant à tester")
    parser.add_argument("--verbose", action="store_true", help="Afficher les informations détaillées")
    
    args = parser.parse_args()
    
    # Tester les composants sélectionnés
    if args.component in ["collector", "all"]:
        test_collector(args.verbose)
    
    if args.component in ["analyzer", "all"]:
        test_analyzer(args.verbose)
    
    if args.component in ["podcast", "all"]:
        test_podcast(args.verbose)
    
    if args.component in ["telegram", "all"]:
        test_telegram(args.verbose)
```

### Exemples de tests

Le script implémente plusieurs fonctions de test pour les différents composants :

```python
def test_collector(verbose=False):
    """Teste le collecteur de données"""
    print("\n----- Test du collecteur de données -----")
    
    try:
        from collectors.quantum_crypto_scraper import QuantumCryptoScraper
        
        scraper = QuantumCryptoScraper()
        csv_path, json_path = scraper.fetch_all_sources()
        
        print(f"[OK] Collecte terminée")
        print(f"[OK] Données sauvegardées dans:")
        print(f"   - {csv_path}")
        print(f"   - {json_path}")
        
        # Afficher un échantillon des données si verbose
        if verbose:
            # ...
        
        return json_path
    
    except Exception as e:
        print(f"[ERREUR] lors du test du collecteur: {str(e)}")
        return None
```

## Scripts d'installation

Le système inclut des scripts d'installation pour Windows (`setup.bat`) et Linux/Mac (`setup.sh`) qui facilitent la configuration initiale du projet :

```bash
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
```

## Autres utilitaires

Le système comprend également d'autres utilitaires moins visibles mais tout aussi importants :

### Fonctions d'initialisation de l'environnement

Dans `main.py`, des fonctions préparent l'environnement Python pour charger correctement les modules du projet :

```python
# Ajouter les répertoires source au chemin Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/collectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/analyzers'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/distributors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/podcast'))
```

### Fichier .env.template

Le fichier `.env.template` fournit un modèle pour configurer les variables d'environnement nécessaires :

```
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Autres configurations
PODCAST_FREQUENCY=weekly  # daily, weekly, monthly
LANGUAGE=fr  # fr, en
```

### Fichier .gitignore

Le fichier `.gitignore` spécifie les fichiers à exclure du référentiel Git :

```
# Environnement Python
venv/
__pycache__/
*.py[cod]

# Données et résultats
data/*.csv
data/*.json
analysis_results/*.json
analysis_results/*.png
analysis_results/*.txt
podcasts/*.mp3
podcasts/*.txt

# Logs
logs/
*.log

# Variables d'environnement
.env

# Fichiers temporaires
*.tmp
```

## Les arguments de ligne de commande

Le script principal (`main.py`) prend en charge plusieurs arguments en ligne de commande pour contrôler son comportement :

```python
parser = argparse.ArgumentParser(description="Système de veille technologique sur la cryptographie quantique")

parser.add_argument("--run-once", action="store_true", help="Exécuter une seule fois puis terminer")
parser.add_argument("--tasks", nargs="+", default=["all"], 
                    choices=["collect", "analyze", "podcast", "telegram", "all"],
                    help="Tâches à exécuter (collect, analyze, podcast, telegram, all)")
parser.add_argument("--check-config", action="store_true", help="Vérifier la configuration uniquement, sans exécuter")
```

Exemples d'utilisation :

```bash
# Exécuter toutes les tâches une seule fois
python main.py --run-once --tasks all

# Vérifier la configuration
python main.py --check-config

# Exécuter uniquement la collecte et l'analyse
python main.py --run-once --tasks collect analyze
```

## Planification des tâches

Le système utilise la bibliothèque `schedule` pour gérer les tâches planifiées :

```python
def schedule_tasks(self):
    """Configure les tâches planifiées"""
    logger.info("Setting up scheduled tasks")
    
    # Exécuter la veille tous les jours à 3h du matin
    schedule.every().day.at("03:00").do(self.run_full_pipeline)
    
    # Exécuter immédiatement au démarrage
    self.run_full_pipeline()
    
    # Démarrer le bot Telegram
    self.start_telegram_bot()
    
    # Boucle principale
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Attendre 1 minute entre les vérifications
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
```

## Utilitaires et bonnes pratiques

Le système implémente plusieurs bonnes pratiques et utilitaires courants :

1. **Gestion des exceptions** : Capture et journalisation des erreurs à tous les niveaux
2. **Documentation du code** : Docstrings détaillées pour les classes et méthodes
3. **Séparation des préoccupations** : Modules indépendants avec des responsabilités clairement définies
4. **Configuration externalitée** : Variables d'environnement et fichiers de configuration
5. **Journalisation structurée** : Système de logs organisé et informatif
6. **Tests unitaires et d'intégration** : Scripts dédiés pour tester les composants
7. **Sauvegarde automatique** : Création de copies de sauvegarde avant les modifications importantes
