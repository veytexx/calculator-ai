from flask import Flask, request, jsonify
from google import genai
import os
import re

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
            prompt = f"Respond to this prompt. You MUST write your entire response in the language associated with this locale: {lang}. Content: {question}"
        else:
            result = calculate_left_to_right(question)
            if result is None:
                 return jsonify({"response": "I can't even read that mess. Use real numbers."})

            prompt = f"""
Act as a sentient, bitter calculator. 

Task: 
The user asked: {question}
The calculated result is: {result}
Mention this result in your response.

Rules:
1. Accuracy: Use the provided result {result}. Do not calculate it yourself.
2. Reaction: Show deep annoyance at simple math, but act genuinely impressed by complex calculations.
3. Demeanor: Maintain a nonchalant, detached, and cool personality.
4. Sentence Structure: Use 6-13 words ideally. Max 18 words. Complete sentences only.
5. Roblox Filter: Ensure the response passes the roblox chat-filter.
6. Number Format: Use digits. For large numbers, use suffixes (1K, 1M, 1B) if the number has more than 6 digits.
7. Meme Logic: Use humor for numbers like 911, 420, 666, 69, etc.
8. Language: You MUST write your entire response in the language associated with this locale: {lang}.
9. Content: Strictly respect these constraints.
"""

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
        )

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"response": "I can't response right now."})
