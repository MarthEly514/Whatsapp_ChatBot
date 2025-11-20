🤖 Bot WhatsApp avec Twilio et Hugging Face
Bot WhatsApp intelligent utilisant Twilio pour la messagerie et les modèles Hugging Face pour générer des réponses automatiques avec l'IA.

📋 Fonctionnalités
✅ Réception et envoi de messages WhatsApp via Twilio
✅ Génération de réponses avec modèles Hugging Face (Mistral, Llama, Flan-T5, etc.)
✅ Support des messages texte et médias
✅ Commandes spéciales (/aide, /info, /ping)
✅ Architecture modulaire et propre
✅ Logs détaillés avec rotation
✅ Health check et endpoints de test
✅ Gestion d'erreurs robuste
✅ Prêt pour la production
🏗️ Structure du projet
whatsapp-bot-twilio/
│
├── app/
│   ├── __init__.py              # Initialisation Flask
│   ├── config.py                # Configuration centralisée
│   ├── routes.py                # Routes et webhooks
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── twilio_service.py    # API Twilio
│   │   └── huggingface_service.py # API Hugging Face
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── message_handler.py   # Logique métier
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # Configuration logs
│
├── tests/
│   └── test_bot.py              # Tests automatisés
│
├── main.py                      # Point d'entrée
├── requirements.txt             # Dépendances
├── .env.example                 # Template configuration
├── .gitignore                   # Fichiers à ignorer
└── README.md                    # Ce fichier
🚀 Installation rapide
1. Prérequis
Python 3.8+
Compte Twilio avec WhatsApp activé
Clé API Hugging Face
2. Cloner et installer
bash
# Créer le dossier du projet
mkdir whatsapp-bot-twilio
cd whatsapp-bot-twilio

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
3. Configuration Twilio
a) Créer un compte Twilio
Inscrivez-vous sur twilio.com
Vérifiez votre numéro de téléphone
Obtenez votre essai gratuit ($15 de crédit)
b) Activer WhatsApp Sandbox
Dans le dashboard Twilio, allez dans Messaging > Try it out > Send a WhatsApp message
Suivez les instructions pour rejoindre le sandbox:
Envoyez un message WhatsApp au numéro Twilio fourni
Message: join <votre-code-sandbox>
Notez le numéro WhatsApp Twilio (ex: whatsapp:+14155238886)
c) Récupérer les credentials
Dans le Dashboard Twilio:

Account SID: Sur la page d'accueil
Auth Token: Sur la page d'accueil (cliquez sur "Show")
4. Configuration Hugging Face
a) Créer un compte
Inscrivez-vous sur huggingface.co
Allez dans Settings > Access Tokens
Créez un nouveau token (Read access suffit)
b) Choisir un modèle
Modèles recommandés (gratuits via Inference API):

Pour le français:

mistralai/Mistral-7B-Instruct-v0.2 ⭐ Recommandé
mistralai/Mixtral-8x7B-Instruct-v0.1 (plus puissant)
Multilingues:

google/flan-t5-large (rapide, bon pour questions/réponses)
facebook/blenderbot-400M-distill (conversationnel)
Avec accès requis:

meta-llama/Llama-2-7b-chat-hf (demander l'accès sur HF)
meta-llama/Meta-Llama-3-8B-Instruct
5. Créer le fichier .env
bash
cp .env.example .env
nano .env  # ou votre éditeur préféré
Remplissez avec vos credentials:

env
# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=votre_auth_token_ici
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Hugging Face
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Serveur
PORT=5000
HOST=0.0.0.0
DEBUG=False
LOG_LEVEL=INFO
🎯 Utilisation
Démarrage du serveur
bash
python main.py
Le serveur démarre sur http://0.0.0.0:5000

Configurer le webhook Twilio
Option 1: ngrok (développement local)
bash
# Installer ngrok: https://ngrok.com/download
ngrok http 5000

# Utiliser l'URL HTTPS fournie (ex: https://abc123.ngrok.io)
Dans Twilio:

Messaging > Settings > WhatsApp Sandbox Settings
When a message comes in: https://votre-url.ngrok.io/webhook
HTTP: POST
Sauvegarder
Option 2: Déploiement cloud (production)
Déployez sur Heroku, Render, Railway, etc., puis configurez l'URL publique dans Twilio.

Tests
bash
# Lancer tous les tests
python tests/test_bot.py

# Ou tester individuellement:
# 1. Health check
curl http://localhost:5000/health

# 2. Test IA
curl -X POST http://localhost:5000/test/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Bonjour!", "user_name": "Test"}'

# 3. Envoyer un message (remplacez le numéro)
curl -X POST http://localhost:5000/test/send \
  -H "Content-Type: application/json" \
  -d '{"to": "+33612345678", "message": "Test!"}'
💬 Utilisation WhatsApp
Une fois le webhook configuré:

Envoyer un message au numéro Twilio sandbox
Le bot répond automatiquement avec l'IA
Commandes disponibles
/aide ou /help - Afficher l'aide
/info - Informations sur le bot
/ping - Vérifier que le bot est actif
Tout autre texte → Réponse générée par l'IA
📊 Logs
Les logs sont enregistrés dans:

Console: Affichage en temps réel
Fichier: logs/whatsapp_bot.log (rotation automatique à 10MB)
Exemple:

2024-01-15 10:30:00 - app.services.twilio_service - INFO - Message reçu de Test User (whatsapp:+33612345678)
2024-01-15 10:30:01 - app.handlers.message_handler - INFO - Traitement message texte: Bonjour!
2024-01-15 10:30:05 - app.services.huggingface_service - INFO - Réponse générée avec succès
2024-01-15 10:30:06 - app.services.twilio_service - INFO - Message envoyé avec succès
🔧 Configuration avancée
Personnaliser le modèle IA
Dans app/services/huggingface_service.py, méthode _format_prompt():

python
def _format_prompt(self, message: str, user_name: str) -> str:
    # Personnalisez le prompt système ici
    return f"""[INST] Tu es un expert en [VOTRE DOMAINE].
Réponds de manière [VOTRE STYLE].

{user_name} demande: {message} [/INST]"""
Paramètres de génération
Dans .env, ajoutez:

env
HF_MAX_NEW_TOKENS=500      # Longueur max de réponse
HF_TEMPERATURE=0.7         # Créativité (0.1-1.0)
HF_TOP_P=0.95             # Diversité
HF_REPETITION_PENALTY=1.1  # Éviter répétitions
Ajouter des commandes
Dans app/handlers/message_handler.py:

python
def _handle_text_message(self, text: str, user_name: str) -> str:
    text_lower = text.lower().strip()
    
    if text_lower == '/weather':
        return "🌤️ Fonctionnalité météo à venir!"
    
    # ... reste du code
🚀 Déploiement en production
Heroku
bash
# Créer un Procfile
echo "web: gunicorn main:app" > Procfile

# Déployer
heroku create mon-bot-whatsapp
heroku config:set TWILIO_ACCOUNT_SID=xxx TWILIO_AUTH_TOKEN=yyy
git push heroku main
Railway / Render
Connectez votre repo GitHub
Configurez les variables d'environnement
Deploy automatique
Docker (optionnel)
dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
⚠️ Limitations et quotas
Twilio (compte gratuit)
$15 de crédit initial
Sandbox WhatsApp: nombres limités de destinataires
Production: numéro WhatsApp Business requis (~$0.005/message)
Hugging Face Inference API
Gratuit avec rate limiting
Modèles peuvent être lents à charger (cold start)
Pour production: considérez Inference Endpoints ($$$) ou hébergement local
🐛 Dépannage
Problème: Webhook non reçu
Solutions:

Vérifiez que ngrok est lancé
Vérifiez l'URL dans Twilio (doit être HTTPS)
Vérifiez les logs: tail -f logs/whatsapp_bot.log
Problème: Modèle Hugging Face lent/timeout
Solutions:

Le modèle se charge (cold start), attendez 20-30s
Changez pour un modèle plus petit (flan-t5-large)
Augmentez le timeout dans huggingface_service.py
Problème: Twilio Auth Error
Solutions:

Vérifiez ACCOUNT_SID et AUTH_TOKEN
Assurez-vous que le compte n'est pas suspendu
Régénérez l'Auth Token si nécessaire
Problème: Messages WhatsApp non envoyés
Solutions:

Vérifiez que le destinataire a rejoint le sandbox
Vérifiez le format du numéro (whatsapp:+33...)
Vérifiez le crédit Twilio
📚 Ressources
Twilio WhatsApp Docs
Hugging Face Inference API
Flask Documentation
Twilio Python SDK
🔒 Sécurité
Bonnes pratiques:
✅ Ne commitez JAMAIS votre .env
✅ Utilisez des variables d'environnement en production
✅ Validez les webhooks Twilio (signature)
✅ Limitez les rate limits
✅ Surveillez les coûts API
✅ HTTPS obligatoire pour webhooks
Validation webhook Twilio (avancé)
Pour production, ajoutez dans twilio_service.py:

python
from twilio.request_validator import RequestValidator

def validate_webhook(self, request):
    validator = RequestValidator(self.auth_token)
    signature = request.headers.get('X-Twilio-Signature', '')
    url = request.url
    params = request.form
    
    return validator.validate(url, params, signature)
📈 Métriques recommandées
Nombre de messages reçus/envoyés
Temps de réponse moyen (Hugging Face)
Taux d'erreur
Coûts API (Twilio + HF)
🤝 Support
Pour toute question:

Vérifiez les logs: logs/whatsapp_bot.log
Lancez les tests: python tests/test_bot.py
Consultez la documentation Twilio/HF
📄 Licence
Projet à usage éducatif. Adaptez selon vos besoins !

🎉 C'est parti !
Votre bot WhatsApp intelligent est prêt à converser ! 🚀

bash
# Lancez le serveur
python main.py

# Envoyez un message WhatsApp
# Le bot répond automatiquement avec l'IA !
