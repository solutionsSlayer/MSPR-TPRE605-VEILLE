#!/usr/bin/env python3
"""
Outil de gestion des fichiers pour le système de veille sur la cryptographie quantique.
Permet de gérer, organiser et nettoyer les fichiers du projet.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Ajouter les répertoires source au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("file_manager_tool")

# Importer le gestionnaire de fichiers
from src.utils.file_manager import FileManager

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Outil de gestion des fichiers pour le système de veille")
    
    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")
    
    # Commande: info
    info_parser = subparsers.add_parser("info", help="Afficher des informations sur les fichiers")
    
    # Commande: archive
    archive_parser = subparsers.add_parser("archive", help="Archiver les anciennes données")
    archive_parser.add_argument("--days", type=int, default=30, help="Nombre de jours avant archivage (défaut: 30)")
    
    # Commande: rebuild
    rebuild_parser = subparsers.add_parser("rebuild", help="Reconstruire l'index")
    
    # Commande: search
    search_parser = subparsers.add_parser("search", help="Rechercher des fichiers par mot-clé")
    search_parser.add_argument("keyword", help="Mot-clé à rechercher")
    
    # Commande: organize
    organize_parser = subparsers.add_parser("organize", help="Organiser les fichiers selon la nouvelle structure")
    
    # Commande: cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Nettoyer les fichiers temporaires et duplicats")
    
    args = parser.parse_args()
    
    # Créer une instance du gestionnaire de fichiers
    file_manager = FileManager()
    
    # Exécuter la commande demandée
    if args.command == "info":
        display_info(file_manager)
    elif args.command == "archive":
        archive_old_data(file_manager, args.days)
    elif args.command == "rebuild":
        rebuild_index(file_manager)
    elif args.command == "search":
        search_files(file_manager, args.keyword)
    elif args.command == "organize":
        organize_files(file_manager)
    elif args.command == "cleanup":
        cleanup_files(file_manager)
    else:
        parser.print_help()

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

def archive_old_data(file_manager, days):
    """Archive les anciennes données"""
    print(f"\nArchivage des données de plus de {days} jours...")
    
    count = file_manager.archive_old_data(days)
    
    print(f"\n{count} fichiers ont été archivés avec succès.")

def rebuild_index(file_manager):
    """Reconstruit l'index"""
    print("\nReconstruction de l'index...")
    
    success = file_manager.rebuild_index()
    
    if success:
        print("\nL'index a été reconstruit avec succès.")
    else:
        print("\nErreur lors de la reconstruction de l'index.")

def search_files(file_manager, keyword):
    """Recherche des fichiers par mot-clé"""
    print(f"\nRecherche de fichiers contenant '{keyword}'...")
    
    results = file_manager.search_by_keyword(keyword)
    
    if not results:
        print("\nAucun résultat trouvé.")
    else:
        print(f"\n{len(results)} fichiers contiennent des correspondances:")
        
        for result in results:
            print(f"\nFichier: quantum_crypto_data_{result['file_id']}")
            print(f"Date: {result['date']}")
            print(f"Correspondances: {len(result['matches'])} articles")
            
            for i, match in enumerate(result['matches'][:5], 1):
                print(f"  {i}. {match.get('title', 'Sans titre')} ({match.get('source', 'Source inconnue')})")
            
            if len(result['matches']) > 5:
                print(f"  ... et {len(result['matches']) - 5} autres correspondances")

def organize_files(file_manager):
    """Organise les fichiers selon la nouvelle structure"""
    print("\nRéorganisation des fichiers...")
    
    # Réorganiser les fichiers de données
    data_folder = os.path.join(file_manager.base_path, "data")
    current_folder = os.path.join(data_folder, "current")
    archives_folder = os.path.join(data_folder, "archives")
    
    # Déplacer les fichiers de données actuels vers le dossier "current"
    files_moved = 0
    for filename in os.listdir(data_folder):
        if filename.startswith("quantum_crypto_data_") and os.path.isfile(os.path.join(data_folder, filename)):
            src = os.path.join(data_folder, filename)
            dst = os.path.join(current_folder, filename)
            
            if not os.path.exists(dst):
                import shutil
                shutil.move(src, dst)
                files_moved += 1
    
    # Réorganiser les résultats d'analyse
    analysis_folder = os.path.join(file_manager.base_path, "analysis_results")
    daily_folder = os.path.join(analysis_folder, "daily")
    weekly_folder = os.path.join(analysis_folder, "weekly")
    monthly_folder = os.path.join(analysis_folder, "monthly")
    visualizations_folder = os.path.join(analysis_folder, "visualizations")
    
    # S'assurer que le dossier visualizations existe
    os.makedirs(visualizations_folder, exist_ok=True)
    
    # Déplacer les fichiers d'analyse vers les dossiers appropriés
    analysis_moved = 0
    visualizations_moved = 0
    
    for filename in os.listdir(analysis_folder):
        if os.path.isfile(os.path.join(analysis_folder, filename)):
            src = os.path.join(analysis_folder, filename)
            dst_folder = None
            
            if filename.startswith("daily_digest_"):
                dst_folder = daily_folder
            elif filename.startswith("weekly_summary_"):
                dst_folder = weekly_folder
            elif filename.startswith("monthly_report_"):
                dst_folder = monthly_folder
            # Gestion des visualisations et données permanentes
            elif (filename.endswith((".png", ".jpg", ".svg", ".csv", ".json")) and
                  not filename.startswith(("daily_", "weekly_", "monthly_", "recent_", "index"))):
                dst_folder = visualizations_folder
                visualizations_moved += 1
            
            if dst_folder:
                dst = os.path.join(dst_folder, filename)
                if not os.path.exists(dst):
                    import shutil
                    shutil.move(src, dst)
                    if dst_folder != visualizations_folder:
                        analysis_moved += 1
    
    # Reconstruire l'index
    file_manager.rebuild_index()
    
    print(f"\n{files_moved} fichiers de données, {analysis_moved} résultats d'analyse et {visualizations_moved} visualisations ont été réorganisés.")
    print("L'index a été mis à jour pour refléter la nouvelle organisation.")

def cleanup_files(file_manager):
    """Nettoie les fichiers temporaires et duplicats"""
    print("\nNettoyage des fichiers temporaires et duplicats...")
    
    # Nettoyer les fichiers temporaires
    temp_removed = 0
    for root, dirs, files in os.walk(file_manager.base_path):
        for filename in files:
            if filename.endswith((".tmp", ".temp")) or filename.startswith("temp_"):
                try:
                    os.remove(os.path.join(root, filename))
                    temp_removed += 1
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {filename}: {e}")
    
    # Identifier et supprimer les duplicats dans les résultats d'analyse
    # (Simplification: on considère que les fichiers avec le même nom de base sont des duplicats)
    duplicates_removed = 0
    analysis_files = {}
    
    for root, dirs, files in os.walk(os.path.join(file_manager.base_path, "analysis_results")):
        for filename in files:
            base_name = filename.split("_")[0]  # daily, weekly, monthly
            
            if base_name in ["daily", "weekly", "monthly"]:
                full_path = os.path.join(root, filename)
                
                if base_name not in analysis_files:
                    analysis_files[base_name] = []
                
                analysis_files[base_name].append((full_path, os.path.getmtime(full_path)))
    
    # Garder uniquement les 5 plus récents pour chaque type
    for base_name, files in analysis_files.items():
        if len(files) > 5:
            # Trier par date de modification (le plus récent en premier)
            sorted_files = sorted(files, key=lambda x: x[1], reverse=True)
            
            # Supprimer les plus anciens (au-delà des 5 plus récents)
            for path, _ in sorted_files[5:]:
                try:
                    os.remove(path)
                    duplicates_removed += 1
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {path}: {e}")
    
    # Reconstruire l'index
    file_manager.rebuild_index()
    
    print(f"\n{temp_removed} fichiers temporaires et {duplicates_removed} duplicats ont été supprimés.")
    print("L'index a été mis à jour pour refléter les changements.")

if __name__ == "__main__":
    main()