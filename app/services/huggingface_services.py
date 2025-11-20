"""
Service pour interagir avec l'API Hugging Face
Gère la génération de texte avec les modèles de langage
"""

import requests
import time
from typing import Optional, Dict, Any
from app.config import Config
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class HuggingFaceService:
    """Service pour gérer les interactions avec Hugging Face"""
    
    def __init__(self):
        """Initialise le service Hugging Face"""
        self.api_key = Config.HUGGINGFACE_API_KEY
        self.model = Config.HUGGINGFACE_MODEL
        self.api_url = Config.HUGGINGFACE_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.generation_params = Config.get_huggingface_params()
        
        logger.info(f"Service Hugging Face initialisé avec modèle: {self.model}")
    
    def generate_response(
        self,
        prompt: str,
        user_name: str = "User",
        max_retries: int = 3
    ) -> str:
        """
        Génère une réponse à partir d'un prompt
        
        Args:
            prompt: Texte du message utilisateur
            user_name: Nom de l'utilisateur
            max_retries: Nombre de tentatives en cas d'erreur
            
        Returns:
            Réponse générée par le modèle
        """
        # Construire le prompt avec contexte
        formatted_prompt = self._format_prompt(prompt, user_name)
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": self.generation_params
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Génération de réponse (tentative {attempt + 1}/{max_retries})")
                logger.debug(f"Prompt: {formatted_prompt[:100]}...")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                # Gérer les cas spécifiques
                if response.status_code == 503:
                    # Modèle en cours de chargement
                    logger.warning("Modèle en cours de chargement, attente...")
                    estimated_time = response.json().get('estimated_time', 20)
                    time.sleep(min(estimated_time, 30))
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                # Extraire la réponse
                generated_text = self._extract_response(result)
                
                if generated_text:
                    logger.info(f"Réponse générée avec succès: {generated_text[:100]}...")
                    return generated_text
                else:
                    logger.warning("Réponse vide du modèle")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout lors de la requête (tentative {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur API Hugging Face: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Réponse: {e.response.text}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}", exc_info=True)
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
        
        # Si toutes les tentatives échouent
        return self._get_fallback_response()
    
    def _format_prompt(self, message: str, user_name: str) -> str:
        """
        Formate le prompt selon le modèle utilisé
        
        Args:
            message: Message de l'utilisateur
            user_name: Nom de l'utilisateur
            
        Returns:
            Prompt formaté
        """
        # Détection du type de modèle pour adapter le format
        model_lower = self.model.lower()
        
        if 'mistral' in model_lower or 'mixtral' in model_lower:
            # Format Mistral avec [INST]
            return f"""[INST] Tu es un assistant WhatsApp utile et amical.
Réponds de manière concise et naturelle en 2-3 phrases maximum.

{user_name} te demande: {message} [/INST]"""
        
        elif 'llama' in model_lower:
            # Format Llama 2
            return f"""<s>[INST] <<SYS>>
Tu es un assistant WhatsApp utile et amical.
Réponds de manière concise et naturelle en 2-3 phrases maximum.
<</SYS>>

{user_name} te demande: {message} [/INST]"""
        
        elif 'flan' in model_lower:
            # Format Flan-T5 (simple)
            return f"Réponds à cette question de manière concise: {message}"
        
        else:
            # Format générique
            return f"""Assistant: Tu es un assistant WhatsApp.
User ({user_name}): {message}
Assistant:"""
    
    def _extract_response(self, api_response: Any) -> Optional[str]:
        """
        Extrait le texte généré de la réponse API
        
        Args:
            api_response: Réponse de l'API Hugging Face
            
        Returns:
            Texte généré ou None
        """
        try:
            if isinstance(api_response, list) and len(api_response) > 0:
                # Format standard: [{"generated_text": "..."}]
                if isinstance(api_response[0], dict):
                    generated = api_response[0].get('generated_text', '')
                    
                    # Nettoyer la réponse (enlever le prompt si présent)
                    if '[/INST]' in generated:
                        generated = generated.split('[/INST]')[-1].strip()
                    elif 'Assistant:' in generated:
                        parts = generated.split('Assistant:')
                        generated = parts[-1].strip() if len(parts) > 1 else generated
                    
                    return generated.strip()
                else:
                    return str(api_response[0]).strip()
            
            elif isinstance(api_response, dict):
                # Autre format possible
                return api_response.get('generated_text', '').strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de la réponse: {e}")
            return None
    
    def _get_fallback_response(self) -> str:
        """
        Retourne une réponse de secours en cas d'erreur
        
        Returns:
            Message de secours
        """
        return (
            "Désolé, je rencontre actuellement un problème technique. "
            "Veuillez réessayer dans quelques instants. 🙏"
        )
    
    def check_model_status(self) -> Dict[str, Any]:
        """
        Vérifie le statut du modèle
        
        Returns:
            Dict avec les infos du modèle
        """
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=10
            )
            
            return {
                "status": response.status_code,
                "available": response.status_code == 200,
                "message": response.text if response.status_code != 200 else "OK"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du modèle: {e}")
            return {
                "status": 0,
                "available": False,
                "message": str(e)
            }