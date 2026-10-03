import google.generativeai as genai
client = genai.Client(api_key="YOUR_API_KEY_HERE")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)