# Module de Gestion des Fichiers

## Présentation générale

Le module de gestion des fichiers (`src/utils/file_manager/`) fournit une couche d'abstraction pour l'organisation, le stockage et la récupération des données et des analyses dans le système de veille. Ce module central assure une gestion structurée et cohérente des fichiers à travers tout le système.

## Classe principale : FileManager

La classe `FileManager` encapsule toutes les opérations liées à la gestion des fichiers. Elle maintient un index central (`data/index.json`) qui référence tous les fichiers du système et leurs métadonnées.

### Initialisation

```python
def __init__(self, base_path="."):
    """Initialise le gestionnaire de fichiers"""
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
```

## Structure du système de fichiers

Le module organise les fichiers selon une hiérarchie précise :

```
data/
├── current/             # Données collectées récentes en cours d'utilisation
├── archives/            # Données collectées plus anciennes
└── index.json           # Fichier d'index centralisé

analysis_results/
├── daily/               # Analyses quotidiennes
├── weekly/              # Analyses hebdomadaires
├── monthly/             # Analyses mensuelles
└── visualizations/      # Visualisations et données permanentes

podcasts/
├── weekly/              # Podcasts hebdomadaires
└── monthly/             # Podcasts mensuels
```

## Structure du fichier d'index

Le fichier `index.json` maintient une trace de tous les fichiers et de leurs relations :

```json
{
  "last_updated": "2025-03-19T12:00:00",
  "data_files": [
    {
      "id": "20250316_134440",
      "date": "2025-03-16",
      "time": "13:44:40",
      "file_paths": {
        "csv": "data/current/quantum_crypto_data_20250316_134440.csv",
        "json": "data/current/quantum_crypto_data_20250316_134440.json"
      },
      "stats": {
        "total_items": 42,
        "scientific_articles": 15,
        "news_articles": 27,
        "unique_sources": 8
      },
      "status": "archived",
      "analysis_results": [
        {
          "type": "daily_digest",
          "date": "2025-03-16",
          "file_path": "analysis_results/daily/daily_digest_2025-03-16.json"
        }
      ]
    }
  ],
  "analysis_metrics": {
    "last_daily_digest": "2025-03-16",
    "last_weekly_summary": "2025-03-15",
    "last_monthly_report": "2025-02-28"
  },
  "podcasts": [
    {
      "type": "weekly",
      "date": "2025-03-15",
      "script_path": "podcasts/weekly/podcast_script_20250315.txt",
      "audio_path": "podcasts/weekly/QuantumCrypto_Weekly_20250315.mp3"
    }
  ]
}
```

## Opérations principales

### Sauvegarde des données collectées

La méthode `save_collected_data()` enregistre les données collectées et met à jour l'index :

```python
def save_collected_data(self, data, timestamp=None):
    """Sauvegarde les données collectées et met à jour l'index"""
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
    
    # Mettre à jour l'index
    # ...
    
    return csv_path, json_path
```

### Enregistrement des résultats d'analyse

La méthode `register_analysis_result()` enregistre un résultat d'analyse dans l'index :

```python
def register_analysis_result(self, data_id, analysis_type, file_path, date=None):
    """Enregistre un résultat d'analyse dans l'index"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Trouver l'entrée correspondante dans l'index
    for file_entry in self.index["data_files"]:
        if file_entry["id"] == data_id:
            # Ajouter ou mettre à jour le résultat d'analyse
            for analysis in file_entry["analysis_results"]:
                if analysis["type"] == analysis_type and analysis["date"] == date:
                    analysis["file_path"] = file_path
                    break
            else:
                file_entry["analysis_results"].append({
                    "type": analysis_type,
                    "date": date,
                    "file_path": file_path
                })
            
            # Mettre à jour les métriques d'analyse
            if analysis_type == "daily_digest":
                self.index["analysis_metrics"]["last_daily_digest"] = date
            # ...
    
    # Sauvegarder l'index
    self._save_index()
```

### Récupération des fichiers récents

La méthode `get_latest_data_file()` récupère le chemin vers le fichier de données le plus récent :

```python
def get_latest_data_file(self, file_type="json"):
    """Récupère le chemin vers le fichier de données le plus récent"""
    if not self.index["data_files"]:
        return None
    
    # Trouver le fichier le plus récent marqué comme "current"
    for file_entry in reversed(self.index["data_files"]):
        if file_entry["status"] == "current":
            return os.path.join(self.base_path, file_entry["file_paths"][file_type])
    
    # Si aucun fichier "current" n'est trouvé, retourner le plus récent
    latest_entry = self.index["data_files"][-1]
    return os.path.join(self.base_path, latest_entry["file_paths"][file_type])
```

### Archivage automatique

La méthode `archive_old_data()` archive les anciennes données pour libérer de l'espace :

```python
def archive_old_data(self, days_threshold=30):
    """Archive les anciennes données"""
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
    
    # Sauvegarder l'index
    if archived_count > 0:
        self._save_index()
    
    return archived_count
```

### Recherche par mot-clé

La méthode `search_by_keyword()` permet de rechercher des fichiers par mot-clé :

```python
def search_by_keyword(self, keyword):
    """Recherche des fichiers par mot-clé dans les titres et résumés"""
    results = []
    keyword = keyword.lower()
    
    for file_entry in self.index["data_files"]:
        # Charger le fichier JSON
        json_path = os.path.join(self.base_path, file_entry["file_paths"]["json"])
        if os.path.exists(json_path):
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
    
    return results
```

### Reconstruction de l'index

La méthode `rebuild_index()` permet de reconstruire l'index à partir des fichiers existants en cas de corruption :

```python
def rebuild_index(self):
    """Reconstruit l'index à partir des fichiers existants"""
    # Créer un nouvel index
    self.index = self._create_new_index()
    
    # Parcourir les fichiers dans le dossier courant
    for filename in os.listdir(self.current_data_folder):
        if filename.startswith("quantum_crypto_data_") and (filename.endswith(".json") or filename.endswith(".csv")):
            # Extraire l'ID à partir du nom de fichier
            file_id = filename.replace("quantum_crypto_data_", "").split(".")[0]
            # ...
    
    # Parcourir les fichiers dans le dossier d'archives
    # ...
    
    # Parcourir les résultats d'analyse
    # ...
    
    # Parcourir les podcasts
    # ...
    
    # Sauvegarder l'index
    self._save_index()
```

## Outil en ligne de commande

Un outil en ligne de commande (`tools/file_manager_tool.py`) est fourni pour faciliter la gestion manuelle des fichiers :

```
python tools/file_manager_tool.py info         # Afficher des informations sur les fichiers
python tools/file_manager_tool.py archive      # Archiver les anciennes données
python tools/file_manager_tool.py rebuild      # Reconstruire l'index
python tools/file_manager_tool.py search KEYWORD  # Rechercher des fichiers par mot-clé
python tools/file_manager_tool.py organize     # Organiser les fichiers selon la nouvelle structure
python tools/file_manager_tool.py cleanup      # Nettoyer les fichiers temporaires et duplicats
```

## Avantages du système

Le module de gestion des fichiers offre plusieurs avantages :

1. **Organisation structurée** : Les fichiers sont classés logiquement par type et par date
2. **Traçabilité** : L'index central maintient les relations entre les données et leurs analyses
3. **Facilité d'accès** : Les méthodes d'accès simplifient la recherche et la récupération des fichiers
4. **Gestion de l'espace** : L'archivage automatique aide à maintenir un système efficient
5. **Résilience** : La capacité de reconstruire l'index assure la robustesse du système
6. **Évolutivité** : La structure peut être étendue pour accueillir de nouveaux types de données

Ce système représente un compromis équilibré entre la simplicité d'un stockage par fichiers et les fonctionnalités avancées d'une base de données, tout en maintenant la possibilité d'une migration future vers une base de données relationnelle si nécessaire.
