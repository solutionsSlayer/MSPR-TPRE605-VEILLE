import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
import traceback
from nltk.corpus import stopwords
import spacy
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Fonction pour télécharger les ressources NLTK si nécessaire
def download_nltk_resources():
    try:
        nltk.data.find('corpora/stopwords')
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Téléchargement des ressources NLTK nécessaires...")
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)

# Télécharger les ressources NLTK au démarrage
download_nltk_resources()

class QuantumCryptoAnalyzer:
    def __init__(self, data_path):
        """
        Initialise l'analyseur avec le chemin du fichier de données
        """
        self.data_path = data_path
        self.results_folder = "analysis_results"
        
        # Créer les sous-dossiers pour une meilleure organisation
        self.clusters_folder = os.path.join(self.results_folder, "clusters")
        self.visualizations_folder = os.path.join(self.results_folder, "visualizations")
        self.entities_folder = os.path.join(self.results_folder, "entities")
        self.reports_folder = os.path.join(self.results_folder, "reports")
        self.daily_folder = os.path.join(self.results_folder, "daily")
        self.weekly_folder = os.path.join(self.results_folder, "weekly")
        self.monthly_folder = os.path.join(self.results_folder, "monthly")
        
        # Créer les répertoires s'ils n'existent pas
        for folder in [self.results_folder, self.clusters_folder, self.visualizations_folder, 
                      self.entities_folder, self.reports_folder, self.daily_folder, 
                      self.weekly_folder, self.monthly_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # Définir un modèle OpenAI moins cher par défaut si aucun n'est spécifié
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Charger les données
        try:
            if data_path.endswith('.csv'):
                self.data = pd.read_csv(data_path, encoding='utf-8')
            elif data_path.endswith('.json'):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.data = pd.DataFrame(json.load(f))
            else:
                raise ValueError("Format de fichier non supporté. Utilisez CSV ou JSON.")
            
            print(f"Données chargées avec succès: {len(self.data)} entrées depuis {data_path}")
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            # Créer un DataFrame minimal en cas d'erreur
            self.data = pd.DataFrame({
                'title': ['Erreur de chargement'],
                'summary': ['Données de test pour récupération'],
                'date': [datetime.now().strftime('%Y-%m-%d')],
                'source': ['Test'],
                'type': ['news']
            })
            print("Un jeu de données minimal a été créé pour récupération.")
        
        # Prétraiter les données
        self.preprocess_data()
        
        # Charger le modèle spaCy pour l'extraction d'entités
        try:
            self.nlp = spacy.load("fr_core_news_sm")
            print("Modèle spaCy chargé avec succès")
        except:
            print("Erreur lors du chargement du modèle spaCy. Tentative d'installation...")
            os.system("python -m spacy download fr_core_news_sm")
            try:
                self.nlp = spacy.load("fr_core_news_sm")
                print("Modèle spaCy installé et chargé avec succès")
            except Exception as e:
                print(f"Impossible de charger le modèle spaCy: {e}")
                self.nlp = None
        
        # Initialiser le client OpenAI
        self.client = None
        self.initialize_openai_client()

    def initialize_openai_client(self):
        """
        Initialise le client OpenAI avec la clé API
        """
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                print("Client OpenAI initialisé avec succès")
            else:
                print("Clé API OpenAI non trouvée dans les variables d'environnement")
        except Exception as e:
            print(f"Erreur lors de l'initialisation du client OpenAI: {e}")
            self.client = None

    def preprocess_data(self):
        """
        Prétraite les données pour l'analyse
        """
        try:
            # Vérifier les colonnes requises
            required_columns = ['title', 'summary', 'date', 'source']
            for col in required_columns:
                if col not in self.data.columns:
                    self.data[col] = ['Non disponible'] * len(self.data)
                    print(f"Colonne '{col}' manquante, ajoutée avec valeurs par défaut")
            
            # Convertir les dates en format datetime
            if 'date' in self.data.columns:
                try:
                    self.data['date'] = pd.to_datetime(self.data['date'], errors='coerce')
                    # Remplacer les dates NaT par la date actuelle
                    self.data['date'].fillna(pd.Timestamp.now(), inplace=True)
                except Exception as e:
                    print(f"Erreur lors de la conversion des dates: {e}")
                    self.data['date'] = pd.Timestamp.now()
            
            # Créer une colonne de texte combiné pour l'analyse
            self.data['combined_text'] = self.data['title'].fillna('') + ' ' + self.data['summary'].fillna('')
            
            # Nettoyer le texte
            self.data['clean_text'] = self.data['combined_text'].apply(self.clean_text)
            
            print("Prétraitement des données terminé avec succès")
        except Exception as e:
            print(f"Erreur lors du prétraitement des données: {e}")
            traceback.print_exc()

    def clean_text(self, text):
        """
        Nettoie le texte pour l'analyse
        """
        if not isinstance(text, str):
            return ""
        
        # Convertir en minuscules
        text = text.lower()
        
        # Tokenisation et suppression des stopwords
        stop_words = set(stopwords.words('french'))
        tokens = nltk.word_tokenize(text, language='french')
        tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
        
        return ' '.join(tokens)

    def perform_clustering(self, n_clusters=5):
        """
        Effectue un clustering des articles basé sur leur contenu
        """
        try:
            # Vérifier qu'il y a suffisamment de données
            if len(self.data) < n_clusters:
                print(f"Pas assez de données pour {n_clusters} clusters. Ajustement à {len(self.data)}.")
                n_clusters = max(2, len(self.data) - 1)
            
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
                # Obtenir les indices des documents dans ce cluster
                indices = self.data[self.data['cluster'] == i].index
                
                if len(indices) > 0:
                    # Calculer la moyenne des vecteurs TF-IDF pour ce cluster
                    cluster_center = X[indices].mean(axis=0)
                    
                    # Obtenir les indices des termes les plus importants
                    terms_indices = cluster_center.argsort()[0, -10:]
                    
                    # Extraire les termes correspondants
                    top_terms = [feature_names[idx] for idx in terms_indices]
                    cluster_terms[i] = top_terms
            
            self.cluster_terms = cluster_terms
            
            # Sauvegarder les résultats
            cluster_results = {}
            for i in range(n_clusters):
                cluster_data = self.data[self.data['cluster'] == i]
                cluster_results[f"Cluster {i}"] = {
                    "size": len(cluster_data),
                    "top_terms": cluster_terms.get(i, []),
                    "articles": cluster_data[['title', 'source', 'date']].to_dict('records')
                }
            
            # Sauvegarder les résultats
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.clusters_folder, f"clusters_{timestamp}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cluster_results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"Clustering terminé avec succès. Résultats sauvegardés dans {output_path}")
            return cluster_results
        
        except Exception as e:
            print(f"Erreur lors du clustering: {e}")
            traceback.print_exc()
            return None

    def generate_wordcloud(self):
        """
        Génère un nuage de mots à partir des textes
        """
        try:
            # Combiner tous les textes nettoyés
            all_text = ' '.join(self.data['clean_text'])
            
            # Générer le nuage de mots
            wordcloud = WordCloud(width=800, height=400, background_color='white', 
                                 max_words=100, contour_width=3, contour_color='steelblue',
                                 collocations=False).generate(all_text)
            
            # Sauvegarder l'image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.visualizations_folder, f"wordcloud_{timestamp}.png")
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300)
            plt.close()
            
            print(f"Nuage de mots généré avec succès. Image sauvegardée dans {output_path}")
            return output_path
        
        except Exception as e:
            print(f"Erreur lors de la génération du nuage de mots: {e}")
            traceback.print_exc()
            return None

    def extract_entities(self):
        """
        Extrait les entités nommées des textes
        """
        if self.nlp is None:
            print("Modèle spaCy non disponible. Impossible d'extraire les entités.")
            return None
        
        try:
            # Initialiser les dictionnaires pour stocker les entités
            entities = {
                'ORG': [],  # Organisations
                'LOC': [],  # Lieux
                'PER': [],  # Personnes
                'MISC': []  # Divers
            }
            
            # Traiter chaque texte
            for text in self.data['combined_text']:
                if not isinstance(text, str) or not text.strip():
                    continue
                
                # Limiter la taille du texte pour éviter les problèmes de mémoire
                doc = self.nlp(text[:10000])
                
                # Extraire les entités
                for ent in doc.ents:
                    if ent.label_ in ['ORG', 'LOC', 'PER']:
                        entities[ent.label_].append(ent.text)
                    else:
                        entities['MISC'].append(ent.text)
            
            # Compter les occurrences
            entity_counts = {}
            for category, items in entities.items():
                counter = {}
                for item in items:
                    counter[item] = counter.get(item, 0) + 1
                
                # Trier par fréquence
                sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
                entity_counts[category] = sorted_items[:20]  # Top 20
            
            # Sauvegarder les résultats
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.entities_folder, f"entities_{timestamp}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(entity_counts, f, ensure_ascii=False, indent=2)
            
            print(f"Extraction d'entités terminée. Résultats sauvegardés dans {output_path}")
            return entity_counts
        
        except Exception as e:
            print(f"Erreur lors de l'extraction d'entités: {e}")
            traceback.print_exc()
            return None

    def analyze_trends(self):
        """
        Analyse les tendances temporelles dans les données
        """
        try:
            # Vérifier que la colonne date est au format datetime
            if not pd.api.types.is_datetime64_any_dtype(self.data['date']):
                self.data['date'] = pd.to_datetime(self.data['date'], errors='coerce')
            
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
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Sauvegarder le graphique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.visualizations_folder, f"trends_{timestamp}.png")
            plt.savefig(output_path, dpi=300)
            plt.close()
            
            # Sauvegarder les données
            trend_data = {
                'monthly_counts': {str(k): int(v) for k, v in monthly_counts.items()}
            }
            
            json_path = os.path.join(self.visualizations_folder, f"trends_data_{timestamp}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(trend_data, f, ensure_ascii=False, indent=2)
            
            print(f"Analyse des tendances terminée. Graphique sauvegardé dans {output_path}")
            return output_path
        
        except Exception as e:
            print(f"Erreur lors de l'analyse des tendances: {e}")
            traceback.print_exc()
            return None

    def generate_ai_insights(self, prompt_template=None):
        """
        Génère des insights sur les données en utilisant l'API OpenAI
        """
        if self.client is None:
            print("Client OpenAI non initialisé. Impossible de générer des insights.")
            return None
        
        try:
            # Préparer un échantillon des données pour l'analyse
            sample_size = min(20, len(self.data))
            sample_data = self.data.sample(sample_size)
            
            # Création d'un résumé des données avec gestion des erreurs
            data_lines = []
            for _, row in sample_data.iterrows():
                try:
                    title = str(row['title']) if not pd.isna(row['title']) else "Sans titre"
                    summary = str(row['summary']) if not pd.isna(row['summary']) else "Sans résumé"
                    date = str(row['date']) if not pd.isna(row['date']) else "Date inconnue"
                    source = str(row['source']) if not pd.isna(row['source']) else "Source inconnue"
                    
                    data_lines.append(f"Titre: {title}")
                    data_lines.append(f"Résumé: {summary}")
                    data_lines.append(f"Date: {date}")
                    data_lines.append(f"Source: {source}")
                    data_lines.append("---")
                except Exception as row_error:
                    print(f"Erreur lors du traitement d'une ligne: {row_error}")
                    continue
            
            data_summary = "\n".join(data_lines)
            
            # Définir le prompt par défaut si non spécifié
            if prompt_template is None:
                prompt_template = """
                Analyse les données suivantes sur la cryptographie quantique et fournit:
                1. Les principales tendances et thèmes
                2. Les acteurs clés mentionnés (entreprises, chercheurs, institutions)
                3. Les technologies émergentes identifiées
                4. Les défis et opportunités dans le domaine
                5. Des recommandations pour la veille technologique future
                
                Données:
                {data_summary}
                
                Format ta réponse de manière structurée avec des sections claires.
                """
            
            # Remplacer le placeholder par les données
            prompt = prompt_template.format(data_summary=data_summary)
            
            # Appeler l'API OpenAI
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "Tu es un expert en cryptographie quantique qui analyse des données de veille technologique."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            # Extraire la réponse
            insights = response.choices[0].message.content
            
            # Sauvegarder les insights
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.reports_folder, f"ai_insights_{timestamp}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)
            
            print(f"Insights générés avec succès. Résultats sauvegardés dans {output_path}")
            return insights
        
        except Exception as e:
            print(f"Erreur lors de la génération des insights: {e}")
            traceback.print_exc()
            return None

    def run_complete_analysis(self):
        """
        Exécute une analyse complète des données
        """
        print("\n=== Démarrage de l'analyse complète ===\n")
        
        # Étape 1: Clustering
        print("\n--- Clustering des articles ---")
        clusters = self.perform_clustering()
        
        # Étape 2: Nuage de mots
        print("\n--- Génération du nuage de mots ---")
        wordcloud_path = self.generate_wordcloud()
        
        # Étape 3: Extraction d'entités
        print("\n--- Extraction des entités nommées ---")
        entities = self.extract_entities()
        
        # Étape 4: Analyse des tendances
        print("\n--- Analyse des tendances temporelles ---")
        trends_path = self.analyze_trends()
        
        # Étape 5: Insights IA
        print("\n--- Génération d'insights par IA ---")
        insights = self.generate_ai_insights()
        
        # Générer un rapport de synthèse
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.reports_folder, f"rapport_complet_{timestamp}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT D'ANALYSE COMPLET ===\n\n")
            f.write(f"Date d'analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Fichier analysé: {self.data_path}\n")
            f.write(f"Nombre d'articles: {len(self.data)}\n\n")
            
            f.write("--- RÉSUMÉ DES RÉSULTATS ---\n\n")
            
            if clusters:
                f.write("CLUSTERS IDENTIFIÉS:\n")
                for cluster, info in clusters.items():
                    f.write(f"{cluster}: {info['size']} articles\n")
                    f.write(f"Termes principaux: {', '.join(info['top_terms'])}\n\n")
            
            if entities:
                f.write("ENTITÉS PRINCIPALES:\n")
                for category, items in entities.items():
                    f.write(f"{category}:\n")
                    for item, count in items[:5]:  # Top 5
                        f.write(f"- {item}: {count} mentions\n")
                    f.write("\n")
            
            if insights:
                f.write("INSIGHTS IA:\n")
                f.write(insights)
        
        print(f"\n=== Analyse complète terminée ===")
        print(f"Rapport de synthèse sauvegardé dans {report_path}")
        
        return {
            "report_path": report_path,
            "clusters": clusters,
            "wordcloud": wordcloud_path,
            "entities": entities,
            "trends": trends_path,
            "insights": insights,
            "topics": [{'label': f'Cluster {i}', 'terms': terms} for i, terms in cluster_terms.items()] if hasattr(self, 'cluster_terms') else [],
            "summary": insights
        }

    def run_full_analysis(self):
        """
        Méthode d'adaptation qui appelle run_complete_analysis pour maintenir la compatibilité
        avec le code existant dans main.py
        """
        print("Info: Redirection de run_full_analysis() vers run_complete_analysis()")
        return self.run_complete_analysis()

# Exemple d'utilisation
if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    else:
        data_path = input("Entrez le chemin du fichier de données (CSV ou JSON): ")
    
    analyzer = QuantumCryptoAnalyzer(data_path)
    results = analyzer.run_complete_analysis()