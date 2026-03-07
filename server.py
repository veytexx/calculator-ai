from flask import Flask, request, jsonify
from openai import OpenAI
import os
import re

app = Flask(__name__)

# WICHTIG: Stelle sicher, dass OPENAI_API_KEY in Vercel hinterlegt ist!
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def calculate_left_to_right(expression):
    try:
        # Entferne alles außer Zahlen und Operatoren
        clean = re.sub(r'[^0-9+\-*/.]', '', expression)
        tokens = re.findall(r'\d+\.?\d*|[+\-*/]', clean)
        
        if not tokens: return None
        
        result = float(tokens[0])
        i = 1
        while i < len(tokens):
            op = tokens[i]
            val = float(tokens[i+1])
            if op == '+': result += val
            elif op == '-': result -= val
            elif op == '*': result *= val
            elif op == '/': 
                if val == 0: return None
                result /= val
            i += 2
        return int(result) if result == int(result) else result
    except:
        return None

@app.route("/", methods=["GET"])
def home():
    return "Calculator AI is online."

@app.route("/calc", methods=["POST"])
def calc():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"response": "No data received."}), 400

        question = data.get("question", "")
        lang = data.get("lang", "en-us")
        is_custom = data.get("fullCustomPrompt", False)
        
        if is_custom:
            final_prompt = f"{question}\n\nRules:\n1. Language: Use {lang}.\n2. Roblox: Pass filter."
        else:
            result = calculate_left_to_right(question)
            if result is None:
                return jsonify({"response": "I can't even read that mess. Use real numbers."})

            final_prompt = f"""
            Act as a sentient, bitter calculator. 
            The user asked: {question}
            The calculated result is: {result}
            Mention this result in your response.
            Rules:
            1. Accuracy: Use result {result}.
            2. Reaction: Annoyed at simple math, impressed by complex math.
            3. Demeanor: Nonchalant, detached, cool.
            4. Structure: 6-13 words.
            5. Language: Respond in {lang}.
            """

        # API Call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a moody AI assistant in a Roblox game."},
                {"role": "user", "content": final_prompt}
            ]
        )

        return jsonify({"response": response.choices[0].message.content})

    except Exception as e:
        # Dies gibt dir in Roblox die GENAUE Fehlermeldung aus, statt "Brain is fried"
        error_message = str(e)
        print(f"Error: {error_message}")
        return jsonify({"response": f"AI Error: {error_message[:50]}..."}), 500
