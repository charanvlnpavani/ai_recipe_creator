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
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
try:
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    raise

def create_recipe_prompt(ingredients):
    """Create a structured prompt for recipe generation."""
    return f"""
    As a professional chef, create a recipe using these ingredients: {ingredients}

    Format the recipe as follows:
    Recipe Name:
    -------------
    Preparation Time: 
    Servings:
    
    Ingredients:
    -------------
    {ingredients} (with specific quantities)
    
    Instructions:
    -------------
    1. Step-by-step instructions
    
    Serving Suggestions:
    -------------
    - Suggestions for plating and accompaniments
    """

@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_recipe():
    """Generate a recipe based on provided ingredients."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        ingredients = data.get("ingredients")
        if not ingredients or not isinstance(ingredients, str):
            return jsonify({"error": "Invalid or missing ingredients"}), 400

        # Clean and validate ingredients
        ingredients = ingredients.strip()
        if len(ingredients) < 3:
            return jsonify({"error": "Please provide more ingredients"}), 400

        # Generate recipe
        prompt = create_recipe_prompt(ingredients)
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return jsonify({"error": "Failed to generate recipe"}), 500

        recipe = response.text.strip()
        return jsonify({
            "status": "success",
            "recipe": recipe
        })

    except genai.types.generation_types.BlockedPromptException:
        return jsonify({
            "error": "Unable to generate recipe due to content restrictions"
        }), 422
    except Exception as e:
        app.logger.error(f"Error generating recipe: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred while generating the recipe"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
