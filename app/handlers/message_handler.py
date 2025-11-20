"""
Gestionnaire principal pour traiter les messages entrants
"""

from typing import Optional, Dict, Any
from app.services import TwilioService, HuggingFaceService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MessageHandler:
    """Classe pour gérer le traitement des messages"""
    
    def __init__(self):
        """Initialise les services nécessaires"""
        self.twilio_service = TwilioService()
        self.huggingface_service = HuggingFaceService()
        logger.info("MessageHandler initialisé")
    
    def process_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Traite un message entrant et envoie une réponse
        
        Args:
            message_data: Données du message parsées par Twilio
            
        Returns:
            True si le traitement a réussi, False sinon
        """
        if not message_data:
            logger.warning("Message data vide")
            return False
        
        sender = message_data.get('from')
        if not sender or not isinstance(sender, str):
            logger.error(f"Sender invalide dans message_data: {sender!r}")
            return False
        body = message_data.get('body', '').strip()
        profile_name = message_data.get('profile_name', 'User')
        num_media = message_data.get('num_media', 0)
        
        try:
            # Gérer les différents types de messages
            if num_media > 0:
                # Message avec média
                response = self._handle_media_message(message_data)
            elif body:
                # Message texte
                response = self._handle_text_message(body, profile_name)
            else:
                # Message vide
                response = "Désolé, je n'ai pas reçu de contenu. Envoyez-moi un message ! 💬"
            
            # Envoyer la réponse
            if response:
                success = self.twilio_service.send_message(sender, response)
                if success:
                    logger.info(f"Réponse envoyée avec succès à {sender}")
                    return True
                else:
                    logger.error(f"Échec de l'envoi de la réponse à {sender}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message: {e}", exc_info=True)
            
            # Tenter d'envoyer un message d'erreur
            try:
                error_message = (
                    "Désolé, une erreur s'est produite lors du traitement "
                    "de votre message. Veuillez réessayer. 🙏"
                )
                self.twilio_service.send_message(sender, error_message)
            except:
                pass
            
            return False
    
    def _handle_text_message(self, text: str, user_name: str) -> str:
        """
        Traite un message texte et génère une réponse
        
        Args:
            text: Contenu du message
            user_name: Nom de l'utilisateur
            
        Returns:
            Réponse à envoyer
        """
        logger.info(f"Traitement message texte: {text[:100]}...")
        
        # Commandes spéciales
        text_lower = text.lower().strip()
        
        if text_lower in ['/start', '/aide', '/help']:
            return self._get_help_message()
        
        elif text_lower == '/info':
            return self._get_info_message()
        
        elif text_lower == '/ping':
            return "🏓 Pong! Le bot est actif."
        
        # Générer une réponse avec Hugging Face
        response = self.huggingface_service.generate_response(text, user_name)
        
        return response
    
    def _handle_media_message(self, message_data: Dict[str, Any]) -> str:
        """
        Traite un message contenant des médias
        
        Args:
            message_data: Données du message avec médias
            
        Returns:
            Réponse à envoyer
        """
        num_media = message_data.get('num_media', 0)
        media_list = message_data.get('media', [])
        
        logger.info(f"Message avec {num_media} média(s) reçu")
        
        # Analyser les types de médias
        media_types = [m.get('content_type', '') for m in media_list]
        
        response = f"Merci pour {'les médias' if num_media > 1 else 'le média'} ! 📎\n\n"
        
        if any('image' in mt for mt in media_types):
            response += "J'ai bien reçu votre image. "
        if any('audio' in mt for mt in media_types):
            response += "J'ai bien reçu votre audio. "
        if any('video' in mt for mt in media_types):
            response += "J'ai bien reçu votre vidéo. "
        if any('document' in mt for mt in media_types):
            response += "J'ai bien reçu votre document. "
        
        response += (
            "\n\nActuellement, je peux uniquement traiter des messages texte. "
            "Envoyez-moi une question et je vous répondrai ! 💬"
        )
        
        return response
    
    def _get_help_message(self) -> str:
        """
        Retourne le message d'aide
        
        Returns:
            Message d'aide
        """
        return """🤖 *Bot WhatsApp avec IA*

Je suis un assistant intelligent propulsé par Hugging Face. Posez-moi n'importe quelle question et je ferai de mon mieux pour vous aider !

*Commandes disponibles:*
• /aide - Afficher ce message
• /info - Informations sur le bot
• /ping - Vérifier si le bot est actif

Envoyez simplement votre message et je vous répondrai ! 💬"""
    
    def _get_info_message(self) -> str:
        """
        Retourne les informations sur le bot
        
        Returns:
            Message d'information
        """
        from app.config import Config
        
        return f"""ℹ️ *Informations sur le bot*

• Modèle IA: {Config.HUGGINGFACE_MODEL.split('/')[-1]}
• Plateforme: Hugging Face Inference API
• Service WhatsApp: Twilio
• Version: 1.0

Le bot utilise des modèles de langage avancés pour comprendre et répondre à vos messages de manière naturelle."""
    
    def check_health(self) -> Dict[str, Any]:
        """
        Vérifie la santé de tous les services
        
        Returns:
            Dict avec le statut de chaque service
        """
        health_status = {
            "status": "healthy",
            "services": {}
        }
        
        # Vérifier Twilio
        try:
            twilio_info = self.twilio_service.get_account_info()
            health_status["services"]["twilio"] = {
                "status": "ok" if twilio_info else "error",
                "info": twilio_info
            }
        except Exception as e:
            health_status["services"]["twilio"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Vérifier Hugging Face
        try:
            hf_status = self.huggingface_service.check_model_status()
            health_status["services"]["huggingface"] = hf_status
            if not hf_status.get("available"):
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["huggingface"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        return health_status