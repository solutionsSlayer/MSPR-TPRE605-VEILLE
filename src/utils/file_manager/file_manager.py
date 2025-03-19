"""
Module de gestion des fichiers pour le système de veille sur la cryptographie quantique.
Ce module facilite l'organisation, l'archivage et la recherche des fichiers de données et d'analyse.
"""

import os
import json
import shutil
import logging
from datetime import datetime, timedelta
import pandas as pd

# Configuration du logger
logger = logging.getLogger("quantum_veille.file_manager")

class FileManager:
    """
    Gestionnaire de fichiers pour le système de veille technologique.
    
    Cette classe centralise toutes les opérations sur les fichiers:
    - Sauvegarde des données collectées
    - Organisation des résultats d'analyse
    - Archivage automatique des anciens fichiers
    - Gestion des méta-données via un index central
    """
    
    def __init__(self, base_path="."):
        """
        Initialise le gestionnaire de fichiers.
        
        Args:
            base_path: Chemin de base du projet
        """
        self.base_path = base_path
        
        # Chemins des dossiers
        self.data_folder = os.path.join(base_path, "data")
        self.current_data_folder = os.path.join(self.data_folder, "current")
        self.archives_folder = os.path.join(self.data_folder, "archives")
        
        self.analysis_folder = os.path.join(base_path, "analysis_results")
        self.daily_analysis_folder = os.path.join(self.analysis_folder, "daily")
        self.weekly_analysis_folder = os.path.join(self.analysis_folder, "weekly")
        self.monthly_analysis_folder = os.path.join(self.analysis_folder, "monthly")
        
        self.podcast_folder = os.path.join(base_path, "podcasts")
        self.weekly_podcast_folder = os.path.join(self.podcast_folder, "weekly")
        self.monthly_podcast_folder = os.path.join(self.podcast_folder, "monthly")
        
        # Fichier d'index
        self.index_file = os.path.join(self.data_folder, "index.json")
        
        # Créer les dossiers s'ils n'existent pas
        self._ensure_directory_structure()
        
        # Charger ou créer l'index
        self.index = self._load_index()
    
    def _ensure_directory_structure(self):
        """Crée la structure de dossiers si elle n'existe pas"""
        for folder in [
            self.data_folder, self.current_data_folder, self.archives_folder,
            self.analysis_folder, self.daily_analysis_folder, self.weekly_analysis_folder, self.monthly_analysis_folder,
            self.podcast_folder, self.weekly_podcast_folder, self.monthly_podcast_folder
        ]:
            os.makedirs(folder, exist_ok=True)
            logger.debug(f"Vérification/création du dossier: {folder}")
    
    def _load_index(self):
        """
        Charge l'index ou crée un nouvel index s'il n'existe pas.
        
        Returns:
            dict: Structure d'index
        """
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Fichier d'index corrompu, création d'un nouvel index")
                return self._create_new_index()
        else:
            logger.info("Fichier d'index non trouvé, création d'un nouvel index")
            return self._create_new_index()
    
    def _create_new_index(self):
        """
        Crée une nouvelle structure d'index.
        
        Returns:
            dict: Structure d'index par défaut
        """
        return {
            "last_updated": datetime.now().isoformat(),
            "data_files": [],
            "analysis_metrics": {
                "last_daily_digest": None,
                "last_weekly_summary": None,
                "last_monthly_report": None
            },
            "podcasts": []
        }
    
    def _save_index(self):
        """Sauvegarde l'index dans le fichier"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def save_collected_data(self, data, timestamp=None):
        """
        Sauvegarde les données collectées et met à jour l'index.
        
        Args:
            data: Données à sauvegarder (liste de dictionnaires)
            timestamp: Horodatage (par défaut: date/heure actuelle)
            
        Returns:
            tuple: (chemin_csv, chemin_json)
        """
        # Utiliser la date/heure actuelle si aucun timestamp n'est fourni
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Créer un DataFrame à partir des données
        df = pd.DataFrame(data)
        
        # Définir les chemins de fichiers
        csv_filename = f"quantum_crypto_data_{timestamp_str}.csv"
        json_filename = f"quantum_crypto_data_{timestamp_str}.json"
        
        csv_path = os.path.join(self.current_data_folder, csv_filename)
        json_path = os.path.join(self.current_data_folder, json_filename)
        
        # Sauvegarder les données
        df.to_csv(csv_path, index=False, encoding='utf-8')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Calculer les statistiques
        stats = {
            "total_items": len(data),
            "scientific_articles": sum(1 for item in data if item.get("type") == "research"),
            "news_articles": sum(1 for item in data if item.get("type") == "news"),
            "unique_sources": len(set(item.get("source", "") for item in data))
        }
        
        # Mettre à jour l'index
        entry = {
            "id": timestamp_str,
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "file_paths": {
                "csv": os.path.join("data", "current", csv_filename),
                "json": os.path.join("data", "current", json_filename)
            },
            "stats": stats,
            "status": "current",
            "analysis_results": []
        }
        
        # Marquer les anciens fichiers comme non courants
        for file_entry in self.index["data_files"]:
            if file_entry["status"] == "current":
                file_entry["status"] = "archived"
        
        # Ajouter la nouvelle entrée
        self.index["data_files"].append(entry)
        
        # Sauvegarder l'index
        self._save_index()
        
        logger.info(f"Données sauvegardées dans {csv_path} et {json_path}")
        
        return csv_path, json_path
    
    def register_analysis_result(self, data_id, analysis_type, file_path, date=None):
        """
        Enregistre un résultat d'analyse dans l'index.
        
        Args:
            data_id: ID des données source (format: YYYYMMDD_HHMMSS)
            analysis_type: Type d'analyse (daily_digest, wordcloud, etc.)
            file_path: Chemin vers le fichier de résultat
            date: Date de l'analyse (par défaut: date actuelle)
        
        Returns:
            bool: Succès de l'opération
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            if isinstance(date, datetime):
                date = date.strftime("%Y-%m-%d")
        
        # Trouver l'entrée correspondante
        found = False
        for file_entry in self.index["data_files"]:
            if file_entry["id"] == data_id:
                found = True
                
                # Vérifier si l'analyse existe déjà
                for analysis in file_entry["analysis_results"]:
                    if analysis["type"] == analysis_type and analysis["date"] == date:
                        # Mettre à jour le chemin
                        analysis["file_path"] = file_path
                        logger.debug(f"Mise à jour du résultat d'analyse existant: {analysis_type} pour {data_id}")
                        break
                else:
                    # Ajouter un nouveau résultat
                    file_entry["analysis_results"].append({
                        "type": analysis_type,
                        "date": date,
                        "file_path": file_path
                    })
                    logger.debug(f"Ajout d'un nouveau résultat d'analyse: {analysis_type} pour {data_id}")
                
                break
        
        if not found:
            logger.warning(f"Impossible de trouver les données avec l'ID {data_id} dans l'index")
            return False
        
        # Mettre à jour les métriques d'analyse
        if analysis_type == "daily_digest":
            self.index["analysis_metrics"]["last_daily_digest"] = date
        elif analysis_type == "weekly_summary":
            self.index["analysis_metrics"]["last_weekly_summary"] = date
        elif analysis_type == "monthly_report":
            self.index["analysis_metrics"]["last_monthly_report"] = date
        
        # Sauvegarder l'index
        self._save_index()
        
        return True
    
    def register_podcast(self, podcast_type, script_path, audio_path, date=None):
        """
        Enregistre un podcast dans l'index.
        
        Args:
            podcast_type: Type de podcast (weekly, monthly)
            script_path: Chemin vers le script du podcast
            audio_path: Chemin vers le fichier audio
            date: Date du podcast (par défaut: date actuelle)
        
        Returns:
            bool: Succès de l'opération
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        elif isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        
        # Ajouter l'entrée de podcast
        self.index["podcasts"].append({
            "type": podcast_type,
            "date": date,
            "script_path": script_path,
            "audio_path": audio_path
        })
        
        # Sauvegarder l'index
        self._save_index()
        
        logger.info(f"Podcast de type {podcast_type} enregistré pour la date {date}")
        
        return True
    
    def get_latest_data_file(self, file_type="json"):
        """
        Récupère le chemin vers le fichier de données le plus récent.
        
        Args:
            file_type: Type de fichier (json ou csv)
        
        Returns:
            str: Chemin vers le fichier ou None si aucun fichier n'est trouvé
        """
        if not self.index["data_files"]:
            logger.warning("Aucun fichier de données trouvé dans l'index")
            return None
        
        # Trouver le fichier le plus récent marqué comme "current"
        for file_entry in reversed(self.index["data_files"]):
            if file_entry["status"] == "current":
                return os.path.join(self.base_path, file_entry["file_paths"][file_type])
        
        # Si aucun fichier "current" n'est trouvé, retourner le plus récent
        latest_entry = self.index["data_files"][-1]
        return os.path.join(self.base_path, latest_entry["file_paths"][file_type])
    
    def get_analysis_by_type(self, analysis_type, date=None):
        """
        Récupère le chemin vers un résultat d'analyse spécifique.
        
        Args:
            analysis_type: Type d'analyse
            date: Date spécifique (par défaut: la plus récente)
        
        Returns:
            str: Chemin vers le fichier ou None si aucun fichier n'est trouvé
        """
        if date is None:
            # Chercher le plus récent
            target_file = None
            target_date = None
            
            for file_entry in self.index["data_files"]:
                for analysis in file_entry["analysis_results"]:
                    if analysis["type"] == analysis_type:
                        if target_date is None or analysis["date"] > target_date:
                            target_date = analysis["date"]
                            target_file = analysis["file_path"]
            
            if target_file:
                return os.path.join(self.base_path, target_file)
            else:
                logger.warning(f"Aucun résultat d'analyse de type {analysis_type} trouvé")
                return None
        else:
            # Chercher pour une date spécifique
            if isinstance(date, datetime):
                date = date.strftime("%Y-%m-%d")
            
            for file_entry in self.index["data_files"]:
                for analysis in file_entry["analysis_results"]:
                    if analysis["type"] == analysis_type and analysis["date"] == date:
                        return os.path.join(self.base_path, analysis["file_path"])
            
            logger.warning(f"Aucun résultat d'analyse de type {analysis_type} trouvé pour la date {date}")
            return None
    
    def archive_old_data(self, days_threshold=30):
        """
        Archive les anciennes données pour libérer de l'espace dans le dossier courant.
        
        Args:
            days_threshold: Nombre de jours avant archivage
        
        Returns:
            int: Nombre de fichiers archivés
        """
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        threshold_str = threshold_date.strftime("%Y-%m-%d")
        
        archived_count = 0
        
        for file_entry in self.index["data_files"]:
            if file_entry["status"] == "archived" and file_entry["date"] < threshold_str:
                # Déplacer les fichiers vers les archives
                for file_type, path in file_entry["file_paths"].items():
                    source_path = os.path.join(self.base_path, path)
                    if os.path.exists(source_path):
                        # Construire le chemin de destination
                        filename = os.path.basename(source_path)
                        dest_path = os.path.join(self.archives_folder, filename)
                        
                        # Déplacer le fichier
                        shutil.move(source_path, dest_path)
                        
                        # Mettre à jour le chemin dans l'index
                        file_entry["file_paths"][file_type] = os.path.join("data", "archives", filename)
                        
                        archived_count += 1
                        logger.debug(f"Fichier archivé: {source_path} -> {dest_path}")
        
        if archived_count > 0:
            self._save_index()
            logger.info(f"{archived_count} fichiers archivés avec succès")
        
        return archived_count
    
    def get_stats(self):
        """
        Fournit des statistiques sur les fichiers gérés.
        
        Returns:
            dict: Statistiques
        """
        stats = {
            "total_data_files": len(self.index["data_files"]),
            "current_data_files": sum(1 for entry in self.index["data_files"] if entry["status"] == "current"),
            "archived_data_files": sum(1 for entry in self.index["data_files"] if entry["status"] == "archived"),
            "total_analysis_results": sum(len(entry["analysis_results"]) for entry in self.index["data_files"]),
            "total_podcasts": len(self.index["podcasts"]),
            "last_update": self.index["last_updated"],
            "analysis_metrics": self.index["analysis_metrics"]
        }
        
        return stats
    
    def search_by_keyword(self, keyword):
        """
        Recherche des fichiers par mot-clé dans les titres et résumés.
        
        Args:
            keyword: Mot-clé à rechercher (insensible à la casse)
        
        Returns:
            list: Liste des fichiers correspondants
        """
        results = []
        keyword = keyword.lower()
        
        for file_entry in self.index["data_files"]:
            # Charger le fichier JSON
            json_path = os.path.join(self.base_path, file_entry["file_paths"]["json"])
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Rechercher dans les données
                    matches = []
                    for item in data:
                        title = item.get("title", "").lower()
                        summary = item.get("summary", "").lower()
                        
                        if keyword in title or keyword in summary:
                            matches.append(item)
                    
                    if matches:
                        results.append({
                            "file_id": file_entry["id"],
                            "date": file_entry["date"],
                            "matches": matches
                        })
                
                except Exception as e:
                    logger.error(f"Erreur lors de la recherche dans {json_path}: {e}")
        
        return results
    
    def rebuild_index(self):
        """
        Reconstruit l'index à partir des fichiers existants.
        Utile en cas de corruption de l'index.
        
        Returns:
            bool: Succès de l'opération
        """
        # Créer un nouvel index
        self.index = self._create_new_index()
        
        # Parcourir les fichiers dans le dossier courant
        for filename in os.listdir(self.current_data_folder):
            if filename.startswith("quantum_crypto_data_") and (filename.endswith(".json") or filename.endswith(".csv")):
                try:
                    # Extraire l'ID à partir du nom de fichier
                    file_id = filename.replace("quantum_crypto_data_", "").split(".")[0]
                    file_date = datetime.strptime(file_id.split("_")[0], "%Y%m%d").strftime("%Y-%m-%d")
                    file_time = datetime.strptime(file_id.split("_")[1], "%H%M%S").strftime("%H:%M:%S")
                    
                    # Vérifier si l'entrée existe déjà
                    for entry in self.index["data_files"]:
                        if entry["id"] == file_id:
                            break
                    else:
                        # Créer une nouvelle entrée
                        csv_filename = f"quantum_crypto_data_{file_id}.csv"
                        json_filename = f"quantum_crypto_data_{file_id}.json"
                        
                        # Calculer les statistiques si le fichier JSON existe
                        stats = {"total_items": 0, "scientific_articles": 0, "news_articles": 0, "unique_sources": 0}
                        json_path = os.path.join(self.current_data_folder, json_filename)
                        if os.path.exists(json_path):
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            stats = {
                                "total_items": len(data),
                                "scientific_articles": sum(1 for item in data if item.get("type") == "research"),
                                "news_articles": sum(1 for item in data if item.get("type") == "news"),
                                "unique_sources": len(set(item.get("source", "") for item in data))
                            }
                        
                        entry = {
                            "id": file_id,
                            "date": file_date,
                            "time": file_time,
                            "file_paths": {
                                "csv": os.path.join("data", "current", csv_filename),
                                "json": os.path.join("data", "current", json_filename)
                            },
                            "stats": stats,
                            "status": "current",
                            "analysis_results": []
                        }
                        
                        self.index["data_files"].append(entry)
                
                except Exception as e:
                    logger.error(f"Erreur lors de la reconstruction de l'index pour {filename}: {e}")
        
        # Parcourir les fichiers dans le dossier d'archives
        for filename in os.listdir(self.archives_folder):
            if filename.startswith("quantum_crypto_data_") and (filename.endswith(".json") or filename.endswith(".csv")):
                try:
                    # Extraire l'ID à partir du nom de fichier
                    file_id = filename.replace("quantum_crypto_data_", "").split(".")[0]
                    file_date = datetime.strptime(file_id.split("_")[0], "%Y%m%d").strftime("%Y-%m-%d")
                    file_time = datetime.strptime(file_id.split("_")[1], "%H%M%S").strftime("%H:%M:%S")
                    
                    # Vérifier si l'entrée existe déjà
                    for entry in self.index["data_files"]:
                        if entry["id"] == file_id:
                            entry["status"] = "archived"
                            if filename.endswith(".csv"):
                                entry["file_paths"]["csv"] = os.path.join("data", "archives", filename)
                            elif filename.endswith(".json"):
                                entry["file_paths"]["json"] = os.path.join("data", "archives", filename)
                            break
                    else:
                        # Créer une nouvelle entrée
                        csv_filename = f"quantum_crypto_data_{file_id}.csv"
                        json_filename = f"quantum_crypto_data_{file_id}.json"
                        
                        entry = {
                            "id": file_id,
                            "date": file_date,
                            "time": file_time,
                            "file_paths": {
                                "csv": os.path.join("data", "archives", csv_filename),
                                "json": os.path.join("data", "archives", json_filename)
                            },
                            "stats": {"total_items": 0, "scientific_articles": 0, "news_articles": 0, "unique_sources": 0},
                            "status": "archived",
                            "analysis_results": []
                        }
                        
                        self.index["data_files"].append(entry)
                
                except Exception as e:
                    logger.error(f"Erreur lors de la reconstruction de l'index pour {filename}: {e}")
        
        # Parcourir les résultats d'analyse
        for folder_name in ["daily", "weekly", "monthly"]:
            folder_path = os.path.join(self.analysis_folder, folder_name)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.startswith(("daily_digest_", "weekly_summary_", "monthly_report_")):
                        try:
                            # Extraire la date
                            date_str = filename.split("_")[-1].split(".")[0]
                            
                            # Déterminer le type d'analyse
                            if filename.startswith("daily_digest_"):
                                analysis_type = "daily_digest"
                                self.index["analysis_metrics"]["last_daily_digest"] = date_str
                            elif filename.startswith("weekly_summary_"):
                                analysis_type = "weekly_summary"
                                self.index["analysis_metrics"]["last_weekly_summary"] = date_str
                            elif filename.startswith("monthly_report_"):
                                analysis_type = "monthly_report"
                                self.index["analysis_metrics"]["last_monthly_report"] = date_str
                            else:
                                continue
                            
                            # Ajouter à l'entrée la plus récente (simplification)
                            if self.index["data_files"]:
                                latest_entry = max(self.index["data_files"], key=lambda x: x["id"])
                                latest_entry["analysis_results"].append({
                                    "type": analysis_type,
                                    "date": date_str,
                                    "file_path": os.path.join("analysis_results", folder_name, filename)
                                })
                        
                        except Exception as e:
                            logger.error(f"Erreur lors de la reconstruction de l'index pour {filename}: {e}")
        
        # Parcourir les podcasts
        for folder_name in ["weekly", "monthly"]:
            folder_path = os.path.join(self.podcast_folder, folder_name)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(".mp3") and filename.startswith(("QuantumCrypto_Weekly_", "QuantumCrypto_Monthly_")):
                        try:
                            # Extraire la date
                            date_str = filename.split("_")[-1].split(".")[0]
                            
                            # Déterminer le type de podcast
                            podcast_type = "weekly" if "Weekly" in filename else "monthly"
                            
                            # Chercher le script correspondant
                            script_filename = f"podcast_script_{date_str}.txt"
                            script_path = os.path.join(self.podcast_folder, folder_name, script_filename)
                            
                            if not os.path.exists(script_path):
                                script_path = None
                            
                            # Ajouter à l'index
                            self.index["podcasts"].append({
                                "type": podcast_type,
                                "date": date_str,
                                "script_path": os.path.join("podcasts", folder_name, script_filename) if script_path else None,
                                "audio_path": os.path.join("podcasts", folder_name, filename)
                            })
                        
                        except Exception as e:
                            logger.error(f"Erreur lors de la reconstruction de l'index pour {filename}: {e}")
        
        # Sauvegarder l'index
        self._save_index()
        
        logger.info("Index reconstruit avec succès")
        
        return True
