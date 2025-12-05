"""
Test script to verify AI (Ollama) connection and functionality.
"""
import requests
import json
from config import settings

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    print("🔍 Testing Ollama Connection...\n")
    
    # Test 1: Check if Ollama server is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama server is running!")
            print(f"📦 Available models: {len(models)}")
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
        else:
            print(f"❌ Ollama server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama server!")
        print("   Make sure Ollama is running:")
        print("   - Windows/macOS: Open the Ollama app")
        print("   - Or run: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False
    
    print()
    
    # Test 2: Check if configured model is available
    model = settings.get("ai_model", "phi3")
    print(f"🔍 Checking if model '{model}' is available...")
    
    model_names = [m.get('name', '') for m in models]
    if any(model in name for name in model_names):
        print(f"✅ Model '{model}' is available!")
    else:
        print(f"⚠️  Model '{model}' not found in available models.")
        print(f"   Install it with: ollama pull {model}")
        return False
    
    print()
    
    # Test 3: Test AI generation
    print("🧠 Testing AI generation...")
    try:
        test_prompt = "Say 'Hello, I am connected!' in one sentence."
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": test_prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 512}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "").strip()
            print(f"✅ AI generation successful!")
            print(f"📝 Prompt: {test_prompt}")
            print(f"🤖 Response: {ai_response}")
            return True
        else:
            print(f"❌ AI generation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during AI generation: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AI Connection Test")
    print("=" * 50)
    print()
    
    success = test_ollama_connection()
    
    print()
    print("=" * 50)
    if success:
        print("✅ All tests passed! AI is ready to use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 50)

