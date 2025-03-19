import os
import json
import logging
import asyncio
from datetime import datetime
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Récupérer le token du bot depuis les variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

# Dossier contenant les données et analyses
DATA_FOLDER = "data"
ANALYSIS_FOLDER = "analysis_results"

class QuantumCryptoBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
        # État du bot
        self.subscribed_users = self._load_subscribed_users()
        
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
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la commande /unsubscribe"""
        user_id = update.effective_user.id
        
        if user_id in self.subscribed_users:
            self.subscribed_users.remove(user_id)
            self._save_subscribed_users()
            await update.message.reply_text(
                "❌ Vous êtes maintenant désabonné des mises à jour."
            )
        else:
            await update.message.reply_text(
                "Vous n'êtes pas abonné aux mises à jour. Utilisez /subscribe pour vous abonner."
            )
    
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
            logger.error(f"Error in latest_command: {e}")
            await update.message.reply_text(f"Une erreur s'est produite: {str(e)}")
    
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la commande /summary - affiche le résumé des tendances récentes"""
        try:
            # Chercher le fichier de résumé le plus récent
            reports_folder = os.path.join(ANALYSIS_FOLDER, "reports")
            os.makedirs(reports_folder, exist_ok=True)
            summary_files = [f for f in os.listdir(reports_folder) if f.startswith('recent_trends_summary')]
            
            if not summary_files:
                await update.message.reply_text(
                    "Aucun résumé disponible pour le moment. Réessayez plus tard."
                )
                return
            
            latest_summary = os.path.join(reports_folder, sorted(summary_files)[-1])
            
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
            logger.error(f"Error in summary_command: {e}")
            await update.message.reply_text(f"Une erreur s'est produite: {str(e)}")
    
    def _get_latest_podcast_link(self):
        """Retourne le lien vers le dernier podcast s'il existe"""
        # Cette fonction serait à implémenter en fonction de votre système de podcasts
        # Pour l'instant, on retourne un lien fictif
        return "https://example.com/quantum-crypto-podcast-latest"
    
    async def topics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la commande /topics - affiche les principaux sujets de discussion"""
        try:
            # Chercher dans le dossier entities
            entities_folder = os.path.join(ANALYSIS_FOLDER, "entities")
            os.makedirs(entities_folder, exist_ok=True)
            topics_file = os.path.join(entities_folder, "topics.csv")
            
            # Si le fichier n'existe pas dans entities, chercher à la racine
            if not os.path.exists(topics_file):
                topics_file = os.path.join(ANALYSIS_FOLDER, "topics.csv")
            
            if not os.path.exists(topics_file):
                await update.message.reply_text(
                    "Analyse des sujets non disponible pour le moment."
                )
                return
            
            topics_df = pd.read_csv(topics_file)
            
            message = "🔍 *PRINCIPAUX SUJETS EN CRYPTOGRAPHIE QUANTIQUE*\n\n"
            
            for _, topic in topics_df.iterrows():
                message += f"*{topic['label']}*\n"
                terms = eval(topic['terms']) if isinstance(topic['terms'], str) else topic['terms']
                message += f"Termes associés: {', '.join(terms[:5])}\n\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in topics_command: {e}")
            await update.message.reply_text(f"Une erreur s'est produite: {str(e)}")
    
    async def sources_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la commande /sources - affiche les sources les plus actives"""
        try:
            # Trouver le digest quotidien le plus récent
            daily_folder = os.path.join(ANALYSIS_FOLDER, "daily")
            os.makedirs(daily_folder, exist_ok=True)
            digest_files = [f for f in os.listdir(daily_folder) if f.startswith('daily_digest')]
            
            if not digest_files:
                await update.message.reply_text(
                    "Informations sur les sources non disponibles pour le moment."
                )
                return
            
            latest_digest = os.path.join(daily_folder, sorted(digest_files)[-1])
            
            with open(latest_digest, 'r') as f:
                digest = json.load(f)
            
            message = "📚 *SOURCES LES PLUS ACTIVES EN CRYPTOGRAPHIE QUANTIQUE*\n\n"
            
            for source, count in digest.get('top_sources', {}).items():
                message += f"*{source}*: {count} publications\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in sources_command: {e}")
            await update.message.reply_text(f"Une erreur s'est produite: {str(e)}")
    
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
    
    def run(self):
        """Démarre le bot"""
        logger.info("Starting Quantum Cryptography Bot")
        self.application.run_polling()

if __name__ == "__main__":
    bot = QuantumCryptoBot(TELEGRAM_TOKEN)
    bot.run()