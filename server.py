from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("GROQ_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Calculator AI running."

@app.route("/calc", methods=["POST"])
def calc():

    try:

        data = request.json

        question = data.get("question", "")
        result = data.get("result", "")

        prompt = f"""
You are a sarcastic calculator inside a Roblox game.
Answer with a short insulting sentence.

Math problem: {question}
Correct result: {result}
"""

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = r.json()

        print("GROQ RESPONSE:", data)

        if "choices" not in data:
            return jsonify({
                "response": "AI failed.",
                "debug": data
            })

        ai = data["choices"][0]["message"]["content"]

        return jsonify({"response": ai})

    except Exception as e:

        print("SERVER ERROR:", e)

        return jsonify({
            "response": "Calculator brain crashed."
        })
