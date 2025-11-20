"""
Routes de l'application Flask
Définit les endpoints pour les webhooks et l'API
"""

from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.handlers import MessageHandler
from app.services import TwilioService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Créer le blueprint
webhook_bp = Blueprint('webhook', __name__)

# Initialiser les services
message_handler = MessageHandler()
twilio_service = TwilioService()


@webhook_bp.route('/')
def home():
    """Route d'accueil"""
    return jsonify({
        "service": "WhatsApp Bot avec Twilio et Hugging Face",
        "status": "running",
        "version": "1.0",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/health (GET)",
            "test": "/test/send (POST)"
        }
    })


@webhook_bp.route('/health')
def health_check():
    """
    Endpoint de health check
    Vérifie que tous les services fonctionnent
    """
    try:
        health_status = message_handler.check_health()
        
        status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 503


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint principal pour recevoir les messages de Twilio
    """
    try:
        logger.info("Webhook reçu de Twilio")
        
        # Valider que la requête vient de Twilio
        if not twilio_service.validate_webhook(request):
            logger.warning("Webhook invalide reçu")
            return "Unauthorized", 401
        
        # Parser le message
        message_data = twilio_service.parse_incoming_message(request)
        
        if not message_data:
            logger.error("Impossible de parser le message")
            return "Bad Request", 400
        
        # Traiter le message de manière asynchrone
        # Note: Pour une production à grande échelle, utilisez Celery
        message_handler.process_message(message_data)
        
        # Twilio attend une réponse TwiML vide
        response = MessagingResponse()
        return str(response), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du webhook: {e}", exc_info=True)
        # Toujours renvoyer 200 pour éviter les retries de Twilio
        response = MessagingResponse()
        return str(response), 200, {'Content-Type': 'text/xml'}


@webhook_bp.route('/test/send', methods=['POST'])
def test_send_message():
    """
    Endpoint de test pour envoyer un message manuellement
    
    Body JSON:
    {
        "to": "+33612345678",
        "message": "Votre message ici"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Body JSON requis"}), 400
        
        to = data.get('to')
        message = data.get('message')
        
        if not to or not message:
            return jsonify({
                "error": "Paramètres 'to' et 'message' requis"
            }), 400
        
        # Envoyer le message
        message_sid = twilio_service.send_message(to, message)
        
        if message_sid:
            return jsonify({
                "success": True,
                "message_sid": message_sid,
                "to": to
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Échec de l'envoi du message"
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message de test: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@webhook_bp.route('/test/ai', methods=['POST'])
def test_ai_response():
    """
    Endpoint de test pour tester la génération de réponse IA
    
    Body JSON:
    {
        "prompt": "Votre question ici",
        "user_name": "Test User" (optionnel)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Body JSON requis"}), 400
        
        prompt = data.get('prompt')
        user_name = data.get('user_name', 'Test User')
        
        if not prompt:
            return jsonify({"error": "Paramètre 'prompt' requis"}), 400
        
        # Générer la réponse
        from app.services import HuggingFaceService
        hf_service = HuggingFaceService()
        response = hf_service.generate_response(prompt, user_name)
        
        return jsonify({
            "success": True,
            "prompt": prompt,
            "response": response
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors du test IA: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@webhook_bp.errorhandler(404)
def not_found(error):
    """Gestionnaire pour les routes non trouvées"""
    return jsonify({
        "error": "Route non trouvée",
        "status": 404
    }), 404


@webhook_bp.errorhandler(500)
def internal_error(error):
    """Gestionnaire pour les erreurs internes"""
    logger.error(f"Erreur interne: {error}", exc_info=True)
    return jsonify({
        "error": "Erreur interne du serveur",
        "status": 500
    }), 500