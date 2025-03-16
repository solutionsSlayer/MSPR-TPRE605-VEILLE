import os
import sys
import logging
import argparse
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

# Ajouter les répertoires source au chemin Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/collectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/analyzers'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/distributors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/podcast'))

# Importer nos modules
from collectors.quantum_crypto_scraper import QuantumCryptoScraper
from analyzers.quantum_crypto_analyzer import QuantumCryptoAnalyzer
from distributors.telegram_bot import QuantumCryptoBot
from podcast.podcast_generator import QuantumCryptoPodcast

# Charger les variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quantum_veille.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QuantumCryptoVeille:
    def __init__(self):
        """Initialise le système de veille technologique"""
        self.data_folder = "data"
        self.analysis_folder = "analysis_results"
        self.podcast_folder = "podcasts"
        
        # Créer les dossiers nécessaires
        for folder in [self.data_folder, self.analysis_folder, self.podcast_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # Récupérer les tokens et API keys
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Vérifier les tokens requis
        if not self.telegram_token:
            logger.warning("TELEGRAM_BOT_TOKEN not found in environment variables. Telegram bot will not be available.")
    
    def collect_data(self):
        """Collecte les données depuis les sources configurées"""
        logger.info("Starting data collection process")
        
        try:
            scraper = QuantumCryptoScraper()
            csv_path, json_path = scraper.fetch_all_sources()
            
            logger.info(f"Data collection completed. Files saved to: {csv_path} and {json_path}")
            return json_path
        
        except Exception as e:
            logger.error(f"Error during data collection: {e}")
            return None
    
    def analyze_data(self, data_path):
        """Analyse les données collectées"""
        logger.info(f"Starting data analysis process for {data_path}")
        
        try:
            analyzer = QuantumCryptoAnalyzer(data_path)
            results = analyzer.run_full_analysis()
            
            logger.info(f"Data analysis completed. Results saved to {self.analysis_folder}")
            return results
        
        except Exception as e:
            logger.error(f"Error during data analysis: {e}")
            return None
    
    def generate_podcast(self):
        """Génère le podcast à partir des analyses"""
        logger.info("Starting podcast generation process")
        
        try:
            podcast_generator = QuantumCryptoPodcast(
                analysis_folder=self.analysis_folder,
                output_folder=self.podcast_folder
            )
            result = podcast_generator.generate_podcast()
            
            if result["status"] == "success":
                logger.info(f"Podcast successfully generated: {result['podcast_path']}")
                return result["podcast_path"]
            else:
                logger.error(f"Error generating podcast: {result['error']}")
                return None
        
        except Exception as e:
            logger.error(f"Error during podcast generation: {e}")
            return None
    
    def start_telegram_bot(self):
        """Démarre le bot Telegram en arrière-plan"""
        if not self.telegram_token:
            logger.warning("Telegram bot not started (missing token)")
            return False
        
        try:
            # Démarrer le bot dans un processus séparé
            import threading
            
            def run_bot():
                bot = QuantumCryptoBot(self.telegram_token)
                bot.run()
            
            bot_thread = threading.Thread(target=run_bot)
            bot_thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
            bot_thread.start()
            
            logger.info("Telegram bot started in background thread")
            return True
        
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
            return False
    
    def run_full_pipeline(self):
        """Exécute le pipeline complet de veille"""
        logger.info("Running full veille pipeline")
        
        try:
            # 1. Collecte des données
            data_path = self.collect_data()
            if not data_path:
                logger.error("Data collection failed, stopping pipeline")
                return False
            
            # 2. Analyse des données
            analysis_results = self.analyze_data(data_path)
            if not analysis_results:
                logger.error("Data analysis failed, stopping pipeline")
                return False
            
            # 3. Génération du podcast (une fois par semaine)
            today = datetime.now()
            if today.weekday() == 0:  # Lundi
                podcast_path = self.generate_podcast()
                if podcast_path:
                    logger.info(f"Weekly podcast generated: {podcast_path}")
            
            logger.info("Veille pipeline completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error in veille pipeline: {e}")
            return False
    
    def schedule_tasks(self):
        """Configure les tâches planifiées"""
        logger.info("Setting up scheduled tasks")
        
        # Exécuter la veille tous les jours à 3h du matin
        schedule.every().day.at("03:00").do(self.run_full_pipeline)
        
        # Exécuter immédiatement au démarrage
        self.run_full_pipeline()
        
        # Démarrer le bot Telegram
        self.start_telegram_bot()
        
        logger.info("Scheduled tasks configured, entering main loop")
        
        # Boucle principale
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Attendre 1 minute entre les vérifications
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
    
    def run_once(self, tasks):
        """Exécute les tâches spécifiées une seule fois"""
        if "collect" in tasks:
            self.collect_data()
        
        if "analyze" in tasks:
            # Trouver le fichier de données le plus récent
            data_files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
            if data_files:
                latest_file = sorted(data_files)[-1]
                self.analyze_data(os.path.join(self.data_folder, latest_file))
            else:
                logger.error("No data files found for analysis")
        
        if "podcast" in tasks:
            self.generate_podcast()
        
        if "telegram" in tasks:
            self.start_telegram_bot()
            # Garder le programme en vie
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Telegram bot stopped by user")
        
        if "all" in tasks:
            self.run_full_pipeline()

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Système de veille technologique sur la cryptographie quantique")
    
    parser.add_argument("--run-once", action="store_true", help="Exécuter une seule fois puis terminer")
    parser.add_argument("--tasks", nargs="+", default=["all"], 
                        choices=["collect", "analyze", "podcast", "telegram", "all"],
                        help="Tâches à exécuter (collect, analyze, podcast, telegram, all)")
    
    args = parser.parse_args()
    
    veille_system = QuantumCryptoVeille()
    
    if args.run_once:
        veille_system.run_once(args.tasks)
    else:
        veille_system.schedule_tasks()

if __name__ == "__main__":
    main()