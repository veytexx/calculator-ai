from flask import Flask, request, jsonify
from google import genai
import os
import re
import logging

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

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
                if val == 0: return "Division by zero? Nice try."
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
        if not data:
            return jsonify({"response": "No data received."}), 400
            
        question = data.get("question", "")
        lang = data.get("lang", "en-us")
        is_custom = data.get("fullCustomPrompt", False)
        
        if is_custom:
            final_prompt = question
        else:
            result = calculate_left_to_right(question)
            if result is None:
                return jsonify({"response": "I can't even read that mess. Use real numbers."})
            
            if isinstance(result, str):
                return jsonify({"response": result})

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
8. Language: Respond in {lang}.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite-preview",
            contents=final_prompt,
        )

        if response and response.text:
            return jsonify({"response": response.text})
        else:
            return jsonify({"response": "Empty response from AI."})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": f"Server Error: {str(e)}"})
