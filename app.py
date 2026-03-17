import json
import random
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Load the structured knowledge base
try:
    # ADDED: encoding='utf-8' prevents the strange symbol errors
    with open('knowledge_base.json', 'r', encoding='utf-8') as file:
        kb = json.load(file)
except FileNotFoundError:
    print("Error: knowledge_base.json not found. Make sure it is in the same directory.")
    kb = {"intents": []}

def clean_text(text):
    """Removes punctuation and converts text to lowercase for easier matching."""
    return re.sub(r'[^\w\s]', '', text.lower())

def get_response(user_msg):
    """Matches the user query against the JSON patterns and formats the response."""
    user_msg_clean = clean_text(user_msg)
    user_words = set(user_msg_clean.split())

    best_match = None
    highest_score = 0

    # Iterate through the intents to find the highest overlapping pattern
    for intent in kb.get('intents', []):
        for pattern in intent['patterns']:
            pattern_clean = clean_text(pattern)
            pattern_words = set(pattern_clean.split())
            
            # Calculate a simple match score based on overlapping words
            if not pattern_words:
                continue
                
            intersection = user_words.intersection(pattern_words)
            score = len(intersection) / float(len(pattern_words))
            
            if score > highest_score:
                highest_score = score
                best_match = intent

    # Threshold (0.3) prevents the bot from guessing completely unrelated topics
    if highest_score >= 0.3 and best_match:
        # Pick a random template from the matched intent
        template = random.choice(best_match['response_templates'])
        # Dynamically inject the structured data into the template string
        return template.format(**best_match['data'])
    
    # Fallback response if the query doesn't match anything
    return "I'm not quite sure about that. Try asking about the hackathon dates, rules, themes, or registration fee!"

# --- ROUTES ---

@app.route('/')
def home():
    """Serves the frontend UI."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """API endpoint to receive messages and return the bot's response."""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
        
    user_message = data['message']
    bot_reply = get_response(user_message)
    
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    # Run the server in debug mode for development
    app.run(debug=True, port=5000)