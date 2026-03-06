from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("GROQ_API_KEY")

@app.route("/calc", methods=["POST"])
def calc():
    try:
        data = request.json

        if not data:
            return jsonify({"response": "No data received."})

        question = data.get("question")
        result = data.get("result")

        if not question or not result:
            return jsonify({"response": "Missing question or result."})

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
            },
            timeout=10
        )

        data = r.json()

        print("Groq response:", data)

        if "choices" not in data:
            return jsonify({"response": "The calculator AI is currently confused."})

        ai = data["choices"][0]["message"]["content"]

        return jsonify({"response": ai})

    except Exception as e:
        print("Server error:", e)
        return jsonify({"response": "Internal calculator malfunction."})


@app.route("/", methods=["GET"])
def home():
    return "Calculator AI running."
