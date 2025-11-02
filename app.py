import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_recipe():
    try:
        data = request.get_json()
        ingredients = data.get("ingredients")

        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        prompt = f"""
        You are a professional chef. Create a delicious recipe using the following ingredients:
        {ingredients}.
        
        Please include:
        - Recipe Name
        - Estimated Preparation Time
        - Required Ingredients (with quantities)
        - Step-by-step Cooking Instructions
        - Optional: Serving suggestions
        """

        response = model.generate_content(prompt)
        recipe = response.text.strip()

        return jsonify({"recipe": recipe})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
