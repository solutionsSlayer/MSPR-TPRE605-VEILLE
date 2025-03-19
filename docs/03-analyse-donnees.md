# Module d'Analyse des Données

## Présentation générale

Le module d'analyse des données (`src/analyzers/`) est chargé de traiter, d'organiser et d'extraire des connaissances pertinentes à partir des données collectées sur la cryptographie quantique. Ce module utilise des techniques de traitement du langage naturel (NLP), d'apprentissage automatique et d'intelligence artificielle pour transformer les données brutes en insights actionnables.

## Classe principale : QuantumCryptoAnalyzer

La classe `QuantumCryptoAnalyzer` (définie dans `quantum_crypto_analyzer.py`) coordonne l'ensemble du processus d'analyse. Elle prend en entrée un fichier de données (CSV ou JSON) et produit divers types d'analyses et de visualisations.

### Initialisation et prétraitement

```python
def __init__(self, data_path):
    """Initialise l'analyseur avec le chemin du fichier de données"""
    self.data_path = data_path
    self.results_folder = "analysis_results"
    
    # Charger les données
    if data_path.endswith('.csv'):
        self.data = pd.read_csv(data_path)
    elif data_path.endswith('.json'):
        with open(data_path, 'r') as f:
            self.data = pd.DataFrame(json.load(f))
            
    # Prétraiter les données
    self.preprocess_data()
    
    # Initialiser le modèle spaCy et le client OpenAI
    self.nlp = spacy.load("fr_core_news_sm")
    self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

Le prétraitement inclut le nettoyage des textes, la conversion des formats de date, et la préparation des données pour l'analyse.

## Types d'analyses effectuées

### 1. Clustering des articles

La méthode `perform_clustering()` regroupe les articles similaires en utilisant l'algorithme K-means sur des représentations vectorielles TF-IDF des textes :

```python
def perform_clustering(self, n_clusters=5):
    """Effectue un clustering des articles basé sur leur contenu"""
    # Vectorisation TF-IDF
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(self.data['clean_text'])
    
    # Clustering K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    self.data['cluster'] = kmeans.fit_predict(X)
    
    # Extraire les termes les plus importants par cluster
    feature_names = vectorizer.get_feature_names_out()
    cluster_terms = {}
    
    for i in range(n_clusters):
        indices = self.data[self.data['cluster'] == i].index
        cluster_center = X[indices].mean(axis=0)
        terms_indices = cluster_center.argsort()[0, -10:]
        top_terms = [feature_names[idx] for idx in terms_indices]
        cluster_terms[i] = top_terms
```

Cette analyse permet d'identifier les thèmes principaux dans les articles collectés et de regrouper les contenus similaires.

### 2. Génération de nuage de mots

La méthode `generate_wordcloud()` crée une représentation visuelle des termes les plus fréquents dans l'ensemble des données :

```python
def generate_wordcloud(self):
    """Génère un nuage de mots à partir des textes"""
    # Combiner tous les textes nettoyés
    all_text = ' '.join(self.data['clean_text'])
    
    # Générer le nuage de mots
    wordcloud = WordCloud(width=800, height=400, background_color='white', 
                         max_words=100, contour_width=3, contour_color='steelblue',
                         collocations=False).generate(all_text)
    
    # Sauvegarder l'image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path)
```

Un nuage de mots est une représentation visuelle où la taille de chaque mot est proportionnelle à sa fréquence d'apparition dans le corpus. Cette visualisation permet d'identifier rapidement les concepts dominants dans les données.

### 3. Extraction d'entités nommées

La méthode `extract_entities()` utilise le modèle spaCy pour identifier et catégoriser les entités nommées dans les textes :

```python
def extract_entities(self):
    """Extrait les entités nommées des textes"""
    # Initialiser les dictionnaires pour stocker les entités
    entities = {
        'ORG': [],  # Organisations
        'LOC': [],  # Lieux
        'PER': [],  # Personnes
        'MISC': []  # Divers
    }
    
    # Traiter chaque texte
    for text in self.data['combined_text']:
        doc = self.nlp(text[:10000])
        
        # Extraire les entités
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'LOC', 'PER']:
                entities[ent.label_].append(ent.text)
            else:
                entities['MISC'].append(ent.text)
```

Cette analyse permet d'identifier :
- Les **organisations** (entreprises, universités, laboratoires) actives dans le domaine
- Les **personnes** (chercheurs, dirigeants) influentes
- Les **lieux** (pays, villes) où se concentrent les activités

### 4. Analyse des tendances temporelles

La méthode `analyze_trends()` examine l'évolution du nombre de publications au fil du temps :

```python
def analyze_trends(self):
    """Analyse les tendances temporelles dans les données"""
    # Créer une colonne pour le mois
    self.data['month'] = self.data['date'].dt.to_period('M')
    
    # Compter le nombre d'articles par mois
    monthly_counts = self.data.groupby('month').size()
    
    # Créer un graphique
    plt.figure(figsize=(12, 6))
    monthly_counts.plot(kind='bar', color='steelblue')
    plt.title('Nombre d\'articles par mois')
    plt.xlabel('Mois')
    plt.ylabel('Nombre d\'articles')
```

Cette analyse permet de détecter :
- Les augmentations ou diminutions d'intérêt pour certains sujets
- Les pics d'activité qui peuvent correspondre à des événements importants
- Les tendances cycliques ou saisonnières

### 5. Génération d'insights avec OpenAI

La méthode `generate_ai_insights()` utilise l'API OpenAI pour générer une analyse approfondie des données :

```python
def generate_ai_insights(self):
    """Génère des insights sur les données en utilisant l'API OpenAI"""
    # Préparer un échantillon des données pour l'analyse
    sample_data = self.data.sample(min(20, len(self.data)))
    
    # Créer un résumé des données
    data_summary = "\n".join([
        f"Titre: {row['title']}",
        f"Résumé: {row['summary']}",
        f"Date: {row['date']}",
        f"Source: {row['source']}",
        "---"
    ] for _, row in sample_data.iterrows())
    
    # Définir le prompt
    prompt = f"""
    Analyse les données suivantes sur la cryptographie quantique et fournit:
    1. Les principales tendances et thèmes
    2. Les acteurs clés mentionnés
    3. Les technologies émergentes identifiées
    4. Les défis et opportunités dans le domaine
    5. Des recommandations pour la veille technologique future
    
    Données:
    {data_summary}
    """
    
    # Appeler l'API OpenAI
    response = self.client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un expert en cryptographie quantique."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
```

Cette analyse utilise l'intelligence artificielle pour fournir :
- Une synthèse des tendances principales
- Une identification des acteurs clés
- Une analyse des technologies émergentes
- Des recommandations pour orienter la veille future

## Méthodologie d'analyse complète

La méthode `run_full_analysis()` exécute toutes les analyses dans une séquence coordonnée :

1. Clustering des articles pour identifier les thèmes
2. Génération de nuage de mots pour visualiser les concepts principaux
3. Extraction d'entités pour identifier les acteurs clés
4. Analyse des tendances temporelles
5. Génération d'insights avec l'IA
6. Production d'un rapport de synthèse

## Format des résultats

Les résultats d'analyse sont sauvegardés dans le dossier `analysis_results/` sous divers formats :

- **Fichiers JSON** : Pour les données structurées (clusters, entités, digest quotidien)
- **Fichiers PNG** : Pour les visualisations (nuage de mots, graphiques de tendances)
- **Fichiers TXT** : Pour les analyses textuelles (insights IA, résumé des tendances)
- **Fichiers CSV** : Pour les données tabulaires (thèmes identifiés)

## Structure des sous-dossiers

Les résultats sont organisés par périodicité :
- `daily/` : Analyses quotidiennes (digest journalier)
- `weekly/` : Analyses hebdomadaires (résumé de la semaine)
- `monthly/` : Analyses mensuelles (rapport mensuel)

## Dépendances techniques

Le module d'analyse utilise plusieurs bibliothèques :
- `pandas` et `numpy` pour la manipulation des données
- `scikit-learn` pour le clustering et la vectorisation TF-IDF
- `matplotlib` et `seaborn` pour les visualisations
- `wordcloud` pour la génération de nuages de mots
- `spaCy` pour le traitement du langage naturel
- `OpenAI` pour l'intégration avec les modèles LLM
