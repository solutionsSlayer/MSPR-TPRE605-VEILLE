import os
import json
import requests
import datetime
import logging
from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuantumCryptoPodcast:
    def __init__(self, analysis_folder="analysis_results", output_folder="podcasts"):
        """
        Initialise le générateur de podcast
        
        Args:
            analysis_folder: Dossier contenant les résultats d'analyse
            output_folder: Dossier où seront stockés les podcasts générés
        """
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
            "voice_id": "EXAVITQu4vr4xnSDxMaL"  # ID de voix ElevenLabs (à ajuster)
        }
        
        # Informations sur le podcast
        self.podcast_info = {
            "name": "QuantumCrypto Weekly",
            "description": "Le podcast hebdomadaire sur l'actualité de la cryptographie quantique"
        }
    
    def _get_latest_analysis(self):
        """Récupère les dernières analyses disponibles"""
        # Chercher le résumé le plus récent
        summary_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('recent_trends_summary')]
        
        if not summary_files:
            raise FileNotFoundError("No summary file found in analysis folder")
        
        latest_summary_file = sorted(summary_files)[-1]
        
        with open(os.path.join(self.analysis_folder, latest_summary_file), 'r') as f:
            summary = f.read()
        
        # Chercher le digest quotidien le plus récent
        digest_files = [f for f in os.listdir(self.analysis_folder) if f.startswith('daily_digest')]
        
        if not digest_files:
            raise FileNotFoundError("No digest file found in analysis folder")
        
        latest_digest_file = sorted(digest_files)[-1]
        
        with open(os.path.join(self.analysis_folder, latest_digest_file), 'r') as f:
            digest = json.load(f)
        
        return {
            "summary": summary,
            "digest": digest,
            "summary_date": latest_summary_file.split('_')[-1].split('.')[0]
        }
    
    def generate_podcast_script(self):
        """Génère le script du podcast basé sur les dernières analyses"""
        logger.info("Generating podcast script")
        
        try:
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
            
            Format de sortie:
            Fournis le script complet avec les sections clairement délimitées (INTRO, CORPS, CONCLUSION).
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
            
            logger.info(f"Script generated and saved to {script_path}")
            return script_path
            
        except Exception as e:
            logger.error(f"Error generating podcast script: {e}")
            raise
    
    def generate_audio_from_script(self, script_path):
        """Génère l'audio du podcast à partir du script"""
        logger.info(f"Generating audio from script: {script_path}")
        
        try:
            # Lire le script
            with open(script_path, 'r') as f:
                script = f.read()
            
            # Ajouter une musique de fond serait fait ici (avec pydub)
            
            # Diviser le script en sections pour une meilleure gestion
            sections = []
            
            # Extraction naïve des sections - à améliorer selon format réel
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
            logger.info(f"Podcast generated and saved to {output_path}")
            
            # Nettoyer les fichiers temporaires
            for file in audio_segments:
                if os.path.exists(file):
                    os.remove(file)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise
    
    def _generate_audio_elevenlabs(self, text, section_index):
        """Génère l'audio avec ElevenLabs TTS"""
        logger.info(f"Generating audio for section {section_index} with ElevenLabs")
        
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
    
    def _generate_audio_openai(self, text, section_index):
        """Génère l'audio avec OpenAI TTS (fallback)"""
        logger.info(f"Generating audio for section {section_index} with OpenAI TTS")
        
        response = self.openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )
        
        output_file = os.path.join(self.output_folder, f"temp_section_{section_index}.mp3")
        response.stream_to_file(output_file)
        
        return output_file
    
    def _combine_audio_segments(self, audio_files):
        """Combine les segments audio en un seul fichier"""
        logger.info(f"Combining {len(audio_files)} audio segments")
        
        combined = AudioSegment.empty()
        
        for file in audio_files:
            segment = AudioSegment.from_file(file)
            combined += segment
        
        # Ajouter ici une éventuelle musique de fond, effets sonores, etc.
        
        return combined
    
    def upload_podcast(self, podcast_path):
        """Upload le podcast sur une plateforme d'hébergement (à implémenter)"""
        logger.info(f"Uploading podcast: {podcast_path}")
        
        # Cette partie dépendrait de la plateforme d'hébergement choisie
        # Exemple avec un service fictif:
        
        # upload_url = "https://example.com/api/upload"
        # with open(podcast_path, "rb") as f:
        #     files = {"file": f}
        #     response = requests.post(upload_url, files=files)
        # 
        # return response.json()["podcast_url"]
        
        # Pour l'instant, on simule simplement un lien
        today = datetime.datetime.now().strftime("%Y%m%d")
        return f"https://example.com/quantum-crypto-podcast-{today}"
    
    def notify_subscribers(self, podcast_url):
        """Notifie les abonnés (via Telegram, email, etc.) de la disponibilité du nouveau podcast"""
        logger.info(f"Notifying subscribers about new podcast: {podcast_url}")
        
        # Cette fonction serait implémentée pour envoyer des notifications
        # Elle pourrait utiliser le bot Telegram déjà créé
        
        # Pour l'instant, on simule simplement une notification
        logger.info("Notification sent to subscribers")
    
    def generate_podcast(self):
        """Exécute le processus complet de génération de podcast"""
        logger.info("Starting podcast generation process")
        
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
            logger.error(f"Error in podcast generation process: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

if __name__ == "__main__":
    try:
        podcast_generator = QuantumCryptoPodcast()
        result = podcast_generator.generate_podcast()
        
        if result["status"] == "success":
            print(f"Podcast successfully generated and available at: {result['podcast_url']}")
            print(f"Local file: {result['podcast_path']}")
        else:
            print(f"Error generating podcast: {result['error']}")
    
    except Exception as e:
        print(f"Fatal error: {e}")