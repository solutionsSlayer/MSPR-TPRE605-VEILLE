# Vue d'ensemble du système

## Introduction

Le système de veille technologique sur la cryptographie quantique est conçu pour collecter, analyser et diffuser des informations pertinentes dans le domaine de la cryptographie quantique. Il s'agit d'un système automatisé qui fonctionne de manière périodique pour maintenir une connaissance à jour des dernières avancées dans ce domaine en pleine évolution.

## Architecture globale

Le système est organisé en modules interconnectés qui forment un pipeline de traitement de l'information :

1. **Collecte de données** : Extraction d'informations depuis des sources variées (articles scientifiques, actualités, conférences)
2. **Analyse des données** : Traitement, classification et extraction de connaissances à partir des données collectées
3. **Gestion des fichiers** : Organisation structurée des données et des résultats d'analyse
4. **Génération de podcasts** : Création de contenus audio résumant les informations importantes
5. **Diffusion** : Distribution des informations via un bot Telegram interactif

```
[Sources externes] → [Collecte] → [Analyse] → [Organisation] → [Diffusion]
     ↓                  ↓            ↓            ↓               ↓
 Articles          Scrapers       NLP/LLM      Système          Telegram
 Brevets           API          Classification  de fichiers     Podcast
 Preprints         RSS          Synthèse                      
```

## Structure des répertoires

Le projet est organisé selon la structure suivante :

```
quantum-crypto-veille/
├── data/                       # Données collectées
│   ├── current/                # Données actuellement en usage
│   ├── archives/               # Données archivées
│   └── index.json              # Index central des fichiers
├── analysis_results/           # Résultats d'analyse
│   ├── daily/                  # Analyses quotidiennes
│   ├── weekly/                 # Analyses hebdomadaires
│   └── monthly/                # Analyses mensuelles
├── podcasts/                   # Podcasts générés
│   ├── weekly/                 # Podcasts hebdomadaires
│   └── monthly/                # Podcasts mensuels
├── docs/                       # Documentation du projet
├── logs/                       # Journaux d'événements
├── src/                        # Code source
│   ├── collectors/             # Modules de collecte de données
│   ├── analyzers/              # Modules d'analyse
│   ├── distributors/           # Modules de diffusion
│   ├── podcast/                # Modules de génération de podcast
│   └── utils/                  # Utilitaires communs
│       ├── logger/             # Système de journalisation
│       └── file_manager/       # Gestionnaire de fichiers
├── tools/                      # Scripts utilitaires
├── main.py                     # Script principal
├── requirements.txt            # Dépendances
└── .env                        # Variables d'environnement
```

## Flux de données

Le flux de données dans le système suit généralement ce parcours :

1. Les **collecteurs** extraient des données de diverses sources et les sauvegardent dans le dossier `data/current/`
2. Le **gestionnaire de fichiers** organise ces données et maintient un index centralisé
3. Les **analyseurs** traitent ces données pour en extraire des tendances, des sujets et des insights
4. Les résultats d'analyse sont sauvegardés dans `analysis_results/` selon leur périodicité
5. Le **générateur de podcasts** utilise ces analyses pour créer des contenus audio
6. Le **bot Telegram** permet aux utilisateurs d'interagir avec les données et les analyses

## Planification des tâches

Le système fonctionne selon une planification définie :
- Collecte et analyse quotidiennes (exécutées à 3h du matin)
- Génération de podcasts hebdomadaire (le lundi)
- Archivage automatique des données anciennes (configurable)

## Points forts du système

- **Modularité** : Architecture en composants indépendants facilitant l'extension et la maintenance
- **Automatisation** : Fonctionnement autonome avec planification des tâches
- **Organisation** : Gestion structurée des fichiers avec indexation centralisée
- **Intelligence artificielle** : Utilisation des LLM pour l'analyse et la génération de contenu
- **Multi-canal** : Diffusion via différents médias (texte et audio)
