# utils/diet_chain.py

import os
import json
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generate"
)

def generate_plan(calories: int, prefs: list[str]) -> dict[str, dict]:
    """
    Call Gemini API to generate a 7-day meal plan.
    Returns a dict:
       {
         "Day 1": {"breakfast": "...", "breakfast_img": "...",
                   "lunch": "...",     "lunch_img": "...",
                   "dinner": "...",    "dinner_img": "..."},
         ...
       }
    """
    # Check if API key is available
    if not GEMINI_KEY:
        return generate_mock_plan(calories, prefs)
        
    prompt = (
        f"Generate a 7-day meal plan for a daily target of {calories} kcal "
        f"with these preferences: {', '.join(prefs)}. "
        "Return only JSON with keys 'Day 1'...'Day 7'; for each day, "
        "provide 'breakfast','lunch','dinner' and for each meal an "
        "'image_url' field (publicly accessible)."
    )

    try:
        headers = {"Content-Type": "application/json"}
        body = {
            "prompt": {"text": prompt},
            "temperature": 0.7,
            "candidate_count": 1,
            "max_output_tokens": 512,
        }

        resp = requests.post(f"{GEMINI_URL}?key={GEMINI_KEY}", 
                         headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        # Gemini returns choices[].generate.text
        text = data["candidates"][0]["output"]
        # Parse JSON
        plan = json.loads(text)
        return plan
    except Exception as e:
        # If API call fails, use mock data
        return generate_mock_plan(calories, prefs)

def generate_mock_plan(calories: int, prefs: list[str]) -> dict[str, dict]:
    """Generate mock meal plan data for demonstration purposes"""
    
    # Adjust descriptions based on preferences
    description_prefix = ""
    if "Vegan" in prefs:
        description_prefix = "Vegan "
    elif "Vegetarian" in prefs:
        description_prefix = "Vegetarian "
    elif "Low-Carb" in prefs or "Keto" in prefs:
        description_prefix = "Low-carb "
    elif "High-Protein" in prefs:
        description_prefix = "High-protein "
    
    # Create mock meal plan
    mock_plan = {}
    
    breakfast_options = [
        {"text": f"{description_prefix}Oatmeal with berries and nuts ({calories//5} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1517093157656-b9eccef91cb1"},
        {"text": f"{description_prefix}Avocado toast with poached eggs ({calories//5} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1525351484163-7529414344d8"},
        {"text": f"{description_prefix}Protein smoothie bowl ({calories//5} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1494597564530-871f2b93ac55"},
    ]
    
    lunch_options = [
        {"text": f"{description_prefix}Quinoa salad with roasted vegetables ({calories//3} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"},
        {"text": f"{description_prefix}Chickpea and vegetable wrap ({calories//3} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1600335895229-6e75511892c8"},
        {"text": f"{description_prefix}Mediterranean bowl with hummus ({calories//3} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6"},
    ]
    
    dinner_options = [
        {"text": f"{description_prefix}Baked salmon with asparagus ({calories//3} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1467003909585-2f8a72700288"},
        {"text": f"{description_prefix}Stir-fried vegetables with tofu ({calories//3} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1511690656952-34342bb7c2f2"},
        {"text": f"{description_prefix}Lentil soup with crusty bread ({calories//3} kcal)", 
         "image_url": "https://images.unsplash.com/photo-1476718406336-bb5a9690ee2a"},
    ]
    
    import random
    days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
    
    for day in days:
        mock_plan[day] = {
            "breakfast": random.choice(breakfast_options),
            "lunch": random.choice(lunch_options),
            "dinner": random.choice(dinner_options)
        }
    
    return mock_plan
