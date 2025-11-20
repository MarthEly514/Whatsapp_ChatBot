"""
Service pour interagir avec l'API Twilio
Gère l'envoi et la réception de messages WhatsApp
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from typing import Optional
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TwilioService:
    """Service pour gérer les interactions avec Twilio"""
    
    def __init__(self):
        """Initialise le client Twilio"""
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.whatsapp_number = Config.TWILIO_WHATSAPP_NUMBER
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Client Twilio initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du client Twilio: {e}")
            raise
    
    def send_message(self, to: str, body: str) -> Optional[str]:
        """
        Envoie un message WhatsApp via Twilio
        
        Args:
            to: Numéro du destinataire (format: whatsapp:+33612345678)
            body: Contenu du message
            
        Returns:
            SID du message si succès, None sinon
        """
        try:
            # S'assurer que le numéro est au format whatsapp:+...
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            logger.info(f"Envoi message à {to}: {body[:50]}...")
            
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                body=body,
                to=to
            )
            
            logger.info(f"Message envoyé avec succès. SID: {message.sid}")
            return message.sid
            
        except TwilioRestException as e:
            logger.error(f"Erreur Twilio lors de l'envoi: {e.msg} (Code: {e.code})")
            return None
            
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'envoi: {e}", exc_info=True)
            return None
    
    def send_media_message(self, to: str, body: str, media_url: str) -> Optional[str]:
        """
        Envoie un message WhatsApp avec média via Twilio
        
        Args:
            to: Numéro du destinataire
            body: Contenu du message
            media_url: URL du média (image, vidéo, etc.)
            
        Returns:
            SID du message si succès, None sinon
        """
        try:
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            logger.info(f"Envoi message avec média à {to}")
            
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                body=body,
                media_url=[media_url],
                to=to
            )
            
            logger.info(f"Message avec média envoyé. SID: {message.sid}")
            return message.sid
            
        except TwilioRestException as e:
            logger.error(f"Erreur Twilio: {e.msg} (Code: {e.code})")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi avec média: {e}", exc_info=True)
            return None
    
    def validate_webhook(self, request) -> bool:
        """
        Valide que la requête provient bien de Twilio
        
        Args:
            request: Objet Flask request
            
        Returns:
            True si valide, False sinon
        """
        # Note: Pour une validation complète en production,
        # utilisez twilio.request_validator.RequestValidator
        # avec la signature X-Twilio-Signature
        
        # Vérification basique des champs requis
        required_fields = ['From', 'Body']
        form_data = request.form or request.values
        
        has_all_fields = all(field in form_data for field in required_fields)
        
        if not has_all_fields:
            logger.warning("Webhook Twilio invalide: champs manquants")
            return False
        
        from_number = form_data.get('From', '')
        if not from_number.startswith('whatsapp:'):
            logger.warning(f"Numéro source invalide: {from_number}")
            return False
        
        return True
    
    def parse_incoming_message(self, request) -> Optional[dict]:
        """
        Parse un message entrant de Twilio
        
        Args:
            request: Objet Flask request
            
        Returns:
            Dict avec les infos du message ou None
        """
        try:
            form_data = request.form or request.values
            
            message_data = {
                'from': form_data.get('From', ''),
                'to': form_data.get('To', ''),
                'body': form_data.get('Body', ''),
                'message_sid': form_data.get('MessageSid', ''),
                'account_sid': form_data.get('AccountSid', ''),
                'num_media': int(form_data.get('NumMedia', 0)),
                'profile_name': form_data.get('ProfileName', 'Unknown'),
            }
            
            # Parser les médias s'il y en a
            if message_data['num_media'] > 0:
                message_data['media'] = []
                for i in range(message_data['num_media']):
                    media_info = {
                        'content_type': form_data.get(f'MediaContentType{i}', ''),
                        'url': form_data.get(f'MediaUrl{i}', '')
                    }
                    message_data['media'].append(media_info)
            
            logger.info(f"Message reçu de {message_data['profile_name']} ({message_data['from']})")
            logger.debug(f"Contenu: {message_data['body'][:100]}...")
            
            return message_data
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing du message: {e}", exc_info=True)
            return None
    
    def get_account_info(self) -> Optional[dict]:
        """
        Récupère les informations du compte Twilio
        
        Returns:
            Dict avec les infos du compte
        """
        try:
            if not self.account_sid:
                logger.error("TWILIO_ACCOUNT_SID n'est pas configuré")
                return None

            # self.account_sid est validé ci-dessus et est sûr d'être une str
            account = self.client.api.accounts(self.account_sid).fetch()
            return {
                'sid': account.sid,
                'friendly_name': account.friendly_name,
                'status': account.status,
                'type': account.type
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos compte: {e}")
            return None