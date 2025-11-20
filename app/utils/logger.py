"""
Configuration du système de logging
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import Config


def setup_logger(name):
    """
    Configure et retourne un logger
    
    Args:
        name: Nom du logger (généralement __name__ du module)
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter de dupliquer les handlers
    if logger.handlers:
        return logger
    
    # Définir le niveau de log
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour le fichier (avec rotation)
    try:
        log_file = Config.LOG_FILE
        log_dir = os.path.dirname(log_file)
        
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Rotation: max 10MB par fichier, garder 5 fichiers
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        logger.warning(f"Impossible de créer le fichier de log: {e}")
    
    return logger