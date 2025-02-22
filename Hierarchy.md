```yaml
iot_project/
├── README.md                      # Documentation générale et instructions d'installation
├── docs/
│   └── architecture.md            # Description de l'architecture globale du projet
├── server/                        # Code du serveur (exécuté sur le Raspberry Pi)
│   ├── app.py                     # Point d'entrée principal de l'application Flask
│   ├── models.py                  # Définition des modèles SQLAlchemy (utilisateurs, événements, SMS, température, etc.)
│   ├── config.py                  # Paramètres de configuration (clé secrète, port, etc.)
│   ├── requirements.txt           # Liste des dépendances Python (Flask, SQLAlchemy, etc.)
│   ├── static/                    # Fichiers statiques utilisés par Flask (CSS, JS, images)
│   │   ├── css/
│   │   │   └── main.css           # Feuille de style globale pour l'admin et les pages côté serveur
│   │   ├── js/
│   │   │   └── main.js            # Scripts JavaScript pour l'interface administrateur
│   │   └── images/                # Images et icônes du projet
│   ├── templates/                 # Templates HTML de Flask
│   │   ├── base.html              # Template de base pour la réutilisation des structures communes (header, footer)
│   │   ├── index.html             # Page d'accueil du dashboard administrateur
│   │   ├── dashboard.html         # Tableau de bord affichant les statistiques (SMS envoyés, alertes température, etc.)
│   │   └── settings.html          # Page de configuration des fonctionnalités et des paramètres (durée de rappel, activation/désactivation, etc.)
│   └── tests/                     # Tests unitaires et d'intégration du backend
│       └── test_app.py            # Exemples de tests pour l'application Flask
└── client/                        # Code du client (interface accessible depuis la machine sur le même réseau)
    ├── index.html                 # Page d'accueil du client, point d'accès aux fonctionnalités
    ├── css/
    │   └── styles.css             # Feuilles de style spécifiques pour le client
    ├── js/
    │   └── app.js                 # Logique JavaScript pour les interactions côté client (envoi des requêtes au serveur)
    └── assets/                    # Autres ressources (images, icônes, etc.)
        └── images/

```
