import json
import random
import re
import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- Added this import

app = Flask(__name__)

# <-- Added this line to allow your GitHub site to talk to this backend
CORS(app) 

# Get the absolute path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load the structured knowledge base
try:
    with open(os.path.join(BASE_DIR, 'knowledge_base.json'), 'r', encoding='utf-8') as file:
        kb = json.load(file)
except FileNotFoundError:
    print("Error: knowledge_base.json not found.")
    kb = {"intents": []}

def clean_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())

def get_response(user_msg):
    user_msg_clean = clean_text(user_msg)
    user_words = set(user_msg_clean.split())

    best_match = None
    highest_score = 0

    for intent in kb.get('intents', []):
        for pattern in intent['patterns']:
            pattern_clean = clean_text(pattern)
            pattern_words = set(pattern_clean.split())
            
            if not pattern_words:
                continue
                
            intersection = user_words.intersection(pattern_words)
            score = len(intersection) / float(len(pattern_words))
            
            if score > highest_score:
                highest_score = score
                best_match = intent

    if highest_score >= 0.3 and best_match:
        template = random.choice(best_match['response_templates'])
        return template.format(**best_match['data'])
    
    return "I'm not quite sure about that. Try asking about the hackathon dates, rules, themes, or registration fee!"

# --- ROUTES ---

# Note: We removed the '/' route because GitHub Pages handles your HTML now!

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
        
    user_message = data['message']
    bot_reply = get_response(user_message)
    
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000)