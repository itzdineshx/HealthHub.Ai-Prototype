# pages/Diet_Planner.py

import streamlit as st
import os
import sys

# Add parent directory to path to ensure module imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.diet_chain import generate_plan
from utils.theme import apply_theme

# Apply dark theme with page config
apply_theme("🥗 GenAI Diet Planner", set_page=True)

st.markdown("""
<div class="card fade-in">
    <h3>Personalized Meal Plans with AI</h3>
    <p>Adjust your calorie target and dietary preferences, then let our AI craft a full 7-day menu with delicious meal options.</p>
</div>
""", unsafe_allow_html=True)

# Create two columns for form
col1, col2 = st.columns([1, 1])

with col1:
    calories = st.slider("Daily Calorie Target (kcal)", 1200, 3500, 2000)

with col2:
    prefs = st.multiselect(
        "Dietary Preferences", 
        ["Vegan", "Vegetarian", "Low-Carb", "High-Protein", "Gluten-Free", "Keto"]
    )

# Center the button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("Generate 7-Day Plan", use_container_width=True)

if generate_button:
    with st.spinner("Generating your personalized plan…"):
        try:
            plan = generate_plan(calories, prefs)
            
            # Success message
            st.success(f"Your {', '.join(prefs) if prefs else 'balanced'} meal plan is ready!")
            
            # Display the plan with images
            for day, meals in plan.items():
                # Create day header with card styling
                st.markdown(f"""
                <div class="card" style="margin-top: 1.5rem;">
                    <h3 style="margin-top: 0;">{day}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(3)
                for i, (meal, content) in enumerate(meals.items()):
                    # content might be string or dict with text & image_url
                    if isinstance(content, dict):
                        desc = content.get("text") or content.get("description")
                        img = content.get("image_url")
                    else:
                        desc = content
                        img = None

                    # Create a styled card for each meal
                    with cols[i]:
                        st.markdown(f"""
                        <div style="padding: 1rem; background-color: var(--card-color); border-radius: 10px; height: 100%;">
                            <h4 style="text-transform: capitalize; color: var(--primary-color);">{meal}</h4>
                            <p>{desc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if img:
                            st.image(img, use_column_width=True)
        
        except Exception as e:
            st.error(f"Failed to generate meal plan: {str(e)}")
            st.info("Using mock data to demonstrate functionality. Please check your API key if you're using Gemini API.")
            
            # Display a sample plan using placeholder data
            sample_plan = {
                "Day 1": {
                    "breakfast": "Oatmeal with berries and nuts",
                    "lunch": "Quinoa salad with roasted vegetables",
                    "dinner": "Baked salmon with asparagus"
                }
            }
            
            st.markdown("""
            <div class="card">
                <h3>Sample Plan</h3>
                <p>This is an example of what your meal plan would look like.</p>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(3)
            meals = ["breakfast", "lunch", "dinner"]
            for i, meal in enumerate(meals):
                with cols[i]:
                    st.markdown(f"""
                    <div style="padding: 1rem; background-color: var(--card-color); border-radius: 10px;">
                        <h4 style="text-transform: capitalize; color: var(--primary-color);">{meal}</h4>
                        <p>{sample_plan["Day 1"][meal]}</p>
                    </div>
                    """, unsafe_allow_html=True)
else:
    # Informational section with nutrition tips
    st.markdown("""
    <div class="card fade-in" style="margin-top: 2rem;">
        <h3>Nutrition Tips</h3>
        <ul>
            <li><strong>Balanced macronutrients:</strong> Aim for a good mix of proteins, fats, and carbohydrates</li>
            <li><strong>Portion control:</strong> Even healthy foods can contribute to weight gain in large amounts</li>
            <li><strong>Hydration:</strong> Drink at least 8 glasses of water daily alongside your meal plan</li>
            <li><strong>Whole foods:</strong> Prioritize unprocessed foods for maximum nutritional value</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("""
    <div class="card fade-in" style="margin-top: 1.5rem;">
        <h3>How It Works</h3>
        <ol>
            <li>Set your daily calorie target based on your goals</li>
            <li>Select any dietary preferences or restrictions</li>
            <li>Our AI generates a complete 7-day plan customized to your needs</li>
            <li>Each meal includes a description and relevant nutritional information</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
