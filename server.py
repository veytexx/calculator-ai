from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("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")

@app.route("/calc", methods=["POST"])
def calc():
    data = request.json

    question = data["question"]
    result = data["result"]

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
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    ai = r.json()["choices"][0]["message"]["content"]

    return jsonify({"response": ai})