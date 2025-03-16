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

```
[Sources] → [Collecte] → [Traitement] → [Diffusion]
   ↓             ↓            ↓             ↓
Articles      Scrapers     NLP/LLM      Telegram
Brevets       API          Synthèse     Podcast
Preprints     RSS          Classification
Conférences
```

## Structure du Projet

```
quantum-crypto-veille/
├── data/                       # Données collectées
├── analysis_results/           # Résultats d'analyse
├── podcasts/                   # Podcasts générés
├── src/
│   ├── collectors/             # Modules de collecte de données
│   │   └── quantum_crypto_scraper.py
│   ├── analyzers/              # Modules d'analyse
│   │   └── quantum_crypto_analyzer.py
│   ├── distributors/           # Modules de diffusion
│   │   └── telegram_bot.py
│   └── podcast/                # Génération de podcast
│       └── podcast_generator.py
├── main.py                     # Script principal
├── requirements.txt            # Dépendances
└── .env.template               # Template pour les variables d'environnement
```

## Installation

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

### Exécuter le système complet (avec planification) :

```bash
python main.py
```

### Exécuter des tâches spécifiques :

```bash
python main.py --run-once --tasks collect analyze  # Collecte et analyse uniquement
python main.py --run-once --tasks podcast          # Génération de podcast uniquement
python main.py --run-once --tasks telegram         # Démarrer le bot Telegram uniquement
```

## Commandes du Bot Telegram

- `/start` - Démarrer le bot
- `/help` - Afficher l'aide
- `/subscribe` - S'abonner aux mises à jour
- `/unsubscribe` - Se désabonner
- `/latest` - Afficher les dernières publications
- `/summary` - Obtenir un résumé des tendances
- `/topics` - Voir les sujets principaux
- `/sources` - Voir les sources les plus actives

## Configurer de Nouvelles Sources

Pour ajouter de nouvelles sources de données, modifiez la méthode `_load_sources()` dans la classe `QuantumCryptoScraper`.

## Personnalisation de la Voix du Podcast

Modifiez les paramètres dans le fichier `podcast_generator.py` pour personnaliser la voix et le style du podcast.

## Technologies Utilisées

- **Python** - Langage principal
- **BeautifulSoup & Requests** - Web scraping
- **Pandas & scikit-learn** - Analyse de données
- **NLTK & spaCy** - Traitement du langage naturel
- **OpenAI API** - Génération de contenu et synthèse
- **ElevenLabs API** - Synthèse vocale de haute qualité
- **python-telegram-bot** - Interface Telegram
- **pydub** - Manipulation audio
- **matplotlib & seaborn** - Visualisations

## Contributions

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Fork du dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commit de vos changements (`git commit -m 'Add some amazing feature'`)
4. Push sur la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
