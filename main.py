"""
Point d'entrée principal de l'application
Lance le serveur Flask
"""

import sys
from app import create_app
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Fonction principale pour lancer l'application"""
    try:
        # Valider la configuration
        logger.info("Validation de la configuration...")
        Config.validate()
        logger.info("Configuration validée ✓")
        
        # Créer l'application
        app = create_app()
        
        # Informations de démarrage
        logger.info("=" * 60)
        logger.info("🚀 Démarrage du Bot WhatsApp")
        logger.info("=" * 60)
        logger.info(f"📱 Service: Twilio WhatsApp")
        logger.info(f"🤖 Modèle IA: {Config.HUGGINGFACE_MODEL}")
        logger.info(f"🌍 Serveur: {Config.HOST}:{Config.PORT}")
        logger.info(f"🐛 Mode Debug: {Config.DEBUG}")
        logger.info("=" * 60)
        
        # Lancer le serveur
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
        
    except ValueError as e:
        logger.error(f"❌ Erreur de configuration: {e}")
        logger.error("Veuillez vérifier votre fichier .env")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()