# Module de Diffusion Telegram

## Présentation générale

Le module de diffusion Telegram (`src/distributors/telegram_bot.py`) permet de diffuser les informations de veille via un bot Telegram interactif. Il offre aux utilisateurs un moyen pratique et mobile d'accéder aux dernières actualités, analyses et tendances dans le domaine de la cryptographie quantique.

## Classe principale : QuantumCryptoBot

La classe `QuantumCryptoBot` coordonne toutes les fonctionnalités du bot Telegram. Elle gère les commandes, les interactions utilisateur, et l'envoi de notifications.

### Initialisation

```python
def __init__(self, token):
    self.token = token
    self.application = Application.builder().token(token).build()
    self.setup_handlers()
    
    # État du bot
    self.subscribed_users = self._load_subscribed_users()
```

## Configuration des gestionnaires de commandes

La méthode `setup_handlers()` configure toutes les commandes disponibles dans le bot :

```python
def setup_handlers(self):
    """Configure les gestionnaires de commandes pour le bot"""
    self.application.add_handler(CommandHandler("start", self.start_command))
    self.application.add_handler(CommandHandler("help", self.help_command))
    self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
    self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
    self.application.add_handler(CommandHandler("latest", self.latest_command))
    self.application.add_handler(CommandHandler("summary", self.summary_command))
    self.application.add_handler(CommandHandler("topics", self.topics_command))
    self.application.add_handler(CommandHandler("sources", self.sources_command))
    self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    # Planifier l'envoi quotidien du résumé
    self.application.job_queue.run_daily(
        self.send_daily_digest,
        time=datetime.strptime("09:00:00", "%H:%M:%S").time()
    )
```

## Commandes disponibles

Le bot offre plusieurs commandes interactives :

### Commande /start

La commande `start_command()` accueille les nouveaux utilisateurs et présente les fonctionnalités du bot :

```python
async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la commande /start"""
    user = update.effective_user
    welcome_message = (
        f"Bonjour {user.first_name} ! 👋\n\n"
        "Bienvenue sur le bot de veille technologique sur la cryptographie quantique.\n\n"
        "Ce bot vous permet de suivre les dernières actualités, recherches et tendances dans "
        "le domaine de la cryptographie quantique.\n\n"
        "Utilisez /help pour voir la liste des commandes disponibles."
    )
    
    # Créer un clavier inline pour les actions principales
    keyboard = [
        [
            InlineKeyboardButton("S'abonner aux mises à jour", callback_data="subscribe"),
            InlineKeyboardButton("Dernières actualités", callback_data="latest")
        ],
        [
            InlineKeyboardButton("Résumé de la semaine", callback_data="summary"),
            InlineKeyboardButton("Thèmes principaux", callback_data="topics")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
```

### Commande /help

La commande `help_command()` affiche la liste des commandes disponibles :

```python
async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la commande /help"""
    help_text = (
        "Commandes disponibles:\n\n"
        "/subscribe - S'abonner aux mises à jour quotidiennes\n"
        "/unsubscribe - Se désabonner des mises à jour\n"
        "/latest - Voir les 5 dernières publications\n"
        "/summary - Obtenir un résumé des tendances récentes\n"
        "/topics - Voir les principaux sujets de discussion\n"
        "/sources - Voir les sources les plus actives\n"
        "/help - Afficher ce message d'aide"
    )
    await update.message.reply_text(help_text)
```

### Gestion des abonnements

Les commandes `subscribe_command()` et `unsubscribe_command()` permettent aux utilisateurs de gérer leur abonnement aux notifications :

```python
async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la commande /subscribe"""
    user_id = update.effective_user.id
    
    if user_id not in self.subscribed_users:
        self.subscribed_users.append(user_id)
        self._save_subscribed_users()
        await update.message.reply_text(
            "✅ Vous êtes maintenant abonné aux mises à jour quotidiennes sur la cryptographie quantique."
        )
    else:
        await update.message.reply_text(
            "Vous êtes déjà abonné aux mises à jour. Utilisez /unsubscribe pour vous désabonner."
        )
```

### Informations récentes

La commande `latest_command()` affiche les dernières publications :

```python
async def latest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la commande /latest - affiche les dernières publications"""
    try:
        # Trouver le fichier de données le plus récent
        data_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv') or f.endswith('.json')]
        if not data_files:
            await update.message.reply_text("Aucune donnée disponible pour le moment.")
            return
        
        latest_file = sorted(data_files)[-1]
        file_path = os.path.join(DATA_FOLDER, latest_file)
        
        # Charger les données
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            with open(file_path, 'r') as f:
                df = pd.DataFrame(json.load(f))
        
        # Trier par date et prendre les 5 plus récentes
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        latest_items = df.sort_values('date', ascending=False).head(5)
        
        # Formater le message
        message = "📰 *DERNIÈRES PUBLICATIONS EN CRYPTOGRAPHIE QUANTIQUE*\n\n"
        
        for _, item in latest_items.iterrows():
            message += f"*{item['title']}*\n"
            message += f"Source: {item['source']} | Date: {item['date'].strftime('%d/%m/%Y')}\n"
            message += f"[Lien]({item['url']})\n\n"
        
        await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=True)
    
    except Exception as e:
        await update.message.reply_text(f"Une erreur s'est produite: {str(e)}")
```

### Résumés et analyses

Les commandes `summary_command()` et `topics_command()` donnent accès aux analyses :

```python
async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la commande /summary - affiche le résumé des tendances récentes"""
    try:
        # Chercher le fichier de résumé le plus récent
        summary_files = [f for f in os.listdir(ANALYSIS_FOLDER) if f.startswith('recent_trends_summary')]
        
        if not summary_files:
            await update.message.reply_text(
                "Aucun résumé disponible pour le moment. Réessayez plus tard."
            )
            return
        
        latest_summary = os.path.join(ANALYSIS_FOLDER, sorted(summary_files)[-1])
        
        with open(latest_summary, 'r') as f:
            summary_text = f.read()
        
        # Ajouter un titre et formater
        message = "📊 *RÉSUMÉ DES TENDANCES EN CRYPTOGRAPHIE QUANTIQUE*\n\n"
        message += summary_text
        
        # Ajouter un lien vers le podcast si disponible
        podcast_link = self._get_latest_podcast_link()
        if podcast_link:
            message += f"\n\n🎙️ *Écoutez notre podcast pour plus de détails*: [Lien]({podcast_link})"
        
        await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=True)
    
    except Exception as e:
        await update.message.reply_text(f"Une erreur s'est produite: {str(e)}")
```

## Notifications automatiques

La méthode `send_daily_digest()` envoie automatiquement un résumé quotidien aux utilisateurs abonnés :

```python
async def send_daily_digest(self, context: ContextTypes.DEFAULT_TYPE):
    """Envoie le résumé quotidien aux utilisateurs abonnés"""
    try:
        # Trouver le digest quotidien le plus récent
        digest_files = [f for f in os.listdir(ANALYSIS_FOLDER) if f.startswith('daily_digest')]
        
        if not digest_files:
            logger.warning("No daily digest available to send")
            return
        
        latest_digest = os.path.join(ANALYSIS_FOLDER, sorted(digest_files)[-1])
        
        with open(latest_digest, 'r') as f:
            digest = json.load(f)
        
        # Formater le message
        today = datetime.now().strftime('%d/%m/%Y')
        message = f"🔔 *VEILLE CRYPTOGRAPHIE QUANTIQUE - {today}*\n\n"
        
        # Ajouter les dernières recherches
        message += "*Dernières recherches publiées:*\n"
        for item in digest.get('latest_research', [])[:3]:
            title = item.get('title', 'Sans titre')
            source = item.get('source', 'Source inconnue')
            url = item.get('url', '#')
            message += f"- [{title}]({url}) - {source}\n"
        
        message += "\n*Dernières actualités:*\n"
        for item in digest.get('latest_news', [])[:3]:
            title = item.get('title', 'Sans titre')
            source = item.get('source', 'Source inconnue')
            url = item.get('url', '#')
            message += f"- [{title}]({url}) - {source}\n"
        
        # Ajouter un lien vers le podcast s'il est disponible
        podcast_link = self._get_latest_podcast_link()
        if podcast_link:
            message += f"\n🎙️ *Nouveau podcast disponible*: [Écouter]({podcast_link})"
        
        # Ajouter des boutons pour plus d'informations
        keyboard = [
            [
                InlineKeyboardButton("Voir tous les derniers articles", callback_data="latest"),
                InlineKeyboardButton("Résumé des tendances", callback_data="summary")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Envoyer à tous les utilisateurs abonnés
        for user_id in self.subscribed_users:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown",
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Could not send message to {user_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error in send_daily_digest: {e}")
```

## Gestion des boutons interactifs

La méthode `button_callback()` gère les clics sur les boutons interactifs :

```python
async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les boutons inline"""
    query = update.callback_query
    await query.answer()
    
    # Rediriger vers la commande appropriée en fonction du callback_data
    if query.data == "subscribe":
        await self.subscribe_command(update, context)
    elif query.data == "latest":
        await self.latest_command(update, context)
    elif query.data == "summary":
        await self.summary_command(update, context)
    elif query.data == "topics":
        await self.topics_command(update, context)
```

## Démarrage du bot et gestion des threads

Le bot est conçu pour fonctionner en arrière-plan, dans un thread dédié :

```python
# Dans QuantumCryptoVeille (main.py)
def start_telegram_bot(self):
    """Démarre le bot Telegram en arrière-plan"""
    if not self.telegram_token:
        logger.warning("Bot Telegram non démarré (token manquant dans .env)")
        return False
    
    try:
        # Démarrer le bot dans un processus séparé
        import threading
        
        def run_bot():
            logger.info("Initialisation du bot Telegram...")
            bot = QuantumCryptoBot(self.telegram_token)
            logger.info("Bot Telegram configuré, démarrage...")
            bot.run()
        
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
        bot_thread.start()
        
        logger.info("Bot Telegram démarré dans un thread d'arrière-plan")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du bot Telegram: {e}")
        return False
```

## Structure des messages

Les messages envoyés par le bot suivent une structure cohérente :

1. **Titre** en gras et en majuscules avec émojis pertinents
2. **Contenu principal** formaté en Markdown
3. **Liens cliquables** pour les articles et ressources
4. **Boutons interactifs** pour les actions supplémentaires

Exemple de message quotidien :

```
🔔 VEILLE CRYPTOGRAPHIE QUANTIQUE - 19/03/2025

Dernières recherches publiées:
- Advances in Quantum Key Distribution - arXiv
- Post-Quantum Cryptography: A Survey - IEEE
- Quantum-Resistant Algorithms for IoT Devices - ACM

Dernières actualités:
- IBM Announces New Quantum-Safe Encryption - Quantum Computing Report
- NSA Releases Guidelines on Post-Quantum Security - Inside Quantum Technology
- European Initiative for Quantum Communication Infrastructure - Quantum Zeitgeist

🎙️ Nouveau podcast disponible: Écouter

[Voir tous les derniers articles] [Résumé des tendances]
```

## Stockage des données utilisateurs

Le bot maintient une liste des utilisateurs abonnés dans un fichier JSON :

```python
def _load_subscribed_users(self):
    """Charge la liste des utilisateurs abonnés depuis un fichier JSON"""
    try:
        with open('subscribed_users.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _save_subscribed_users(self):
    """Sauvegarde la liste des utilisateurs abonnés dans un fichier JSON"""
    with open('subscribed_users.json', 'w') as f:
        json.dump(self.subscribed_users, f)
```

## Intégration avec les podcasts

Le bot fournit également des liens vers les podcasts générés :

```python
def _get_latest_podcast_link(self):
    """Retourne le lien vers le dernier podcast s'il existe"""
    podcast_folder = "podcasts"
    weekly_folder = os.path.join(podcast_folder, "weekly")
    
    # Chercher le podcast le plus récent
    if os.path.exists(weekly_folder):
        podcast_files = [f for f in os.listdir(weekly_folder) if f.endswith('.mp3')]
        if podcast_files:
            latest_podcast = sorted(podcast_files)[-1]
            # Construction de l'URL (à adapter selon votre hébergement)
            return f"https://example.com/podcasts/{latest_podcast}"
    
    return None
```

## Avantages du canal Telegram

L'utilisation de Telegram comme canal de diffusion offre plusieurs avantages :

1. **Accessibilité** : Les utilisateurs peuvent accéder aux informations sur mobile ou desktop
2. **Interactivité** : Les boutons et commandes permettent une navigation facile
3. **Notifications** : Les utilisateurs sont alertés des nouvelles publications
4. **Format riche** : Support du Markdown, des liens et des médias
5. **Engagement** : Les utilisateurs peuvent choisir les informations qui les intéressent
6. **Faible barrière d'entrée** : Simple à utiliser, pas de création de compte spécifique nécessaire

## Configuration du bot

Pour configurer le bot, un token Telegram est nécessaire :

1. Créer un bot via [@BotFather](https://t.me/botfather) sur Telegram
2. Obtenir le token du bot et l'ajouter dans le fichier `.env`
3. Activer le bot en exécutant le système

```
# Exemple de configuration dans .env
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ
```
