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

# Import du logger personnalisé
from src.utils.logger import get_logger
qv_logger = get_logger()
logger = qv_logger.logger

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
        qv_logger.log_stage_start("Collecte de données")
        
        try:
            scraper = QuantumCryptoScraper()
            csv_path, json_path = scraper.fetch_all_sources()
            
            # Collecter des statistiques sur les données collecteées
            stats = {}
            try:
                import json
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    
                stats = {
                    "Total des éléments collectés": len(data),
                    "Articles scientifiques": sum(1 for item in data if item.get("type") == "research"),
                    "Articles d'actualité": sum(1 for item in data if item.get("type") == "news"),
                    "Sources uniques": len(set(item.get("source", "") for item in data))
                }
                qv_logger.log_data_stats(stats)
            except Exception as stats_e:
                logger.warning(f"Impossible de collecter les statistiques: {stats_e}")
            
            logger.info(f"Collecte de données terminée. Fichiers sauvegardés dans: {csv_path} et {json_path}")
            qv_logger.log_stage_end("Collecte de données", True)
            return json_path
        
        except Exception as e:
            qv_logger.log_exception(e, "Erreur durant la collecte de données")
            qv_logger.log_stage_end("Collecte de données", False)
            return None
    
    def analyze_data(self, data_path):
        """Analyse les données collectées"""
        qv_logger.log_stage_start("Analyse des données")
        logger.info(f"Démarrage de l'analyse pour {data_path}")
        
        try:
            analyzer = QuantumCryptoAnalyzer(data_path)
            results = analyzer.run_full_analysis()
            
            # Vérifier les résultats
            if 'topics' in results and results['topics']:
                logger.info(f"Thèmes identifiés: {len(results['topics'])}")
                for i, topic in enumerate(results['topics']):
                    logger.info(f"Thème {i+1}: {topic.get('label', 'Non étiqueté')}")
            else:
                logger.warning("Aucun thème n'a été identifié dans les données")
            
            if 'summary' in results and results['summary']:
                logger.info("Une synthèse des tendances a été générée")
            else:
                logger.warning("Aucune synthèse n'a pu être générée")
                
            logger.info(f"Analyse terminée. Résultats sauvegardés dans {self.analysis_folder}")
            qv_logger.log_stage_end("Analyse des données", True)
            return results
        
        except Exception as e:
            qv_logger.log_exception(e, "Erreur durant l'analyse des données")
            qv_logger.log_stage_end("Analyse des données", False)
            return None
    
    def generate_podcast(self):
        """Génère le podcast à partir des analyses"""
        qv_logger.log_stage_start("Génération de podcast")
        
        # Vérifier que les fichiers nécessaires sont disponibles
        summary_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('recent_trends_summary')]
        digest_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('daily_digest')]
        
        if not summary_files or not digest_files:
            logger.error("Fichiers d'analyse nécessaires non disponibles pour la génération du podcast")
            qv_logger.log_stage_end("Génération de podcast", False)
            return None
        
        try:
            # Vérifier la disponibilité de ffmpeg
            import shutil
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                logger.warning("ffmpeg non trouvé sur le système. La génération audio pourrait échouer.")
            
            podcast_generator = QuantumCryptoPodcast(
                analysis_folder=self.analysis_folder,
                output_folder=self.podcast_folder
            )
            result = podcast_generator.generate_podcast()
            
            if result["status"] == "success":
                logger.info(f"Podcast généré avec succès: {result['podcast_path']}")
                logger.info(f"Script: {result['script_path']}")
                logger.info(f"URL: {result.get('podcast_url', 'Non disponible')}")
                qv_logger.log_stage_end("Génération de podcast", True)
                return result["podcast_path"]
            else:
                error_details = result.get('error', 'Raison inconnue')
                logger.error(f"Erreur lors de la génération du podcast: {error_details}")
                qv_logger.log_stage_end("Génération de podcast", False)
                return None
        
        except Exception as e:
            qv_logger.log_exception(e, "Erreur lors de la génération du podcast")
            qv_logger.log_stage_end("Génération de podcast", False)
            return None
    
    def start_telegram_bot(self):
        """Démarre le bot Telegram en arrière-plan"""
        qv_logger.log_stage_start("Démarrage du bot Telegram")
        
        if not self.telegram_token:
            logger.warning("Bot Telegram non démarré (token manquant dans .env)")
            logger.info("Ajoutez votre token Telegram dans le fichier .env pour activer cette fonctionnalité")
            qv_logger.log_stage_end("Démarrage du bot Telegram", False)
            return False
        
        # Vérifier que le token ne contient pas la valeur par défaut
        if self.telegram_token.startswith("your_"):
            logger.warning("Bot Telegram non démarré (token par défaut détecté)")
            logger.info("Remplacez 'your_telegram_bot_token_here' par un véritable token dans le fichier .env")
            qv_logger.log_stage_end("Démarrage du bot Telegram", False)
            return False
        
        try:
            # Démarrer le bot dans un processus séparé
            import threading
            
            def run_bot():
                logger.info("Initialisation du bot Telegram...")
                try:
                    bot = QuantumCryptoBot(self.telegram_token)
                    logger.info("Bot Telegram configuré, démarrage...")
                    bot.run()
                except Exception as bot_e:
                    logger.error(f"Erreur dans le thread du bot: {bot_e}")
            
            bot_thread = threading.Thread(target=run_bot)
            bot_thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
            bot_thread.start()
            
            logger.info("Bot Telegram démarré dans un thread d'arrière-plan")
            logger.info("Utilisez Telegram pour interagir avec le bot")
            qv_logger.log_stage_end("Démarrage du bot Telegram", True)
            return True
        
        except Exception as e:
            qv_logger.log_exception(e, "Erreur lors du démarrage du bot Telegram")
            qv_logger.log_stage_end("Démarrage du bot Telegram", False)
            return False
    
    def run_full_pipeline(self):
        """Exécute le pipeline complet de veille"""
        qv_logger.log_stage_start("Pipeline de veille complet")
        logger.info("Exécution du pipeline complet de veille technologique")
        
        try:
            # Vérifier la configuration au démarrage
            qv_logger.log_config_status()
            
            # 1. Collecte des données
            data_path = self.collect_data()
            if not data_path:
                logger.error("La collecte de données a échoué, arrêt du pipeline")
                qv_logger.log_stage_end("Pipeline de veille complet", False)
                return False
            
            # 2. Analyse des données
            analysis_results = self.analyze_data(data_path)
            if not analysis_results:
                logger.error("L'analyse des données a échoué, arrêt du pipeline")
                qv_logger.log_stage_end("Pipeline de veille complet", False)
                return False
            
            # 3. Génération du podcast (une fois par semaine)
            today = datetime.now()
            is_podcast_day = today.weekday() == 0  # Lundi
            
            if is_podcast_day:
                logger.info("Jour de génération de podcast (lundi)")
                podcast_path = self.generate_podcast()
                if podcast_path:
                    logger.info(f"Podcast hebdomadaire généré: {podcast_path}")
                else:
                    logger.warning("La génération du podcast a échoué mais le pipeline continue")
            else:
                logger.info(f"Pas de génération de podcast aujourd'hui (jour de la semaine: {today.weekday()})")
            
            # 4. Démarrer le bot Telegram
            self.start_telegram_bot()
            
            logger.info("Pipeline de veille terminé avec succès")
            qv_logger.log_stage_end("Pipeline de veille complet", True)
            return True
        
        except Exception as e:
            qv_logger.log_exception(e, "Erreur dans le pipeline de veille")
            qv_logger.log_stage_end("Pipeline de veille complet", False)
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
    parser.add_argument("--check-config", action="store_true", help="Vérifier la configuration uniquement, sans exécuter")
    
    args = parser.parse_args()
    
    # Vérifier la configuration au démarrage
    logger.info("Démarrage du système de veille sur la cryptographie quantique")
    qv_logger.log_config_status()
    
    # Si l'utilisateur a demandé uniquement une vérification de la configuration
    if args.check_config:
        logger.info("Vérification de la configuration terminée.")
        return
    
    veille_system = QuantumCryptoVeille()
    
    if args.run_once:
        veille_system.run_once(args.tasks)
    else:
        veille_system.schedule_tasks()

if __name__ == "__main__":
    main()