#!/usr/bin/env python3
"""
Test which Gemini models are available with your API key.
Run this to see what models your GOOGLE_API_KEY has access to.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ GOOGLE_API_KEY not found in environment")
    exit(1)

print(f"✅ API Key found: {GOOGLE_API_KEY[:20]}...")

try:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    
    print("\n📋 Available models:")
    print("-" * 60)
    
    for model in genai.list_models():
        # Check if supports generateContent (what we need)
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            if hasattr(model, 'display_name'):
                print(f"  Display: {model.display_name}")
            if hasattr(model, 'description'):
                print(f"  Desc: {model.description[:80]}...")
            print()
    
    print("-" * 60)
    print("\n🔧 Testing gemini-2.0-flash-exp...")
    
    try:
        test_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = test_model.generate_content("Say 'Hello from Gemini!'")
        print(f"✅ Success! Response: {response.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("\nTrying other models...")
        
        # Try alternatives
        for model_name in ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']:
            try:
                print(f"\nTesting {model_name}...")
                test_model = genai.GenerativeModel(model_name)
                response = test_model.generate_content("Say 'Hello!'")
                print(f"✅ {model_name} works! Response: {response.text}")
                break
            except Exception as e2:
                print(f"❌ {model_name} failed: {e2}")
        
except ImportError:
    print("❌ google-generativeai not installed")
    print("Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")
