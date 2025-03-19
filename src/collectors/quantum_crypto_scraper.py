import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import arxiv
import time
import json
import os
from tqdm import tqdm
import logging
from urllib.parse import urljoin

class QuantumCryptoScraper:
    def __init__(self):
        self.data_folder = "data"
        os.makedirs(self.data_folder, exist_ok=True)
        self.sources = self._load_sources()
        
        # Configuration de l'agent utilisateur pour éviter les blocages
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        
        # Configuration du timeout pour les requêtes
        self.timeout = 15
        
    def _load_sources(self):
        """Charge les sources depuis un fichier de configuration"""
        sources = {
            "rss_feeds": [
                {"name": "Quantum Computing Report", "url": "https://quantumcomputingreport.com/feed/"},
                {"name": "Inside Quantum Technology", "url": "https://www.insidequantumtechnology.com/feed/"},
                {"name": "Quantum Zeitgeist", "url": "https://quantumzeitgeist.com/feed/"}
            ],
            "scientific_keywords": [
                "quantum cryptography", "quantum key distribution", 
                "post-quantum cryptography", "quantum-resistant"
            ],
            "news_sites": [
                {"name": "The Quantum Insider", "url": "https://thequantuminsider.com/category/quantum-cryptography/", "selector": "article"},
                {"name": "Quantum Computing Report", "url": "https://quantumcomputingreport.com/category/quantum-cryptography/", "selector": "article"}
            ],
            "conferences": [
                "QCrypt", "PQCrypto", "Eurocrypt", "Crypto"
            ]
        }
        return sources
    
    def fetch_rss_feeds(self):
        """Récupère les articles depuis les flux RSS"""
        articles = []
        print("Récupération des articles depuis les flux RSS...")
        
        for feed in tqdm(self.sources["rss_feeds"], desc="Parsing RSS feeds"):
            try:
                parsed_feed = feedparser.parse(feed["url"])
                
                # Vérifier si le feed a été correctement analysé
                if hasattr(parsed_feed, 'status') and parsed_feed.status != 200:
                    print(f"[AVERTISSEMENT] Erreur lors de l'accès à {feed['name']}: statut {parsed_feed.status}")
                    continue
                    
                if not hasattr(parsed_feed, 'entries') or len(parsed_feed.entries) == 0:
                    print(f"[AVERTISSEMENT] Aucune entrée trouvée dans le flux {feed['name']}")
                    continue
                
                # Parcourir les entrées du flux RSS
                for entry in parsed_feed.entries:
                    try:
                        # Vérifier si les champs requis existent
                        if not hasattr(entry, 'title') or not hasattr(entry, 'link'):
                            continue
                            
                        # Obtenir le résumé s'il existe, sinon utiliser une chaîne vide
                        summary = entry.summary if hasattr(entry, 'summary') else ""
                        
                        # Vérifier la pertinence
                        if self._is_relevant(entry.title + " " + summary):
                            # Traiter la date de publication
                            pub_date = None
                            if hasattr(entry, 'published'):
                                try:
                                    # Essayer différents formats de date
                                    try:
                                        pub_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                                    except ValueError:
                                        try:
                                            pub_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                                        except ValueError:
                                            pub_date = datetime.strptime(entry.published[:25], "%a, %d %b %Y %H:%M:%S")
                                except:
                                    # En cas d'échec, utiliser la date actuelle
                                    pub_date = datetime.now()
                            else:
                                pub_date = datetime.now()
                                
                            # Formater la date
                            date_str = pub_date.strftime("%Y-%m-%d")
                            
                            # Ajouter l'article
                            articles.append({
                                "title": entry.title,
                                "source": feed["name"],
                                "url": entry.link,
                                "date": date_str,
                                "summary": summary,
                                "type": "news"
                            })
                    except Exception as entry_e:
                        print(f"Erreur lors du traitement d'une entrée de {feed['name']}: {entry_e}")
                        continue
                    
                print(f"Récupéré {len(articles)} articles depuis {feed['name']}")
                
            except Exception as e:
                print(f"Erreur lors de la récupération de {feed['name']}: {e}")
        
        return articles
    
    def fetch_arxiv_papers(self, max_results=30):
        """Récupère les articles scientifiques depuis arXiv"""
        papers = []
        all_ids = set()  # Pour éviter les doublons
        
        for keyword in tqdm(self.sources["scientific_keywords"], desc="Searching arXiv"):
            try:
                search = arxiv.Search(
                    query=keyword,
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                
                for result in search.results():
                    # Éviter les doublons
                    if result.entry_id in all_ids:
                        continue
                    
                    all_ids.add(result.entry_id)
                    
                    # Extraire les informations
                    try:
                        papers.append({
                            "title": result.title,
                            "source": "arXiv",
                            "url": result.pdf_url,
                            "date": result.published.strftime("%Y-%m-%d"),
                            "summary": result.summary,
                            "authors": ", ".join([author.name for author in result.authors]),
                            "type": "research"
                        })
                    except Exception as paper_e:
                        print(f"Erreur lors du traitement d'un article arXiv: {paper_e}")
                        continue
                
                print(f"Récupéré {len(papers)} articles pour le mot-clé '{keyword}'")
                # Pause pour éviter de surcharger l'API
                time.sleep(1)
                
            except Exception as e:
                print(f"Erreur lors de la recherche arXiv pour '{keyword}': {e}")
        
        print(f"Total de {len(papers)} articles uniques récupérés depuis arXiv")
        return papers
    
    def fetch_news_sites(self):
        """Scrape les sites d'actualités sur la cryptographie quantique"""
        articles = []
        
        for site in tqdm(self.sources["news_sites"], desc="Scraping news sites"):
            try:
                # Faire la requête avec timeout et headers appropriés
                response = requests.get(
                    site["url"], 
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                # Vérifier le statut de la requête
                response.raise_for_status()
                
                # Utiliser BeautifulSoup pour analyser le HTML
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Utiliser le sélecteur spécifique au site
                selector = site.get("selector", "article")
                article_elements = soup.select(selector)
                
                if not article_elements:
                    print(f"[AVERTISSEMENT] Aucun article trouvé sur {site['name']} avec le sélecteur '{selector}'")
                    print(f"Essai avec un sélecteur alternatif...")
                    # Essayer avec des sélecteurs alternatifs
                    alternative_selectors = ["article", ".post", ".entry", ".article", ".blog-post"]
                    for alt_selector in alternative_selectors:
                        article_elements = soup.select(alt_selector)
                        if article_elements:
                            print(f"Sélecteur alternatif '{alt_selector}' a fonctionné!")
                            break
                
                # Parcourir les articles trouvés
                for article in article_elements:
                    try:
                        # Rechercher les éléments de l'article avec plusieurs sélecteurs possibles
                        title_elem = article.select_one("h1, h2, h3, .entry-title, .post-title")
                        link_elem = article.select_one("a")
                        date_elem = article.select_one(".date, .posted-on, .entry-date, time")
                        summary_elem = article.select_one(".entry-summary, .excerpt, .post-excerpt, .summary, p")
                        
                        if title_elem and link_elem:
                            title = title_elem.text.strip()
                            
                            # Traiter l'URL
                            link = link_elem["href"]
                            if not link.startswith(('http:', 'https:')):
                                # URL relative, la rendre absolue
                                link = urljoin(site["url"], link)
                            
                            # Extraire la date
                            date = "N/A"
                            if date_elem:
                                date = date_elem.text.strip()
                                # Tenter de convertir en format standard si c'est une chaîne de date
                                try:
                                    if date != "N/A":
                                        # Essayer différents formats courants
                                        date_formats = [
                                            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", 
                                            "%B %d, %Y", "%d %B %Y"
                                        ]
                                        for format in date_formats:
                                            try:
                                                parsed_date = datetime.strptime(date, format)
                                                date = parsed_date.strftime("%Y-%m-%d")
                                                break
                                            except ValueError:
                                                continue
                                except:
                                    # Garder la chaîne originale en cas d'échec
                                    pass
                            
                            # Extraire le résumé
                            summary = ""
                            if summary_elem:
                                summary = summary_elem.text.strip()
                            
                            # Vérifier la pertinence
                            if self._is_relevant(title + " " + summary):
                                articles.append({
                                    "title": title,
                                    "source": site["name"],
                                    "url": link,
                                    "date": date,
                                    "summary": summary,
                                    "type": "news"
                                })
                    except Exception as article_e:
                        print(f"Erreur lors du traitement d'un article sur {site['name']}: {article_e}")
                        continue
                
                print(f"Récupéré {len(articles)} articles depuis {site['name']}")
                
            except requests.RequestException as req_e:
                print(f"Erreur de requête pour {site['name']}: {req_e}")
            except Exception as e:
                print(f"Erreur lors du scraping de {site['name']}: {e}")
                
        return articles
    
    def _is_relevant(self, text):
        """Vérifie si le texte est pertinent pour la cryptographie quantique"""
        relevant_terms = [
            "quantum cryptography", "quantum key", "qkd", "post-quantum", 
            "quantum-resistant", "quantum security", "quantum encryption",
            "quantum random", "quantum safe", "cryptographie quantique",
            "sécurité quantique", "chiffrement quantique", "cryptographie post-quantique"
        ]
        
        text_lower = text.lower()
        return any(term in text_lower for term in relevant_terms)
    
    def fetch_all_sources_data(self):
        """Récupère les données de toutes les sources sans les sauvegarder"""
        print("Starting data collection...")
        
        all_data = []
        
        # Collecter depuis les flux RSS
        rss_articles = self.fetch_rss_feeds()
        all_data.extend(rss_articles)
        print(f"Collected {len(rss_articles)} articles from RSS feeds")
        
        # Collecter depuis arXiv
        arxiv_papers = self.fetch_arxiv_papers()
        all_data.extend(arxiv_papers)
        print(f"Collected {len(arxiv_papers)} papers from arXiv")
        
        # Collecter depuis les sites d'actualités
        news_articles = self.fetch_news_sites()
        all_data.extend(news_articles)
        print(f"Collected {len(news_articles)} articles from news sites")
        
        # Gérer les cas où aucune donnée n'est collectée
        if not all_data:
            print("Aucune donnée collectée! Création d'un jeu de données minimal pour tests.")
            # Créer des données de test minimales
            test_data = [
                {
                    "title": "Exemple d'article sur la cryptographie quantique",
                    "source": "Test Source",
                    "url": "https://example.com/test-article",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "summary": "Ceci est un exemple d'article sur la cryptographie quantique créé pour les tests.",
                    "type": "news"
                },
                {
                    "title": "Recherche sur la distribution quantique de clés",
                    "source": "Test Research",
                    "url": "https://example.com/test-research",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "summary": "Exemple de recherche sur la QKD pour les tests.",
                    "authors": "Author Test",
                    "type": "research"
                }
            ]
            all_data = test_data
        
        return all_data

    def fetch_all_sources(self):
        """Récupère les données de toutes les sources et les sauvegarde"""
        print("Starting data collection...")
        
        # Utiliser la méthode fetch_all_sources_data pour collecter les données
        all_data = self.fetch_all_sources_data()
        
        # Sauvegarder les données collectées
        df = pd.DataFrame(all_data)
        
        # Créer le timestamp pour les noms de fichiers
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarder en CSV
        file_path = os.path.join(self.data_folder, f"quantum_crypto_data_{timestamp}.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        # Sauvegarder en JSON
        json_path = os.path.join(self.data_folder, f"quantum_crypto_data_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
            
        print(f"Saved {len(all_data)} items to {file_path} and {json_path}")
        return file_path, json_path

if __name__ == "__main__":
    scraper = QuantumCryptoScraper()
    csv_path, json_path = scraper.fetch_all_sources()
    print(f"Data collection completed. Files saved to:\n- {csv_path}\n- {json_path}")
