import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import spacy
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class QuantumCryptoAnalyzer:
    def __init__(self, data_path):
        """
        Initialise l'analyseur avec le chemin du fichier de données
        """
        self.data_path = data_path
        self.results_folder = "analysis_results"
        os.makedirs(self.results_folder, exist_ok=True)
        
        # Charger les données
        if data_path.endswith('.csv'):
            self.data = pd.read_csv(data_path)
        elif data_path.endswith('.json'):
            with open(data_path, 'r') as f:
                self.data = pd.DataFrame(json.load(f))
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON.")
        
        # Prétraiter les données
        self.preprocess_data()
        
        # Charger le modèle spaCy pour l'extraction d'entités
        self.nlp = spacy.load("fr_core_news_sm")
        
        # Initialiser le client OpenAI pour la synthèse
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def preprocess_data(self):
        """Prétraite les données pour l'analyse"""
        # Convertir les dates en format datetime
        self.data['date'] = pd.to_datetime(self.data['date'], errors='coerce')
        
        # Filtrer les données des 90 derniers jours
        latest_date = self.data['date'].max()
        cutoff_date = latest_date - timedelta(days=90)
        self.recent_data = self.data[self.data['date'] >= cutoff_date]
        
        # S'assurer que les colonnes textuelles sont des chaînes
        for col in ['title', 'summary']:
            if col in self.data.columns:
                self.data[col] = self.data[col].fillna('').astype(str)
                
        # Combiner titre et résumé pour l'analyse
        self.data['full_text'] = self.data['title'] + ' ' + self.data['summary']
    
    def extract_topics(self, num_topics=5, num_words=10):
        """Extrait les principaux sujets à l'aide de TF-IDF et K-means"""
        print("Extracting main topics...")
        
        # Création de la matrice TF-IDF
        tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = tfidf_vectorizer.fit_transform(self.data['full_text'])
        
        # Clustering avec K-means
        kmeans = KMeans(n_clusters=num_topics, random_state=42)
        kmeans.fit(tfidf_matrix)
        
        # Obtenir les termes les plus importants pour chaque cluster
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
        terms = tfidf_vectorizer.get_feature_names_out()
        
        topics = []
        for i in range(num_topics):
            topic_terms = [terms[ind] for ind in order_centroids[i, :num_words]]
            topics.append({
                'id': i,
                'terms': topic_terms,
                'label': self._generate_topic_label(topic_terms)
            })
            
            print(f"Topic {i+1}: {', '.join(topic_terms)}")
        
        # Ajouter les étiquettes de cluster aux données
        self.data['cluster'] = kmeans.labels_
        
        # Sauvegarder les résultats
        topics_df = pd.DataFrame(topics)
        topics_path = os.path.join(self.results_folder, "topics.csv")
        topics_df.to_csv(topics_path, index=False)
        
        return topics
    
    def _generate_topic_label(self, terms):
        """Génère une étiquette descriptive pour un sujet à partir de ses termes"""
        # Utiliser LLM pour générer une étiquette significative
        prompt = f"Générer un titre court (3-5 mots) pour un sujet de cryptographie quantique basé sur ces termes: {', '.join(terms)}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant spécialisé en cryptographie quantique."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20
            )
            return response.choices[0].message.content.strip().strip('"')
        except Exception as e:
            print(f"Error generating topic label: {e}")
            # Fallback: utiliser les 3 premiers termes
            return " - ".join(terms[:3])
    
    def extract_entities(self):
        """Extrait les organisations, personnes et technologies mentionnées"""
        print("Extracting named entities...")
        
        entities = {
            'ORG': [],  # Organisations
            'PERSON': [],  # Personnes
            'PRODUCT': []  # Produits/Technologies
        }
        
        for text in self.data['full_text']:
            doc = self.nlp(text[:10000])  # Limiter la taille pour la performance
            
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)
        
        # Compter les occurrences
        entity_counts = {}
        for entity_type, entity_list in entities.items():
            if entity_list:
                counts = pd.Series(entity_list).value_counts().head(15)
                entity_counts[entity_type] = counts.to_dict()
        
        # Sauvegarder les résultats
        with open(os.path.join(self.results_folder, "entities.json"), 'w') as f:
            json.dump(entity_counts, f, indent=2)
            
        return entity_counts
    
    def create_visualizations(self):
        """Crée des visualisations à partir des données analysées"""
        print("Creating visualizations...")
        
        # 1. Évolution temporelle des publications
        plt.figure(figsize=(12, 6))
        self.data['date'].value_counts().sort_index().plot(kind='line')
        plt.title('Nombre de publications sur la cryptographie quantique au fil du temps')
        plt.xlabel('Date')
        plt.ylabel('Nombre de publications')
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, 'publications_over_time.png'))
        
        # 2. Répartition par source
        plt.figure(figsize=(12, 8))
        source_counts = self.data['source'].value_counts().head(15)
        sns.barplot(x=source_counts.values, y=source_counts.index)
        plt.title('Top 15 des sources d\'information sur la cryptographie quantique')
        plt.xlabel('Nombre de publications')
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, 'sources_distribution.png'))
        
        # 3. Nuage de mots des titres
        text = ' '.join(self.data['title'])
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            stopwords=set(stopwords.words('english')),
            max_words=100
        ).generate(text)
        
        plt.figure(figsize=(16, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, 'title_wordcloud.png'))
        
        # 4. Distribution par type de contenu
        plt.figure(figsize=(10, 6))
        self.data['type'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Répartition par type de contenu')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, 'content_type_distribution.png'))
        
        return os.path.join(self.results_folder)
    
    def generate_summary(self):
        """Génère une synthèse des dernières tendances en cryptographie quantique"""
        print("Generating summary of recent trends...")
        
        # Filtrer pour les données récentes (30 derniers jours)
        latest_date = self.data['date'].max()
        month_ago = latest_date - timedelta(days=30)
        recent_data = self.data[self.data['date'] >= month_ago]
        
        # Préparer les données pour le prompt
        recent_titles = recent_data['title'].head(20).tolist()
        titles_text = "\n".join([f"- {title}" for title in recent_titles])
        
        # Générer le résumé avec OpenAI
        prompt = f"""
        Voici les titres des 20 publications récentes sur la cryptographie quantique:
        
        {titles_text}
        
        En vous basant sur ces informations, générez une synthèse (environ 300 mots) des tendances actuelles en cryptographie quantique.
        La synthèse doit être structurée en plusieurs paragraphes courts couvrant :
        1. Les avancées technologiques principales
        2. Les applications émergentes
        3. Les défis et obstacles actuels
        4. Les perspectives futures
        
        Utilisez un style journalistique, adapté à un podcast tech.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en cryptographie quantique qui rédige une synthèse pour une veille technologique."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700
            )
            
            summary = response.choices[0].message.content
            
            # Sauvegarder le résumé
            summary_path = os.path.join(self.results_folder, "recent_trends_summary.txt")
            with open(summary_path, 'w') as f:
                f.write(summary)
                
            return summary
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Erreur lors de la génération de la synthèse."
    
    def run_full_analysis(self):
        """Exécute l'analyse complète et retourne un rapport de résultats"""
        print("Running full analysis pipeline...")
        
        results = {}
        
        # 1. Extraire les sujets principaux
        results['topics'] = self.extract_topics()
        
        # 2. Extraire les entités nommées
        results['entities'] = self.extract_entities()
        
        # 3. Créer des visualisations
        results['visualizations_path'] = self.create_visualizations()
        
        # 4. Générer une synthèse des tendances récentes
        results['summary'] = self.generate_summary()
        
        # 5. Préparer les données pour diffusion
        self.prepare_for_distribution()
        
        print(f"Analysis complete. Results saved to {self.results_folder}")
        return results
    
    def prepare_for_distribution(self):
        """Prépare les données pour la diffusion (Telegram, podcast)"""
        # Créer un résumé quotidien au format JSON
        latest_date = self.data['date'].max()
        today = datetime.now().strftime('%Y-%m-%d')
        
        daily_digest = {
            'date': today,
            'total_items': len(self.data),
            'recent_items': len(self.recent_data),
            'top_sources': self.data['source'].value_counts().head(5).to_dict(),
            'latest_research': self.data[self.data['type'] == 'research'].sort_values('date', ascending=False).head(5)[['title', 'source', 'url', 'date']].to_dict('records'),
            'latest_news': self.data[self.data['type'] == 'news'].sort_values('date', ascending=False).head(5)[['title', 'source', 'url', 'date']].to_dict('records')
        }
        
        # Sauvegarder le digest
        with open(os.path.join(self.results_folder, f"daily_digest_{today}.json"), 'w') as f:
            json.dump(daily_digest, f, indent=2)
            
        return daily_digest

if __name__ == "__main__":
    # Exemple d'utilisation
    data_path = "data/quantum_crypto_data_20250315_120000.json"  # À ajuster selon votre fichier
    analyzer = QuantumCryptoAnalyzer(data_path)
    results = analyzer.run_full_analysis()
    print("Analysis completed successfully!")