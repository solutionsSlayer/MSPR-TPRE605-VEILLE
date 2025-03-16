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

class QuantumCryptoScraper:
    def __init__(self):
        self.data_folder = "data"
        os.makedirs(self.data_folder, exist_ok=True)
        self.sources = self._load_sources()
        
    def _load_sources(self):
        """Charge les sources depuis un fichier de configuration"""
        sources = {
            "rss_feeds": [
                {"name": "MIT Technology Review Quantum", "url": "https://www.technologyreview.com/topic/computing/quantum-computing/feed"},
                {"name": "Quantum Computing Report", "url": "https://quantumcomputingreport.com/feed/"},
                {"name": "IEEE Spectrum Quantum", "url": "https://spectrum.ieee.org/tag/quantum/feed"}
            ],
            "scientific_keywords": [
                "quantum cryptography", "quantum key distribution", 
                "post-quantum cryptography", "quantum-resistant"
            ],
            "news_sites": [
                {"name": "The Quantum Insider", "url": "https://thequantuminsider.com/category/quantum-cryptography/"},
                {"name": "Quantum Computing Report", "url": "https://quantumcomputingreport.com/category/quantum-cryptography/"}
            ],
            "conferences": [
                "QCrypt", "PQCrypto", "Eurocrypt", "Crypto"
            ]
        }
        return sources
    
    def fetch_rss_feeds(self):
        """Récupère les articles depuis les flux RSS"""
        articles = []
        for feed in tqdm(self.sources["rss_feeds"], desc="Parsing RSS feeds"):
            try:
                parsed_feed = feedparser.parse(feed["url"])
                for entry in parsed_feed.entries:
                    if self._is_relevant(entry.title + " " + entry.summary):
                        articles.append({
                            "title": entry.title,
                            "source": feed["name"],
                            "url": entry.link,
                            "date": datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d"),
                            "summary": entry.summary,
                            "type": "news"
                        })
            except Exception as e:
                print(f"Error fetching {feed['name']}: {e}")
        
        return articles
    
    def fetch_arxiv_papers(self, max_results=50):
        """Récupère les articles scientifiques depuis arXiv"""
        papers = []
        
        for keyword in tqdm(self.sources["scientific_keywords"], desc="Searching arXiv"):
            search = arxiv.Search(
                query=keyword,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            for result in search.results():
                papers.append({
                    "title": result.title,
                    "source": "arXiv",
                    "url": result.pdf_url,
                    "date": result.published.strftime("%Y-%m-%d"),
                    "summary": result.summary,
                    "authors": ", ".join([author.name for author in result.authors]),
                    "type": "research"
                })
                
        return papers
    
    def fetch_news_sites(self):
        """Scrape les sites d'actualités sur la cryptographie quantique"""
        articles = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        for site in tqdm(self.sources["news_sites"], desc="Scraping news sites"):
            try:
                response = requests.get(site["url"], headers=headers)
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Cette partie doit être adaptée pour chaque site spécifique
                # Exemple pour un blog WordPress typique
                for article in soup.select("article"):
                    title_elem = article.select_one("h2")
                    link_elem = article.select_one("a")
                    date_elem = article.select_one(".date, .posted-on")
                    summary_elem = article.select_one(".entry-summary, .excerpt")
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        link = link_elem["href"]
                        date = date_elem.text.strip() if date_elem else "N/A"
                        summary = summary_elem.text.strip() if summary_elem else ""
                        
                        if self._is_relevant(title + " " + summary):
                            articles.append({
                                "title": title,
                                "source": site["name"],
                                "url": link,
                                "date": date,
                                "summary": summary,
                                "type": "news"
                            })
            except Exception as e:
                print(f"Error scraping {site['name']}: {e}")
                
        return articles
    
    def _is_relevant(self, text):
        """Vérifie si le texte est pertinent pour la cryptographie quantique"""
        relevant_terms = [
            "quantum cryptography", "quantum key", "qkd", "post-quantum", 
            "quantum-resistant", "quantum security", "quantum encryption",
            "quantum random", "quantum safe"
        ]
        
        text_lower = text.lower()
        return any(term in text_lower for term in relevant_terms)
    
    def fetch_all_sources(self):
        """Récupère les données de toutes les sources et les sauvegarde"""
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
        
        # Sauvegarder les données collectées
        df = pd.DataFrame(all_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.data_folder, f"quantum_crypto_data_{timestamp}.csv")
        df.to_csv(file_path, index=False)
        
        # Sauvegarder également en JSON pour préserver la structure
        json_path = os.path.join(self.data_folder, f"quantum_crypto_data_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(all_data, f, indent=2)
            
        print(f"Saved {len(all_data)} items to {file_path} and {json_path}")
        return file_path, json_path

if __name__ == "__main__":
    scraper = QuantumCryptoScraper()
    csv_path, json_path = scraper.fetch_all_sources()
    print(f"Data collection completed. Files saved to:\n- {csv_path}\n- {json_path}")