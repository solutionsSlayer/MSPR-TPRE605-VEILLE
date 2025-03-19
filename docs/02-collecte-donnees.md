# Module de Collecte de Données

## Présentation générale

Le module de collecte de données (`src/collectors/`) est responsable de l'extraction d'informations depuis diverses sources externes concernant la cryptographie quantique. Il constitue le point d'entrée du pipeline de veille technologique, fournissant les données brutes qui seront ensuite analysées.

## Classe principale : QuantumCryptoScraper

La classe `QuantumCryptoScraper` (définie dans `quantum_crypto_scraper.py`) orchestre l'ensemble du processus de collecte. Elle implémente plusieurs méthodes pour extraire des informations de différentes sources.

### Méthodes principales

#### `fetch_all_sources_data()`

Cette méthode coordonne la collecte de données depuis toutes les sources configurées et retourne les données brutes sans les sauvegarder.

```python
def fetch_all_sources_data(self):
    """Récupère les données de toutes les sources sans les sauvegarder"""
    all_data = []
    
    # Collecte depuis les flux RSS
    rss_articles = self.fetch_rss_feeds()
    all_data.extend(rss_articles)
    
    # Collecte depuis arXiv
    arxiv_papers = self.fetch_arxiv_papers()
    all_data.extend(arxiv_papers)
    
    # Collecte depuis les sites d'actualités
    news_articles = self.fetch_news_sites()
    all_data.extend(news_articles)
    
    return all_data
```

#### `fetch_all_sources()`

Cette méthode utilise `fetch_all_sources_data()` pour collecter les données puis les sauvegarde dans les formats CSV et JSON.

#### `fetch_rss_feeds()`

Extrait les articles pertinents depuis les flux RSS configurés.

#### `fetch_arxiv_papers()`

Recherche et extrait les articles scientifiques depuis arXiv concernant la cryptographie quantique.

#### `fetch_news_sites()`

Scrape les sites d'actualités spécialisés pour en extraire les articles pertinents.

## Sources de données

Le système collecte des informations depuis plusieurs types de sources :

### Flux RSS

Les flux RSS permettent de suivre les actualités publiées sur des sites spécialisés :
- Quantum Computing Report
- Inside Quantum Technology
- Quantum Zeitgeist

### Articles scientifiques (arXiv)

La plateforme arXiv est utilisée pour suivre les publications scientifiques. La recherche est effectuée avec les mots-clés suivants :
- "quantum cryptography"
- "quantum key distribution"
- "post-quantum cryptography"
- "quantum-resistant"

### Sites d'actualités spécialisés

Le scraping de sites web est utilisé pour collecter des informations depuis :
- The Quantum Insider
- Quantum Computing Report (section cryptographie quantique)

### Conférences

Le système suit également les actualités liées aux conférences majeures :
- QCrypt
- PQCrypto
- Eurocrypt
- Crypto

## Structure des données collectées

Chaque élément collecté est structuré sous forme de dictionnaire avec les champs suivants :

| Champ | Description | Exemple |
|-------|-------------|---------|
| `title` | Titre de l'article ou de la publication | "Advances in Quantum Key Distribution" |
| `source` | Source de l'information | "arXiv", "Quantum Computing Report" |
| `url` | Lien vers le contenu original | "https://example.com/article" |
| `date` | Date de publication (format YYYY-MM-DD) | "2025-03-15" |
| `summary` | Résumé du contenu | "This paper presents a new approach to..." |
| `type` | Type de contenu | "research", "news" |
| `authors` | Auteurs (pour les articles scientifiques) | "Smith, J., Kumar, A." |

## Filtrage et pertinence

Le système utilise une méthode `_is_relevant()` pour filtrer les contenus et ne conserver que ceux liés à la cryptographie quantique. Cette méthode recherche des termes spécifiques dans les titres et résumés :

```python
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
```

## Gestion des erreurs

Le module implémente une gestion robuste des erreurs pour assurer la continuité de service même en cas de problème avec certaines sources :

- Chaque source est traitée indépendamment
- Les exceptions sont capturées et journalisées
- En cas d'échec complet, un jeu de données minimal est généré pour les tests

## Extensibilité

Le système est conçu pour être facilement extensible :

1. Pour ajouter une nouvelle source RSS, il suffit de l'ajouter à la liste dans `_load_sources()`
2. Pour ajouter un nouveau mot-clé de recherche, il suffit de l'ajouter à la liste `scientific_keywords`
3. Pour ajouter un nouveau site à scraper, il faut l'ajouter à la liste `news_sites` avec son sélecteur CSS

## Dépendances externes

Le module de collecte utilise plusieurs bibliothèques :
- `feedparser` pour l'analyse des flux RSS
- `requests` et `BeautifulSoup4` pour le scraping web
- `arxiv` pour l'accès à l'API arXiv
- `pandas` pour la manipulation des données
