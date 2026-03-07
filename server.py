from flask import Flask, request, jsonify
from openai import OpenAI
import os
import re

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def calculate_left_to_right(expression):
    try:
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
    return "Calculator AI running."

@app.route("/calc", methods=["POST"])
def calc():
    try:
        data = request.json
        question = data.get("question", "")
        lang = data.get("lang", "en-us")
        is_custom = data.get("fullCustomPrompt", False)
        
        if is_custom:
            final_prompt = f"{question}\n\nRules:\n1. Language: Use {lang}. Default to English.\n2. Roblox: Pass Roblox filter."
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
4. Structure: 6-13 words. Max 18.
5. Roblox: Pass Roblox filter.
6. Format: Use digits and suffixes (1K, 1M).
7. Memes: Humor for 911, 420, 666, 69.
8. Language: Respond in {lang}. If invalid, use English.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful but moody AI assistant inside a Roblox game."},
                {"role": "user", "content": final_prompt}
            ]
        )

        return jsonify({"response": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"response": "My brain is fried. Try again later."})
