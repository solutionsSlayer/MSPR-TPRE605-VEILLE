#!/usr/bin/env python3
"""
Script simple pour exécuter l'organisation des fichiers.
Ce script utilise le gestionnaire de fichiers amélioré pour organiser tous les fichiers,
y compris les visualisations et données permanentes.
"""

import os
import sys
import shutil
import logging

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("organize_files")

def main():
    """
    Fonction principale qui organise tous les fichiers du projet
    """
    print("=== Organisation des fichiers du système de veille sur la cryptographie quantique ===")
    
    # Chemins des dossiers
    base_path = os.path.dirname(os.path.abspath(__file__))
    analysis_folder = os.path.join(base_path, "analysis_results")
    daily_folder = os.path.join(analysis_folder, "daily")
    weekly_folder = os.path.join(analysis_folder, "weekly")
    monthly_folder = os.path.join(analysis_folder, "monthly")
    visualizations_folder = os.path.join(analysis_folder, "visualizations")
    
    # S'assurer que tous les dossiers existent
    for folder in [daily_folder, weekly_folder, monthly_folder, visualizations_folder]:
        os.makedirs(folder, exist_ok=True)
    
    # Liste des fichiers à déplacer vers le dossier visualizations
    visualization_files = [
        "content_type_distribution.png",
        "entities.json",
        "publications_over_time.png",
        "sources_distribution.png",
        "title_wordcloud.png",
        "topics.csv"
    ]
    
    # Déplacer les fichiers vers le dossier visualizations
    files_moved = 0
    
    for filename in visualization_files:
        src = os.path.join(analysis_folder, filename)
        dst = os.path.join(visualizations_folder, filename)
        
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.move(src, dst)
                files_moved += 1
                print(f"Déplacé: {filename} → visualizations/")
            except Exception as e:
                logger.error(f"Erreur lors du déplacement de {filename}: {e}")
    
    # Déplacer les fichiers journaliers, hebdomadaires et mensuels
    analysis_patterns = {
        "daily_digest_": daily_folder,
        "weekly_summary_": weekly_folder,
        "monthly_report_": monthly_folder
    }
    
    for filename in os.listdir(analysis_folder):
        if os.path.isfile(os.path.join(analysis_folder, filename)):
            for pattern, folder in analysis_patterns.items():
                if filename.startswith(pattern):
                    src = os.path.join(analysis_folder, filename)
                    dst = os.path.join(folder, filename)
                    
                    if not os.path.exists(dst):
                        try:
                            shutil.move(src, dst)
                            files_moved += 1
                            print(f"Déplacé: {filename} → {os.path.basename(folder)}/")
                        except Exception as e:
                            logger.error(f"Erreur lors du déplacement de {filename}: {e}")
    
    print(f"\nOrganisation terminée. {files_moved} fichiers ont été déplacés.")
    print("Tous les fichiers sont maintenant correctement placés dans leurs dossiers respectifs.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
