# Système de Veille Technologique sur la Cryptographie Quantique

Ce projet implémente un système automatisé de veille technologique spécialisé dans le domaine de la cryptographie quantique. Il collecte, analyse et diffuse des informations pertinentes via un bot Telegram et génère des podcasts synthétisés par IA.

## Fonctionnalités

- **Collecte de données** depuis diverses sources (articles scientifiques, actualités, conférences)
- **Analyse et classification** des informations collectées
- **Extraction de tendances** et identification des sujets émergents
- **Diffusion via bot Telegram** avec commandes interactives
- **Génération de podcasts** avec synthèse vocale IA
- **Système automatisé** avec planification des tâches

## Architecture du Système

Le système de veille technologique suit un flux de travail en quatre étapes principales :

### 1. Collecte des données

Le module `QuantumCryptoScraper` collecte des informations depuis diverses sources :

- **Flux RSS** : Articles du Web via les flux RSS de sites spécialisés
- **arXiv** : Articles scientifiques via l'API arXiv
- **Sites Web** : Articles spécialisés par web scraping

Les données sont filtrées selon leur pertinence pour la cryptographie quantique et stockées dans des fichiers CSV et JSON dans le dossier `data/current/`.

### 2. Analyse des données

Le module `QuantumCryptoAnalyzer` traite les données collectées pour en extraire des informations pertinentes :

- **Clustering** : Regroupe les articles similaires (stockés dans `clusters/`)
- **Extraction d'entités** : Identifie les organisations, personnes et lieux mentionnés (stockés dans `entities/`)
- **Génération de visualisations** : Crée des nuages de mots et graphiques de tendances (stockés dans `visualizations/`)
- **Insights IA** : Génère des analyses et synthèses grâce à l'API OpenAI (stockées dans `reports/`)

### 3. Génération de Podcasts

Le module `QuantumCryptoPodcast` transforme les analyses en contenu audio :

- Génération de scripts structurés à partir des analyses
- Synthèse vocale via l'API ElevenLabs ou OpenAI
- Production de fichiers MP3 avec introduction, corps et conclusion

### 4. Diffusion

Le module `QuantumCryptoBot` diffuse les informations via Telegram :

- Commandes interactives pour accéder aux analyses
- Notifications automatiques pour les nouveaux contenus
- Abonnement aux mises à jour quotidiennes

## Structure des dossiers

Le projet utilise une architecture modulaire organisée dans les dossiers suivants :

```
quantum-crypto-veille/
├── data/                      # Données collectées
│   ├── current/            # Données actuellement utilisées
│   └── archives/           # Données archivées (plus anciennes)
├── analysis_results/          # Résultats d'analyse
│   ├── clusters/           # Résultats du clustering des articles
│   ├── entities/           # Entités extraites des textes
│   ├── reports/            # Rapports complets et insights générés par IA
│   ├── visualizations/     # Nuages de mots et graphiques de tendances
│   ├── daily/              # Résumés et analyses quotidiennes
│   ├── weekly/             # Résumés et analyses hebdomadaires
│   └── monthly/            # Résumés et analyses mensuelles
├── podcasts/                  # Podcasts générés
│   ├── weekly/             # Podcasts hebdomadaires
│   └── monthly/            # Podcasts mensuels
├── src/
│   ├── collectors/          # Modules de collecte de données
│   ├── analyzers/           # Modules d'analyse
│   ├── distributors/        # Modules de diffusion
│   ├── podcast/             # Génération de podcast
│   └── utils/               # Utilitaires (logger, gestion de fichiers)
├── logs/                      # Fichiers de logs
└── tools/                     # Scripts et outils utilitaires
```

## Installation

### Méthode automatisée (recommandée)

1. Cloner le dépôt :
```bash
git clone https://github.com/your-username/quantum-crypto-veille.git
cd quantum-crypto-veille
```

2. Exécuter le script de configuration :

**Sur Windows :**
```bash
setup.bat
```

**Sur Linux/Mac :**
```bash
chmod +x setup.sh
./setup.sh
```

Ce script crée automatiquement un environnement virtuel, installe toutes les dépendances, télécharge les modèles nécessaires et prépare le fichier `.env`.

3. Activer l'environnement virtuel si ce n'est pas déjà fait :

**Sur Windows :**
```bash
venv\Scripts\activate
```

**Sur Linux/Mac :**
```bash
source venv/bin/activate
```

4. Modifier le fichier `.env` avec vos clés API.

### Méthode manuelle

1. Cloner le dépôt :
```bash
git clone https://github.com/your-username/quantum-crypto-veille.git
cd quantum-crypto-veille
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Télécharger les modèles nécessaires :
```bash
python -m nltk.downloader punkt stopwords
python -m spacy download fr_core_news_sm
```

5. Configurer les variables d'environnement :
```bash
cp .env.template .env
# Modifier le fichier .env avec vos clés API
```

## Configuration du Bot Telegram

1. Créer un bot Telegram via [@BotFather](https://t.me/botfather)
2. Obtenir le token du bot et l'ajouter dans le fichier `.env`

## Utilisation

### Exécuter le script de test (recommandé pour débuter)

Ce script vous permet de tester facilement les différents composants du système :

```bash
# Tester tous les composants
python run_tests.py

# Tester un composant spécifique
python run_tests.py --component collector  # Teste uniquement le collecteur de données
python run_tests.py --component analyzer   # Teste uniquement l'analyseur
python run_tests.py --component podcast    # Teste uniquement la génération de podcast
python run_tests.py --component telegram   # Teste uniquement la configuration du bot Telegram

# Mode verbeux pour plus de détails
python run_tests.py --verbose
```

### Exécuter le système complet (avec planification) :

```bash
python main.py
```

### Exécuter des tâches spécifiques :

```bash
# Collecte et analyse uniquement
python main.py --run-once --tasks collect analyze

# Génération de podcast uniquement
python main.py --run-once --tasks podcast

# Démarrer le bot Telegram uniquement
python main.py --run-once --tasks telegram

# Vérifier la configuration sans exécuter de tâches
python main.py --check-config
```

## Accès aux Résultats d'Analyse

Les résultats d'analyse sont organisés dans des sous-dossiers spécifiques pour une meilleure navigation :

### Visualisations (`analysis_results/visualizations/`)

- **Nuages de mots** : Fichiers `wordcloud_*.png` représentant les termes les plus fréquents
- **Graphiques de tendances** : Fichiers `trends_*.png` montrant l'évolution temporelle des articles
- **Données de tendances** : Fichiers `trends_data_*.json` contenant les données brutes des tendances

### Clustering (`analysis_results/clusters/`)

- Fichiers `clusters_*.json` contenant les groupes d'articles similaires et leurs termes représentatifs

### Entités (`analysis_results/entities/`)

- Fichiers `entities_*.json` listant les organisations, personnes et lieux mentionnés
- Fichier `topics.csv` recensant les thèmes principaux identifiés

### Rapports (`analysis_results/reports/`)

- **Rapports complets** : Fichiers `rapport_complet_*.txt` synthétisant toutes les analyses
- **Insights IA** : Fichiers `ai_insights_*.txt` générés par l'IA sur les tendances observées

### Analyses temporelles

- **Analyses quotidiennes** : Dossier `daily/` contenant les digests journaliers
- **Analyses hebdomadaires** : Dossier `weekly/` pour les synthèses de la semaine
- **Analyses mensuelles** : Dossier `monthly/` pour les rapports mensuels

## Configuration des API Externes

Le système utilise plusieurs API externes qui doivent être configurées dans le fichier `.env` :

```
# API Keys
OPENAI_API_KEY=your_openai_api_key_here       # Pour la génération d'insights IA
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here  # Pour la synthèse vocale de haute qualité

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here  # Pour la diffusion via Telegram

# Autres configurations
PODCAST_FREQUENCY=weekly  # daily, weekly, monthly
LANGUAGE=fr  # fr, en
```

Pour obtenir ces clés :

1. **OpenAI API** : Inscrivez-vous sur [OpenAI Platform](https://platform.openai.com/)
2. **ElevenLabs API** : Créez un compte sur [ElevenLabs](https://elevenlabs.io/)
3. **Telegram Bot** : Créez un bot via [@BotFather](https://t.me/botfather) sur Telegram

## Commandes du Bot Telegram

Le bot Telegram offre une interface conviviale pour accéder aux résultats de veille :

- `/start` - Démarrer le bot et afficher le menu principal
- `/help` - Afficher l'aide avec toutes les commandes disponibles
- `/subscribe` - S'abonner aux mises à jour quotidiennes
- `/unsubscribe` - Se désabonner des notifications
- `/latest` - Afficher les 5 dernières publications collectées
- `/summary` - Obtenir un résumé des tendances récentes
- `/topics` - Voir les sujets principaux identifiés par l'analyse
- `/sources` - Voir les sources les plus actives et leur nombre de publications

## Personnalisation et Extension

### Ajouter de Nouvelles Sources

Pour ajouter de nouvelles sources de données, modifiez la méthode `_load_sources()` dans la classe `QuantumCryptoScraper` :

```python
def _load_sources(self):
    """Charge les sources depuis un fichier de configuration"""
    sources = {
        "rss_feeds": [
            # Ajouter vos nouveaux flux RSS ici
            {"name": "Nouveau Site", "url": "https://example.com/feed/"},
        ],
        "scientific_keywords": [
            # Ajouter vos nouveaux mots-clés de recherche ici
            "nouveau terme de recherche",
        ],
        "news_sites": [
            # Ajouter vos nouveaux sites d'actualités ici
            {"name": "Nouveau Site Web", "url": "https://example.com/category/quantum/", "selector": "article"},
        ]
    }
    return sources
```

### Personnalisation de la Voix du Podcast

Modifiez les paramètres dans le fichier `src/podcast/podcast_generator.py` pour personnaliser la voix et le style du podcast :

```python
# Format du podcast
self.podcast_format = {
    "intro_duration": 30,  # secondes
    "body_duration": 300,  # 5 minutes
    "outro_duration": 20,  # secondes
    "voice_id": "EXAVITQu4vr4xnSDxMaL"  # ID de voix ElevenLabs (à remplacer)
}
```

## Maintenance et Dépannage

### Fichiers de Logs

Les logs du système sont stockés dans le dossier `logs/` avec un format `YYYYMMDD_HHMMSS_quantum_veille.log`. Ils contiennent des informations détaillées sur chaque exécution du système.

### Erreurs Courantes

#### Problèmes d'API

Si vous rencontrez des erreurs liées aux API externes :

1. Vérifiez que vos clés API sont correctement configurées dans le fichier `.env`
2. Assurez-vous que vous n'avez pas atteint les limites d'utilisation des API
3. Vérifiez la connectivité réseau

#### Erreurs lors de l'analyse

Les erreurs lors de l'analyse peuvent être causées par :

1. Des données mal formatées dans les sources
2. Un manque de mémoire pour les opérations intensives
3. Des dépendances manquantes ou incompatibles

### Organisation des Fichiers

Si vous avez besoin de réorganiser manuellement les fichiers dans les sous-dossiers appropriés, vous pouvez utiliser le script `organize_files.py` :

```bash
python organize_files.py
```

Ce script déplacera tous les fichiers d'analyse dans leurs dossiers respectifs en fonction de leur type.

## Technologies Utilisées

Ce projet s'appuie sur une combinaison de technologies de pointe pour la collecte, l'analyse et la diffusion d'informations :

### Langage et Base
- **Python 3.10+** - Langage principal de développement

### Collecte de Données
- **BeautifulSoup 4** - Analyse HTML pour le web scraping
- **Requests** - Requêtes HTTP pour l'accès aux API et sites web
- **feedparser** - Analyse des flux RSS
- **arxiv** - API client pour accéder aux papers scientifiques

### Analyse et Traitement
- **Pandas** - Manipulation et analyse de données structurées
- **scikit-learn** - Techniques d'apprentissage automatique (clustering, vectorisation)
- **NLTK** - Outils de traitement du langage naturel
- **spaCy** - Extraction d'entités nommées et analyse linguistique
- **matplotlib & seaborn** - Création de visualisations et graphiques
- **wordcloud** - Génération de nuages de mots

### Intégration IA
- **OpenAI API** - Génération de contenu et résumés avec GPT-4

### Diffusion
- **python-telegram-bot** - Interface pour le bot Telegram
- **ElevenLabs API** - Synthèse vocale de haute qualité
- **pydub** - Manipulation et édition audio

### Automatisation
- **schedule** - Planification des tâches récurrentes
- **python-dotenv** - Gestion des variables d'environnement

## Contributions

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. **Fork du dépôt** sur GitHub
2. **Créez une branche** pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. **Committez vos changements** (`git commit -m 'Add some amazing feature'`)
4. **Poussez sur la branche** (`git push origin feature/amazing-feature`)
5. **Ouvrez une Pull Request**

Améliorations prioritaires :

- Amélioration des algorithmes de clustering
- Ajout de nouvelles sources de données
- Optimisation des performances
- Traduction et support multilingue
- Amélioration de l'interface Telegram

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
