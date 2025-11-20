"""
Configuration de l'application
Charge les variables d'environnement et définit les paramètres
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Classe de configuration principale"""
    
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Configuration Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+12525818652')
    
    # Configuration Hugging Face
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    HUGGINGFACE_MODEL = os.getenv('HUGGINGFACE_MODEL', '="HuggingFaceH4/zephyr-7b-beta:featherless-ai"')
    HUGGINGFACE_API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
    
    # Paramètres de génération pour Hugging Face
    HF_MAX_NEW_TOKENS = int(os.getenv('HF_MAX_NEW_TOKENS', 500))
    HF_TEMPERATURE = float(os.getenv('HF_TEMPERATURE', 0.7))
    HF_TOP_P = float(os.getenv('HF_TOP_P', 0.95))
    HF_REPETITION_PENALTY = float(os.getenv('HF_REPETITION_PENALTY', 1.1))
    
    # Configuration des logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/whatsapp_bot.log')
    
    @staticmethod
    def validate():
        """
        Valide que toutes les configurations requises sont présentes
        
        Raises:
            ValueError: Si une configuration requise est manquante
        """
        required_vars = {
            'TWILIO_ACCOUNT_SID': Config.TWILIO_ACCOUNT_SID,
            'TWILIO_AUTH_TOKEN': Config.TWILIO_AUTH_TOKEN,
            'HUGGINGFACE_API_KEY': Config.HUGGINGFACE_API_KEY,
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(
                f"Variables d'environnement manquantes: {', '.join(missing_vars)}\n"
                f"Veuillez créer un fichier .env avec ces variables."
            )
    
    @classmethod
    def get_huggingface_params(cls):
        """
        Retourne les paramètres de génération pour Hugging Face
        
        Returns:
            dict: Paramètres de génération
        """
        return {
            "max_new_tokens": cls.HF_MAX_NEW_TOKENS,
            "temperature": cls.HF_TEMPERATURE,
            "top_p": cls.HF_TOP_P,
            "repetition_penalty": cls.HF_REPETITION_PENALTY,
            "return_full_text": False
        }