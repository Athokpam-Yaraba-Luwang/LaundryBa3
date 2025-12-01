# google/genai/__init__.py
import os
import google.generativeai as real_genai

class Models:
    def generate_content(self, model, contents):
        # Bridge to real Gemini API if available, or mock
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("GenAI Shim: No valid API Key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY.")

        try:
            real_genai.configure(api_key=api_key)
            m = real_genai.GenerativeModel(model)
            # Convert ADK format to real API format
            real_contents = []
            if isinstance(contents, str):
                real_contents.append(contents)
            elif isinstance(contents, list):
                if len(contents) > 0 and isinstance(contents[0], dict) and "parts" in contents[0]:
                     # ADK format: contents=[{"role":"user","parts":[{"image": img, "text":"..."}]}]
                    parts = contents[0]["parts"]
                    for p in parts:
                        if "image" in p:
                            real_contents.append(p["image"])
                        if "text" in p:
                            real_contents.append(p["text"])
                else:
                    # List of strings or other objects
                    real_contents = contents
            
            return m.generate_content(real_contents)
        except Exception as e:
            print(f"GenAI Shim Error: {e}")
            raise e

class Client:
    def __init__(self):
        self.models = Models()
