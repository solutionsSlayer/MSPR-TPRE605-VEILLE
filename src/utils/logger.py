"""
Module de gestion des logs pour le système de veille sur la cryptographie quantique.
Permet de créer des logs détaillés avec une nomenclature spécifique.
"""

import os
import logging
import traceback
from datetime import datetime
from pathlib import Path

class QuantumVeilleLogger:
    """
    Gestionnaire de logs avancé pour le système de veille.
    Crée des fichiers de logs avec une nomenclature par date et heure.
    """
    
    def __init__(self, log_level=logging.INFO):
        """
        Initialise le gestionnaire de logs.
        
        Args:
            log_level: Niveau de logging (par défaut: INFO)
        """
        self.logger = logging.getLogger("quantum_veille")
        self.logger.setLevel(log_level)
        
        # Créer le dossier logs s'il n'existe pas
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Vider les handlers existants
        if self.logger.handlers:
            self.logger.handlers.clear()
        
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
        
        # Logger l'initialisation
        self.logger.info(f"Logger initialisé - fichier de log: {self.current_log_file}")
    
    def _create_log_file(self):
        """
        Crée un nouveau fichier de log avec la nomenclature temporelle.
        
        Returns:
            str: Chemin vers le fichier de log créé
        """
        # Format: logs/YYYYMMDD_HHMMSS_quantum_veille.log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"{timestamp}_quantum_veille.log"
        return str(log_file)
    
    def get_latest_log_file(self):
        """
        Retourne le chemin vers le fichier de log le plus récent.
        
        Returns:
            str: Chemin vers le dernier fichier de log
        """
        log_files = list(self.logs_dir.glob("*_quantum_veille.log"))
        if not log_files:
            return None
        
        # Trier par date de modification, le plus récent en premier
        return str(sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[0])
    
    def log_exception(self, e, context=""):
        """
        Enregistre une exception avec ses détails complets.
        
        Args:
            e: L'exception à enregistrer
            context: Contexte supplémentaire (optionnel)
        """
        error_msg = f"{context}: {str(e)}" if context else str(e)
        self.logger.error(error_msg)
        
        # Enregistrer la trace complète
        tb = traceback.format_exc()
        self.logger.debug(f"Traceback complète: {tb}")
    
    def log_api_error(self, service_name, error_details):
        """
        Enregistre une erreur d'API externe de manière structurée.
        
        Args:
            service_name: Nom du service API (ex: "OpenAI", "Telegram")
            error_details: Détails de l'erreur
        """
        self.logger.error(f"Erreur API {service_name}: {error_details}")
    
    def log_stage_start(self, stage_name):
        """
        Enregistre le début d'une étape du pipeline.
        
        Args:
            stage_name: Nom de l'étape
        """
        self.logger.info(f"DÉBUT ÉTAPE: {stage_name} {'='*40}")
    
    def log_stage_end(self, stage_name, success=True):
        """
        Enregistre la fin d'une étape du pipeline.
        
        Args:
            stage_name: Nom de l'étape
            success: Indique si l'étape s'est terminée avec succès
        """
        status = "RÉUSSIE" if success else "ÉCHOUÉE"
        self.logger.info(f"FIN ÉTAPE: {stage_name} - {status} {'='*40}")
    
    def log_data_stats(self, stats_dict):
        """
        Enregistre des statistiques sur les données collectées/analysées.
        
        Args:
            stats_dict: Dictionnaire de statistiques
        """
        self.logger.info("Statistiques des données:")
        for key, value in stats_dict.items():
            self.logger.info(f"  - {key}: {value}")
    
    def log_config_status(self):
        """
        Vérifie et enregistre l'état des configurations principales.
        """
        self.logger.info("Vérification des configurations:")
        
        # Vérifier les dossiers
        for folder in ["data", "analysis_results", "podcasts"]:
            # Utiliser du texte ASCII plutôt que des symboles Unicode pour éviter les problèmes d'encodage
            status = "OK" if os.path.isdir(folder) else "ABSENT"
            self.logger.info(f"  - Dossier {folder}: {status}")
        
        # Vérifier le fichier .env
        env_exists = os.path.isfile(".env")
        status = "OK" if env_exists else "ABSENT"
        self.logger.info(f"  - Fichier .env: {status}")
        
        # Vérifier les clés API sans les exposer
        if env_exists:
            from dotenv import load_dotenv
            import os as os_env
            
            load_dotenv()
            
            openai_api = os_env.getenv("OPENAI_API_KEY", "")
            telegram_bot = os_env.getenv("TELEGRAM_BOT_TOKEN", "")
            elevenlabs_api = os_env.getenv("ELEVENLABS_API_KEY", "")
            
            openai_status = "OK" if openai_api and not openai_api.startswith("your_") else "ABSENT"
            telegram_status = "OK" if telegram_bot and not telegram_bot.startswith("your_") else "ABSENT"
            elevenlabs_status = "OK" if elevenlabs_api and not elevenlabs_api.startswith("your_") else "ABSENT"
            
            self.logger.info(f"  - Clé API OpenAI: {openai_status}")
            self.logger.info(f"  - Token Bot Telegram: {telegram_status}")
            self.logger.info(f"  - Clé API ElevenLabs: {elevenlabs_status}")
        
        # Vérifier la présence de ffmpeg
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        ffmpeg_status = "OK" if ffmpeg_path else "ABSENT"
        self.logger.info(f"  - FFmpeg: {ffmpeg_status}")
        if ffmpeg_path:
            self.logger.info(f"    Chemin: {ffmpeg_path}")

# Créer une instance singleton pour être utilisée dans tout le projet
logger = QuantumVeilleLogger()

def get_logger():
    """
    Retourne l'instance du logger pour être utilisée dans les autres modules.
    
    Returns:
        QuantumVeilleLogger: Instance du logger
    """
    return logger
