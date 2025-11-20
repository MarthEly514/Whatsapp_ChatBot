"""
Package principal de l'application WhatsApp Bot
Initialise Flask et configure l'application
"""

from flask import Flask
from app.config import Config
from app.utils.logger import setup_logger
import os

# Initialiser le logger
logger = setup_logger(__name__)


def create_app(config_class=Config):
    """
    Factory pour créer et configurer l'application Flask
    
    Args:
        config_class: Classe de configuration à utiliser
        
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Créer le dossier de logs s'il n'existe pas
    log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Enregistrer les routes
    from app.routes import webhook_bp
    app.register_blueprint(webhook_bp)
    
    logger.info("Application WhatsApp Bot initialisée avec succès")
    logger.info(f"Mode Debug: {app.config.get('DEBUG')}")
    logger.info(f"Modèle Hugging Face: {app.config.get('HUGGINGFACE_MODEL')}")
    
    return app