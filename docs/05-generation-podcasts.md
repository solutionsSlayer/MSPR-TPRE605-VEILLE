# Module de Génération de Podcasts

## Présentation générale

Le module de génération de podcasts (`src/podcast/`) transforme les analyses textuelles en contenu audio accessible. Il permet de diffuser les informations de veille dans un format alternatif qui peut être consommé lors des déplacements ou d'autres activités. Ce module représente une extension multimédia importante du système de veille.

## Classe principale : QuantumCryptoPodcast

La classe `QuantumCryptoPodcast` (définie dans `podcast_generator.py`) orchestre l'ensemble du processus de génération de podcasts, depuis la création du script jusqu'à la synthèse vocale et la production du fichier audio final.

### Initialisation

```python
def __init__(self, analysis_folder="analysis_results", output_folder="podcasts"):
    """Initialise le générateur de podcast"""
    # Vérifier les API keys nécessaires
    self.openai_api_key = os.getenv("OPENAI_API_KEY")
    self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not self.openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing from environment variables")
    
    # Initialiser le client OpenAI
    self.openai_client = OpenAI(api_key=self.openai_api_key)
    
    # Configurer les dossiers
    self.analysis_folder = analysis_folder
    self.output_folder = output_folder
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Format du podcast
    self.podcast_format = {
        "intro_duration": 30,  # secondes
        "body_duration": 300,  # 5 minutes
        "outro_duration": 20,  # secondes
        "voice_id": "EXAVITQu4vr4xnSDxMaL"  # ID de voix ElevenLabs
    }
    
    # Informations sur le podcast
    self.podcast_info = {
        "name": "QuantumCrypto Weekly",
        "description": "Le podcast hebdomadaire sur l'actualité de la cryptographie quantique"
    }
```

## Processus de génération de podcasts

Le processus de génération d'un podcast se déroule en plusieurs étapes :

### 1. Récupération des analyses récentes

La méthode `_get_latest_analysis()` collecte les dernières analyses disponibles :

```python
def _get_latest_analysis(self):
    """Récupère les dernières analyses disponibles"""
    # Chercher le résumé le plus récent
    summary_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('recent_trends_summary')]
    latest_summary_file = sorted(summary_files)[-1]
    with open(os.path.join(self.analysis_folder, latest_summary_file), 'r') as f:
        summary = f.read()
    
    # Chercher le digest quotidien le plus récent
    digest_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('daily_digest')]
    latest_digest_file = sorted(digest_files)[-1]
    with open(os.path.join(self.analysis_folder, latest_digest_file), 'r') as f:
        digest = json.load(f)
    
    return {
        "summary": summary,
        "digest": digest,
        "summary_date": latest_summary_file.split('_')[-1].split('.')[0]
    }
```

### 2. Génération du script du podcast

La méthode `generate_podcast_script()` utilise l'API OpenAI pour créer un script narratif basé sur les analyses :

```python
def generate_podcast_script(self):
    """Génère le script du podcast basé sur les dernières analyses"""
    # Récupérer les dernières analyses
    analysis = self._get_latest_analysis()
    
    # Extraire des informations clés pour le script
    latest_research = analysis['digest'].get('latest_research', [])
    latest_news = analysis['digest'].get('latest_news', [])
    
    # Formatage pour le prompt GPT
    research_items = "\n".join([
        f"- {item['title']} ({item['source']})" 
        for item in latest_research[:5]
    ])
    
    news_items = "\n".join([
        f"- {item['title']} ({item['source']})" 
        for item in latest_news[:5]
    ])
    
    # Créer le prompt pour la génération du script
    prompt = f"""
    Tu es le rédacteur principal d'un podcast tech spécialisé en cryptographie quantique appelé "QuantumCrypto Weekly".
    
    Crée un script de podcast de 5 minutes qui couvrira l'actualité récente de la cryptographie quantique.
    
    Le podcast doit avoir la structure suivante:
    1. Une introduction de 30 secondes qui présente le podcast et les sujets du jour
    2. Corps principal (environ 4 minutes) qui couvre:
       - Résumé des tendances majeures de la semaine
       - Présentation de 2-3 recherches importantes
       - Présentation de 2-3 actualités importantes
    3. Une conclusion de 30 secondes

    Voici le résumé des tendances récentes:
    {analysis['summary']}
    
    Voici les dernières recherches scientifiques:
    {research_items}
    
    Voici les dernières actualités:
    {news_items}
    
    Important:
    - Utilise un ton conversationnel, comme si tu parlais à un auditeur
    - Inclus occasionnellement des questions rhétoriques pour engager l'auditeur
    - Utilise des transitions claires entre les sujets
    - Évite les longs paragraphes, préfère des phrases plus courtes adaptées à l'audio
    - Inclus des balises [PAUSE] pour indiquer de courtes pauses naturelles
    """
    
    # Générer le script avec GPT-4
    response = self.openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un expert en vulgarisation scientifique spécialisé dans les technologies quantiques."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )
    
    script = response.choices[0].message.content
    
    # Sauvegarder le script
    today = datetime.datetime.now().strftime("%Y%m%d")
    script_path = os.path.join(self.output_folder, f"podcast_script_{today}.txt")
    with open(script_path, 'w') as f:
        f.write(script)
    
    return script_path
```

### 3. Génération audio à partir du script

La méthode `generate_audio_from_script()` transforme le script textuel en fichier audio :

```python
def generate_audio_from_script(self, script_path):
    """Génère l'audio du podcast à partir du script"""
    # Lire le script
    with open(script_path, 'r') as f:
        script = f.read()
    
    # Diviser le script en sections pour une meilleure gestion
    sections = []
    
    if "INTRO" in script and "CORPS" in script and "CONCLUSION" in script:
        parts = script.split("INTRO")
        intro = "INTRO" + parts[1].split("CORPS")[0]
        body = "CORPS" + parts[1].split("CORPS")[1].split("CONCLUSION")[0]
        outro = "CONCLUSION" + parts[1].split("CONCLUSION")[1]
        sections = [intro, body, outro]
    else:
        # Diviser en morceaux de 4000 caractères max (limite pour TTS)
        chunk_size = 4000
        for i in range(0, len(script), chunk_size):
            sections.append(script[i:i+chunk_size])
    
    # Utiliser ElevenLabs pour la génération vocale
    audio_segments = []
    
    if self.elevenlabs_api_key:
        for i, section in enumerate(sections):
            audio_file = self._generate_audio_elevenlabs(section, i)
            audio_segments.append(audio_file)
    else:
        # Fallback sur OpenAI TTS
        for i, section in enumerate(sections):
            audio_file = self._generate_audio_openai(section, i)
            audio_segments.append(audio_file)
    
    # Combiner les segments audio
    final_audio = self._combine_audio_segments(audio_segments)
    
    # Sauvegarder l'audio final
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(self.output_folder, f"QuantumCrypto_Weekly_{today}.mp3")
    final_audio.export(output_path, format="mp3", bitrate="192k")
    
    return output_path
```

### 4. Génération vocale avec ElevenLabs

La méthode `_generate_audio_elevenlabs()` utilise l'API ElevenLabs pour la synthèse vocale :

```python
def _generate_audio_elevenlabs(self, text, section_index):
    """Génère l'audio avec ElevenLabs TTS"""
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + self.podcast_format["voice_id"]
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": self.elevenlabs_api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        output_file = os.path.join(self.output_folder, f"temp_section_{section_index}.mp3")
        with open(output_file, "wb") as f:
            f.write(response.content)
        return output_file
    else:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
```

### 5. Génération vocale avec OpenAI (solution de secours)

La méthode `_generate_audio_openai()` utilise l'API TTS d'OpenAI comme solution de repli :

```python
def _generate_audio_openai(self, text, section_index):
    """Génère l'audio avec OpenAI TTS (fallback)"""
    response = self.openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
        input=text
    )
    
    output_file = os.path.join(self.output_folder, f"temp_section_{section_index}.mp3")
    response.stream_to_file(output_file)
    
    return output_file
```

### 6. Combinaison des segments audio

La méthode `_combine_audio_segments()` assemble les segments audio en un fichier unique :

```python
def _combine_audio_segments(self, audio_files):
    """Combine les segments audio en un seul fichier"""
    combined = AudioSegment.empty()
    
    for file in audio_files:
        segment = AudioSegment.from_file(file)
        combined += segment
    
    # Ajouter ici une éventuelle musique de fond, effets sonores, etc.
    
    return combined
```

### 7. Processus complet de génération

La méthode `generate_podcast()` orchestre le processus complet :

```python
def generate_podcast(self):
    """Exécute le processus complet de génération de podcast"""
    try:
        # 1. Générer le script
        script_path = self.generate_podcast_script()
        
        # 2. Générer l'audio
        podcast_path = self.generate_audio_from_script(script_path)
        
        # 3. Uploader le podcast
        podcast_url = self.upload_podcast(podcast_path)
        
        # 4. Notifier les abonnés
        self.notify_subscribers(podcast_url)
        
        return {
            "status": "success",
            "script_path": script_path,
            "podcast_path": podcast_path,
            "podcast_url": podcast_url
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

## Organisation des podcasts

Les podcasts sont organisés selon leur périodicité :

- `podcasts/weekly/` : Podcasts hebdomadaires
  - Scripts : `podcast_script_YYYYMMDD.txt`
  - Fichiers audio : `QuantumCrypto_Weekly_YYYYMMDD.mp3`

- `podcasts/monthly/` : Podcasts mensuels
  - Scripts : `podcast_script_YYYYMMDD.txt`
  - Fichiers audio : `QuantumCrypto_Monthly_YYYYMMDD.mp3`

## Personnalisation des voix

Le système permet de personnaliser la voix utilisée pour les podcasts :

- Via ElevenLabs (option préférée) : Voices professionnelles avec paramètres de stabilité et de similarité ajustables
- Via OpenAI TTS (solution de repli) : Plusieurs voix disponibles (alloy, echo, fable, onyx, nova, shimmer)

Les identifiants de voix sont configurables dans `self.podcast_format["voice_id"]`.

## Intégration avec le système principal

Le système de génération de podcasts est intégré dans le pipeline principal du système de veille :

```python
# Dans QuantumCryptoVeille (main.py)
def generate_podcast(self):
    """Génère le podcast à partir des analyses"""
    # Vérifier que les fichiers nécessaires sont disponibles
    summary_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('recent_trends_summary')]
    digest_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('daily_digest')]
    
    if not summary_files or not digest_files:
        logger.error("Fichiers d'analyse nécessaires non disponibles pour la génération du podcast")
        return None
    
    try:
        podcast_generator = QuantumCryptoPodcast(
            analysis_folder=self.analysis_folder,
            output_folder=self.podcast_folder
        )
        result = podcast_generator.generate_podcast()
        
        if result["status"] == "success":
            # Enregistrer le podcast dans l'index
            self.file_manager.register_podcast(
                "weekly", 
                result["script_path"], 
                result["podcast_path"]
            )
            return result["podcast_path"]
        else:
            error_details = result.get('error', 'Raison inconnue')
            logger.error(f"Erreur lors de la génération du podcast: {error_details}")
            return None
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du podcast: {e}")
        return None
```

## Planification de la génération

La génération de podcasts est planifiée de façon hebdomadaire, généralement le lundi :

```python
# Dans la méthode run_full_pipeline() de QuantumCryptoVeille
# 3. Génération du podcast (une fois par semaine)
today = datetime.now()
is_podcast_day = today.weekday() == 0  # Lundi

if is_podcast_day:
    logger.info("Jour de génération de podcast (lundi)")
    podcast_path = self.generate_podcast()
    if podcast_path:
        logger.info(f"Podcast hebdomadaire généré: {podcast_path}")
```

## Dépendances techniques

Le module de génération de podcasts utilise plusieurs bibliothèques :
- `openai` pour la génération de scripts et la synthèse vocale de secours
- `requests` pour l'API ElevenLabs
- `pydub` pour la manipulation audio
- `datetime` pour la gestion des dates et horodatages
