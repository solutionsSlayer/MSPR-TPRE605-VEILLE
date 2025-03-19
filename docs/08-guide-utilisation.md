# Guide d'Utilisation

## Installation du système

### Prérequis

Avant d'installer le système de veille sur la cryptographie quantique, assurez-vous que votre environnement répond aux prérequis suivants :

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (pour cloner le dépôt)
- ffmpeg (pour la génération de podcasts)

### Installation automatisée

Le système offre des scripts d'installation automatisée pour Windows et Linux/Mac.

#### Sur Windows

1. Clonez le dépôt :
   ```
   git clone https://github.com/your-username/quantum-crypto-veille.git
   cd quantum-crypto-veille
   ```

2. Exécutez le script d'installation :
   ```
   setup.bat
   ```

3. Activez l'environnement virtuel si ce n'est pas déjà fait :
   ```
   venv\Scripts\activate
   ```

4. Modifiez le fichier `.env` avec vos clés API.

#### Sur Linux/Mac

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/your-username/quantum-crypto-veille.git
   cd quantum-crypto-veille
   ```

2. Rendez le script d'installation exécutable puis lancez-le :
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Activez l'environnement virtuel si ce n'est pas déjà fait :
   ```bash
   source venv/bin/activate
   ```

4. Modifiez le fichier `.env` avec vos clés API.

### Configuration des API

Le système utilise plusieurs API externes qui nécessitent des clés d'accès :

1. **OpenAI API** : pour la génération de contenus et l'analyse
   - Créez un compte sur [OpenAI](https://platform.openai.com/)
   - Obtenez une clé API dans la section "API Keys"
   - Ajoutez-la dans `.env` : `OPENAI_API_KEY=votre_clé_ici`

2. **ElevenLabs API** : pour la synthèse vocale de haute qualité
   - Créez un compte sur [ElevenLabs](https://elevenlabs.io/)
   - Obtenez une clé API dans la section "Profile"
   - Ajoutez-la dans `.env` : `ELEVENLABS_API_KEY=votre_clé_ici`

3. **Telegram Bot Token** : pour le bot de diffusion
   - Créez un bot via [@BotFather](https://t.me/botfather) sur Telegram
   - Obtenez le token de votre bot
   - Ajoutez-le dans `.env` : `TELEGRAM_BOT_TOKEN=votre_token_ici`

## Exécution du système

### Test des composants

Avant de lancer le système complet, vous pouvez tester individuellement chaque composant à l'aide du script `run_tests.py` :

```bash
# Tester tous les composants
python run_tests.py

# Tester un composant spécifique avec des informations détaillées
python run_tests.py --component collector --verbose
python run_tests.py --component analyzer --verbose
python run_tests.py --component podcast --verbose
python run_tests.py --component telegram --verbose
```

### Vérification de la configuration

Vous pouvez vérifier que votre configuration est correcte sans exécuter le système :

```bash
python main.py --check-config
```

Cela affichera l'état de vos dossiers, fichiers et clés API.

### Exécution ponctuelle

Pour exécuter le système une seule fois sans planification :

```bash
# Exécuter toutes les tâches
python main.py --run-once --tasks all

# Exécuter seulement certaines tâches
python main.py --run-once --tasks collect analyze
python main.py --run-once --tasks podcast
python main.py --run-once --tasks telegram
```

### Exécution continue avec planification

Pour démarrer le système en mode continu avec planification des tâches :

```bash
python main.py
```

Cette commande va :
1. Exécuter immédiatement le pipeline complet
2. Planifier la collecte et l'analyse quotidienne à 3h du matin
3. Planifier la génération de podcasts les lundis
4. Démarrer le bot Telegram en arrière-plan

## Utilisation du bot Telegram

### Démarrage et inscription

1. Recherchez votre bot sur Telegram par son nom d'utilisateur (défini lors de sa création)
2. Envoyez la commande `/start` pour démarrer l'interaction avec le bot
3. Utilisez le bouton "S'abonner aux mises à jour" ou la commande `/subscribe` pour recevoir les notifications quotidiennes

### Commandes disponibles

Le bot répond aux commandes suivantes :

- `/help` - Affiche la liste des commandes disponibles
- `/subscribe` - S'abonne aux mises à jour quotidiennes
- `/unsubscribe` - Se désabonne des mises à jour
- `/latest` - Affiche les 5 dernières publications
- `/summary` - Affiche un résumé des tendances récentes
- `/topics` - Affiche les principaux sujets de discussion
- `/sources` - Affiche les sources les plus actives

### Notifications quotidiennes

Si vous êtes abonné, vous recevrez chaque jour à 9h du matin un résumé contenant :
- Les dernières recherches scientifiques
- Les dernières actualités
- Un lien vers le podcast le plus récent (si disponible)

## Gestion des fichiers

### Organisation des fichiers

Le système utilise une structure de fichiers organisée dans plusieurs dossiers :

```
data/
├── current/           # Données collectées récentes
├── archives/          # Données collectées plus anciennes
└── index.json         # Index central des fichiers

analysis_results/
├── daily/             # Analyses quotidiennes
├── weekly/            # Analyses hebdomadaires
└── monthly/           # Analyses mensuelles

podcasts/
├── weekly/            # Podcasts hebdomadaires
└── monthly/           # Podcasts mensuels

logs/                  # Journaux d'événements
```

### Outil de gestion des fichiers

Un outil en ligne de commande est disponible pour gérer les fichiers du système :

```bash
# Afficher des informations sur les fichiers
python tools/file_manager_tool.py info

# Archiver les données anciennes (plus de 30 jours par défaut)
python tools/file_manager_tool.py archive
python tools/file_manager_tool.py archive --days 60  # Pour les données de plus de 60 jours

# Rechercher des fichiers par mot-clé
python tools/file_manager_tool.py search quantum
python tools/file_manager_tool.py search "post-quantum"

# Organiser les fichiers selon la structure actuelle
python tools/file_manager_tool.py organize

# Nettoyer les fichiers temporaires et duplicats
python tools/file_manager_tool.py cleanup

# Reconstruire l'index en cas de corruption
python tools/file_manager_tool.py rebuild
```

## Accès aux podcasts

Les podcasts générés sont stockés dans le dossier `podcasts/` :

- `podcasts/weekly/` : Podcasts hebdomadaires
  - Scripts : `podcast_script_YYYYMMDD.txt`
  - Fichiers audio : `QuantumCrypto_Weekly_YYYYMMDD.mp3`

Pour écouter un podcast, vous pouvez :
1. Accéder directement au fichier MP3 sur le serveur
2. Utiliser le lien fourni dans les notifications Telegram
3. Configurer un serveur HTTP pour servir les fichiers (non inclus)

## Personnalisation du système

### Modification des sources de données

Pour ajouter ou modifier les sources de données collectées, éditez la méthode `_load_sources()` dans la classe `QuantumCryptoScraper` (`src/collectors/quantum_crypto_scraper.py`) :

```python
def _load_sources(self):
    """Charge les sources depuis un fichier de configuration"""
    sources = {
        "rss_feeds": [
            {"name": "Quantum Computing Report", "url": "https://quantumcomputingreport.com/feed/"},
            {"name": "Inside Quantum Technology", "url": "https://www.insidequantumtechnology.com/feed/"},
            # Ajoutez vos flux RSS ici
        ],
        "scientific_keywords": [
            "quantum cryptography", "quantum key distribution", 
            # Ajoutez vos mots-clés ici
        ],
        "news_sites": [
            {"name": "The Quantum Insider", "url": "https://thequantuminsider.com/category/quantum-cryptography/", "selector": "article"},
            # Ajoutez vos sites d'actualités ici
        ],
        "conferences": [
            "QCrypt", "PQCrypto", "Eurocrypt", "Crypto",
            # Ajoutez vos conférences ici
        ]
    }
    return sources
```

### Personnalisation de la voix du podcast

Pour personnaliser la voix utilisée pour les podcasts, modifiez les paramètres dans le fichier `podcast_generator.py` :

```python
self.podcast_format = {
    "intro_duration": 30,  # secondes
    "body_duration": 300,  # 5 minutes
    "outro_duration": 20,  # secondes
    "voice_id": "EXAVITQu4vr4xnSDxMaL"  # ID de voix ElevenLabs
}
```

Pour trouver des voice_id disponibles, utilisez la commande suivante avec votre clé API ElevenLabs :

```bash
curl -H "xi-api-key: YOUR_API_KEY" https://api.elevenlabs.io/v1/voices
```

### Modification de la planification

Pour modifier la planification des tâches, éditez la méthode `schedule_tasks()` dans `main.py` :

```python
def schedule_tasks(self):
    """Configure les tâches planifiées"""
    # Exécuter la veille tous les jours à 8h du matin
    schedule.every().day.at("08:00").do(self.run_full_pipeline)
    
    # Exécuter la génération de podcast tous les vendredis
    schedule.every().friday.at("12:00").do(self.generate_podcast)
    
    # ...
```

## Résolution des problèmes courants

### Messages d'erreur dans les logs

Consultez les fichiers de log dans le dossier `logs/` pour diagnostiquer les problèmes.

### Clés API expirées ou invalides

Vérifiez que vos clés API sont valides et mises à jour dans le fichier `.env`.

### Réinitialisation du système

Pour réinitialiser complètement le système en cas de problèmes graves :

1. Arrêtez le système (Ctrl+C si en cours d'exécution)
2. Supprimez les dossiers `data/`, `analysis_results/` et `podcasts/` (sauvegardez-les si nécessaire)
3. Réexécutez `python main.py --run-once --tasks all` pour recréer les dossiers et réinitialiser le système

### Reconstruction de l'index

Si l'index central semble corrompu ou désynchronisé :

```bash
python tools/file_manager_tool.py rebuild
```

### Problèmes avec le bot Telegram

Si le bot Telegram ne répond pas :

1. Vérifiez que le token dans `.env` est correct
2. Assurez-vous que le bot n'a pas été bloqué ou supprimé
3. Redémarrez le bot : `python main.py --run-once --tasks telegram`

## Ressources additionnelles

- [Documentation OpenAI](https://platform.openai.com/docs/introduction)
- [Documentation ElevenLabs](https://docs.elevenlabs.io/welcome/introduction)
- [Documentation python-telegram-bot](https://docs.python-telegram-bot.org/)
- [Guide FFmpeg](https://ffmpeg.org/documentation.html)

## Support

Pour obtenir de l'aide supplémentaire, vous pouvez :

1. Consulter les logs détaillés dans le dossier `logs/`
2. Exécuter les tests avec l'option verbose : `python run_tests.py --verbose`
3. Vérifier la configuration : `python main.py --check-config`
