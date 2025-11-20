"""
Script de test pour le bot WhatsApp
Teste les différents endpoints et fonctionnalités
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"


def print_separator(title=""):
    """Affiche un séparateur visuel"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def test_home():
    """Test la route d'accueil"""
    print_separator("Test 1: Route d'accueil")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Réponse: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Test réussi")
            return True
        else:
            print("❌ Test échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_health():
    """Test le health check"""
    print_separator("Test 2: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        
        data = response.json()
        print(f"Status général: {data.get('status')}")
        
        # Afficher le statut de chaque service
        services = data.get('services', {})
        for service_name, service_info in services.items():
            status = service_info.get('status', 'unknown')
            print(f"  - {service_name}: {status}")
        
        if response.status_code in [200, 503]:  # 503 = degraded mais OK
            print("✅ Test réussi")
            return True
        else:
            print("❌ Test échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_ai_response():
    """Test la génération de réponse IA"""
    print_separator("Test 3: Génération de réponse IA")
    
    payload = {
        "prompt": "Bonjour, comment ça va?",
        "user_name": "Test User"
    }
    
    try:
        print(f"Prompt: {payload['prompt']}")
        print("Génération en cours...")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/test/ai",
            json=payload,
            timeout=120
        )
        elapsed = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Temps de réponse: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nRéponse IA:")
            print(f"  {data.get('response', 'Aucune réponse')}")
            print("\n✅ Test réussi")
            return True
        else:
            print(f"Erreur: {response.text}")
            print("❌ Test échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_send_message():
    """Test l'envoi d'un message (optionnel)"""
    print_separator("Test 4: Envoi de message (OPTIONNEL)")
    
    print("⚠️  Ce test envoie un vrai message WhatsApp!")
    print("Vous devez avoir:")
    print("  1. Un numéro WhatsApp activé dans Twilio Sandbox")
    print("  2. Le numéro doit avoir rejoint le sandbox")
    
    choice = input("\nVoulez-vous continuer? (o/n): ").lower()
    
    if choice != 'o':
        print("Test ignoré")
        return None
    
    phone = input("Entrez le numéro (ex: +33612345678): ")
    
    payload = {
        "to": phone,
        "message": "🤖 Test du bot WhatsApp! Si vous recevez ce message, tout fonctionne correctement!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/test/send",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message SID: {data.get('message_sid')}")
            print("✅ Message envoyé avec succès!")
            print(f"Vérifiez le numéro {phone}")
            return True
        else:
            print(f"Erreur: {response.text}")
            print("❌ Test échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_webhook():
    """Test la simulation d'un webhook Twilio"""
    print_separator("Test 5: Simulation Webhook Twilio")
    
    # Simuler les données d'un webhook Twilio
    webhook_data = {
        "From": "whatsapp:+33612345678",
        "To": "whatsapp:+14155238886",
        "Body": "Test de webhook!",
        "MessageSid": "SM" + "x" * 32,
        "AccountSid": "AC" + "x" * 32,
        "NumMedia": "0",
        "ProfileName": "Test User"
    }
    
    try:
        print("Envoi de données webhook simulées...")
        
        response = requests.post(
            f"{BASE_URL}/webhook",
            data=webhook_data,
            timeout=120
        )
        
        print(f"Status: {response.status_code}")
        
        # Twilio attend une réponse XML (TwiML)
        if response.status_code == 200:
            print("✅ Webhook traité (vérifiez les logs serveur)")
            return True
        else:
            print(f"Erreur: {response.text}")
            print("❌ Test échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def run_all_tests():
    """Lance tous les tests"""
    print("\n" + "🧪" * 30)
    print("  TESTS DU BOT WHATSAPP (TWILIO + HUGGING FACE)")
    print("🧪" * 30)
    
    print("\n⚠️  Assurez-vous que le serveur est lancé (python main.py)")
    input("Appuyez sur Entrée pour continuer...")
    
    results = []
    
    # Tests automatiques
    results.append(("Route d'accueil", test_home()))
    results.append(("Health Check", test_health()))
    results.append(("Génération IA", test_ai_response()))
    results.append(("Webhook Simulation", test_webhook()))
    
    # Test optionnel
    send_result = test_send_message()
    if send_result is not None:
        results.append(("Envoi Message", send_result))
    
    # Résumé
    print_separator("RÉSUMÉ DES TESTS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Tous les tests ont réussi!")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")