"""
Script de test du système de veille technologique sur la cryptographie quantique.
Ce script permet de tester facilement les différents composants du système.
"""

import os
import sys
import time
import argparse
from datetime import datetime

# Ajouter les répertoires source au chemin Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/collectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/analyzers'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/distributors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/podcast'))

def main():
    """Fonction principale qui gère les différents tests"""
    
    parser = argparse.ArgumentParser(description="Tests du système de veille cryptographie quantique")
    parser.add_argument("--component", choices=["collector", "analyzer", "telegram", "podcast", "all"],
                        default="all", help="Composant à tester")
    parser.add_argument("--verbose", action="store_true", help="Afficher les informations détaillées")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Mode verbeux activé - affichage de tous les détails")
    
    print(f"{'='*80}")
    print(f"{'Test du système de veille sur la cryptographie quantique':^80}")
    print(f"{'='*80}")
    
    # Vérifier si l'environnement virtuel est activé
    if "VIRTUAL_ENV" not in os.environ:
        print("ATTENTION: Vous n'êtes pas dans un environnement virtuel.")
        print("Il est recommandé d'activer l'environnement virtuel avant d'exécuter les tests.")
        print("Windows: call venv\\Scripts\\activate.bat")
        print("Linux/Mac: source venv/bin/activate")
        
        user_input = input("Voulez-vous continuer quand même? (y/n): ")
        if user_input.lower() != 'y':
            print("Test annulé.")
            return
    
    # Vérifier la présence du fichier .env
    if not os.path.exists(".env"):
        print("ERREUR: Le fichier .env n'existe pas.")
        print("Veuillez créer un fichier .env à partir du template .env.template")
        print("et y ajouter vos clés API et configurations.")
        return
    
    # Tester les composants sélectionnés
    if args.component in ["collector", "all"]:
        test_collector(args.verbose)
    
    if args.component in ["analyzer", "all"]:
        test_analyzer(args.verbose)
    
    if args.component in ["podcast", "all"]:
        test_podcast(args.verbose)
    
    if args.component in ["telegram", "all"]:
        test_telegram(args.verbose)
    
    print(f"\n{'='*80}")
    print(f"{'Tests terminés':^80}")
    print(f"{'='*80}")

def test_collector(verbose=False):
    """Teste le collecteur de données"""
    print("\n----- Test du collecteur de données -----")
    
    try:
        from collectors.quantum_crypto_scraper import QuantumCryptoScraper
        
        start_time = time.time()
        print("Démarrage de la collecte de données...")
        
        scraper = QuantumCryptoScraper()
        csv_path, json_path = scraper.fetch_all_sources()
        
        duration = time.time() - start_time
        
        print(f"[OK] Collecte terminée en {duration:.2f} secondes")
        print(f"[OK] Données sauvegardées dans:")
        print(f"   - {csv_path}")
        print(f"   - {json_path}")
        
        # Afficher un échantillon des données si verbose
        if verbose and os.path.exists(json_path):
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\nAperçu des données collectées ({len(data)} éléments au total):")
            for i, item in enumerate(data[:3]):
                print(f"\nÉlément {i+1}:")
                print(f"  Titre: {item.get('title', 'N/A')}")
                print(f"  Source: {item.get('source', 'N/A')}")
                print(f"  Date: {item.get('date', 'N/A')}")
                print(f"  Type: {item.get('type', 'N/A')}")
            
            if len(data) > 3:
                print(f"... et {len(data) - 3} autres éléments")
        
        return json_path
    
    except Exception as e:
        print(f"[ERREUR] lors du test du collecteur: {str(e)}")
        return None

def test_analyzer(verbose=False):
    """Teste l'analyseur de données"""
    print("\n----- Test de l'analyseur de données -----")
    
    # Trouver le fichier de données le plus récent
    data_files = [f for f in os.listdir("data") if f.endswith('.json')]
    
    if not data_files:
        print("[ERREUR] Aucun fichier de données trouvé dans le dossier 'data/'")
        print("   Veuillez d'abord exécuter le collecteur de données")
        return None
    
    latest_file = sorted(data_files)[-1]
    data_path = os.path.join("data", latest_file)
    
    try:
        from analyzers.quantum_crypto_analyzer import QuantumCryptoAnalyzer
        
        start_time = time.time()
        print(f"Démarrage de l'analyse des données ({data_path})...")
        
        analyzer = QuantumCryptoAnalyzer(data_path)
        results = analyzer.run_full_analysis()
        
        duration = time.time() - start_time
        
        print(f"[OK] Analyse terminée en {duration:.2f} secondes")
        print(f"[OK] Résultats sauvegardés dans le dossier 'analysis_results/'")
        
        # Afficher un aperçu des résultats si verbose
        if verbose:
            print("\nAperçu des résultats:")
            
            if 'topics' in results:
                print(f"\nThèmes principaux ({len(results['topics'])} au total):")
                for i, topic in enumerate(results['topics']):
                    print(f"  Thème {i+1}: {topic.get('label', 'N/A')}")
                    terms = topic.get('terms', [])
                    if terms:
                        print(f"    Termes: {', '.join(terms[:5])}")
            
            if 'entities' in results:
                print("\nEntités extraites:")
                for entity_type, entities in results['entities'].items():
                    print(f"  {entity_type}: {', '.join(list(entities.keys())[:5])}")
            
            if 'summary' in results:
                print("\nAperçu de la synthèse:")
                summary_lines = results['summary'].split('\n')
                for line in summary_lines[:5]:
                    print(f"  {line}")
                if len(summary_lines) > 5:
                    print("  ...")
        
        return results
    
    except Exception as e:
        print(f"[ERREUR] lors du test de l'analyseur: {str(e)}")
        return None

def test_podcast(verbose=False):
    """Teste le générateur de podcast"""
    print("\n----- Test du générateur de podcast -----")
    
    # Vérifier si des résultats d'analyse sont disponibles
    summary_files = [f for f in os.listdir("analysis_results") if f.startswith('recent_trends_summary')]
    digest_files = [f for f in os.listdir("analysis_results") if f.startswith('daily_digest')]
    
    if not summary_files or not digest_files:
        print("[ERREUR] Fichiers d'analyse nécessaires non trouvés dans 'analysis_results/'")
        print("   Veuillez d'abord exécuter l'analyseur de données")
        return None
    
    try:
        from podcast.podcast_generator import QuantumCryptoPodcast
        
        start_time = time.time()
        print("Démarrage de la génération du podcast...")
        
        podcast = QuantumCryptoPodcast()
        result = podcast.generate_podcast()
        
        duration = time.time() - start_time
        
        if result["status"] == "success":
            print(f"[OK] Génération du podcast terminée en {duration:.2f} secondes")
            print(f"[OK] Script du podcast: {result['script_path']}")
            print(f"[OK] Fichier audio: {result['podcast_path']}")
            print(f"[OK] URL du podcast: {result['podcast_url']}")
            
            # Afficher un aperçu du script si verbose
            if verbose and os.path.exists(result['script_path']):
                with open(result['script_path'], 'r', encoding='utf-8') as f:
                    script = f.read()
                
                print("\nAperçu du script du podcast:")
                script_lines = script.split('\n')
                for line in script_lines[:10]:
                    print(f"  {line}")
                if len(script_lines) > 10:
                    print("  ...")
                
        else:
            print(f"[ERREUR] lors de la génération du podcast: {result['error']}")
        
        return result
    
    except Exception as e:
        print(f"[ERREUR] lors du test du générateur de podcast: {str(e)}")
        return None

def test_telegram(verbose=False):
    """Teste le bot Telegram"""
    print("\n----- Test du bot Telegram -----")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("[ERREUR] TELEGRAM_BOT_TOKEN non défini dans le fichier .env")
            print("   Veuillez ajouter votre token Telegram dans le fichier .env")
            return False
        
        # Test minimal pour vérifier que les imports et la configuration fonctionnent
        from distributors.telegram_bot import QuantumCryptoBot
        
        print("[OK] Configuration du bot Telegram valide")
        print("[INFO] Pour démarrer le bot, exécutez:")
        print("   python main.py --run-once --tasks telegram")
        
        # Ne pas démarrer le bot ici car il bloquerait l'exécution du reste des tests
        
        return True
    
    except Exception as e:
        print(f"[ERREUR] lors du test du bot Telegram: {str(e)}")
        return False

if __name__ == "__main__":
    main()
