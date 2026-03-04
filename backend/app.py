import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq

# 🔑 API KEY FROM RENDER ENVIRONMENT
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend"),
    static_folder=os.path.join(BASE_DIR, "frontend")
)

CORS(app)

# 📖 Load Gita verses
GITA_VERSES = []
json_path = os.path.join(BACKEND_DIR, "gita_verses.json")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    if isinstance(data, list):
        GITA_VERSES = data


# 🔍 Simple keyword search (lightweight)
def search_verse(user_message):
    user_message = user_message.lower()

    for verse in GITA_VERSES:
        translation = verse.get("translation", "").lower()
        if any(word in translation for word in user_message.split()):
            return verse

    return GITA_VERSES[0]  # fallback if nothing matches


# 🟡 Krishna Mode
def generate_krishna_reply(user_message, verse_text):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are Lord Krishna speaking with wisdom, calmness, and compassion. Give practical life guidance in simple English."
            },
            {
                "role": "user",
                "content": f"""
User Question: {user_message}

Relevant Bhagavad Gita Verse:
{verse_text}

Give a clear and practical answer in 3-4 sentences.
"""
            }
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return completion.choices[0].message.content


# 🟢 Normal Mode
def generate_normal_reply(user_message):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant. Give clear, direct, short answers in simple English. Do not roleplay."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return completion.choices[0].message.content


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        mode = data.get("mode", "krishna")

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # 🟢 Normal Mode
        if mode == "normal":
            ai_reply = generate_normal_reply(user_message)
            return jsonify({"reply": ai_reply})

        # 🟡 Krishna Mode
        verse = search_verse(user_message)
        ai_reply = generate_krishna_reply(
            user_message,
            verse.get("translation", "")
        )

        return jsonify({
            "chapter": verse.get("chapter", "N/A"),
            "verse": verse.get("verse", "N/A"),
            "text": verse.get("translation", ""),
            "meaning": ai_reply
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
