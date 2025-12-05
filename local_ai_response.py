import requests
import json

def generate_response(prompt: str, model: str = "phi3") -> str:
    """
    Sends a prompt to a locally running Ollama model and returns the response.
    Requires Ollama running in the background (ollama serve).
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Lower = more deterministic
            "num_ctx": 512       # Context window
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            return f"[Error] HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return f"[Exception] {str(e)}"

if __name__ == "__main__":
    # Test prompt
    test_question = "What is the capital of France?"
    print(f"❓ Prompt: {test_question}\n")
    
    answer = generate_response(test_question)
    print(f"🤖 Response:\n{answer}")

