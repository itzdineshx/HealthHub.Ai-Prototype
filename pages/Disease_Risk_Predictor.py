import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import sys

# Add parent directory to path to ensure module imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.theme import apply_theme

# Apply dark theme with page config
apply_theme("🔍 Disease Risk Predictor", set_page=True)

# Function to load models
def load_model(model_name):
    """
    Attempt to load a model file with multiple extensions from multiple directories
    """
    # Define possible file extensions and directories to check
    extensions = [".pkl", ".sav"]
    directories = ["models", "saved_models"]
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Try each combination of directory and extension
    for directory in directories:
        for ext in extensions:
            model_path = os.path.join(base_dir, directory, f"{model_name}{ext}")
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as file:
                        model = pickle.load(file)
                    st.success(f"Successfully loaded {model_name} model from {model_path}")
                    return model
                except Exception as e:
                    st.warning(f"Error loading {model_path}: {str(e)}")
    
    # If we get here, no model was successfully loaded
    st.error(f"Could not find or load {model_name} model in any location")
    return None

# Load the models
heart_model = load_model("heart_disease_model")
diabetes_model = load_model("diabetes_model")

# Header
st.markdown("""
<div class="card fade-in">
    <h3>Multi-Disease Risk Assessment</h3>
    <p>Complete the form below to get personalized risk predictions for heart disease and diabetes based on your health parameters.</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for different disease predictions
tab1, tab2 = st.tabs(["Heart Disease", "Diabetes"])

# Heart Disease Prediction
with tab1:
    st.markdown("""
    <div class="card">
        <h4>Heart Disease Risk Assessment</h4>
        <p>Enter your health metrics to assess your heart disease risk. This tool uses a machine learning model trained on clinical data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for form layout
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", 18, 100, 45)
        sex = st.selectbox("Sex", ["Male", "Female"])
        sex_encoded = 1 if sex == "Male" else 0
        
        cp = st.selectbox("Chest Pain Type", 
                         ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"])
        cp_encoded = {"Typical Angina": 0, "Atypical Angina": 1, "Non-anginal Pain": 2, "Asymptomatic": 3}[cp]
        
        trestbps = st.number_input("Resting Blood Pressure (mm Hg)", 90, 200, 120)
        chol = st.number_input("Serum Cholesterol (mg/dl)", 100, 600, 200)
        
    with col2:
        fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["No", "Yes"])
        fbs_encoded = 1 if fbs == "Yes" else 0
        
        restecg = st.selectbox("Resting ECG Results", 
                              ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"])
        restecg_encoded = {"Normal": 0, "ST-T Wave Abnormality": 1, "Left Ventricular Hypertrophy": 2}[restecg]
        
        thalach = st.number_input("Maximum Heart Rate Achieved", 60, 220, 150)
        exang = st.selectbox("Exercise Induced Angina", ["No", "Yes"])
        exang_encoded = 1 if exang == "Yes" else 0
        
    # Center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        heart_predict_btn = st.button("Predict Heart Disease Risk", use_container_width=True)
    
    # Prediction
    if heart_predict_btn:
        if heart_model:
            # Create feature array
            heart_features = np.array([[age, sex_encoded, cp_encoded, trestbps, chol, 
                                      fbs_encoded, restecg_encoded, thalach, exang_encoded]])
            
            # Make prediction
            with st.spinner('Analyzing your heart disease risk...'):
                heart_prediction = heart_model.predict(heart_features)
                heart_prediction_proba = heart_model.predict_proba(heart_features)
                
                # Display results
                st.markdown("<div class='card fade-in'>", unsafe_allow_html=True)
                st.subheader("Heart Disease Risk Assessment Results")
                
                if heart_prediction[0] == 1:
                    st.markdown(f"""
                    <div style="background-color: rgba(255, 84, 84, 0.2); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="color: #ff5454;">Elevated Risk Detected</h3>
                        <p>Based on the provided health metrics, our model indicates a <b>{heart_prediction_proba[0][1]*100:.1f}%</b> probability of heart disease risk.</p>
                        <p>Please consult with a healthcare professional for a proper diagnosis and advice.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: rgba(84, 255, 118, 0.2); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="color: #54ff76;">Low Risk Detected</h3>
                        <p>Based on the provided health metrics, our model indicates a <b>{heart_prediction_proba[0][1]*100:.1f}%</b> probability of heart disease risk.</p>
                        <p>Continue maintaining a healthy lifestyle and regular check-ups.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Risk factors explanation
                st.markdown("### Key Risk Factors Analysis")
                
                # Identify top risk factors
                risk_factors = []
                
                if age > 55:
                    risk_factors.append(("Age above 55", "Higher age is associated with increased heart disease risk"))
                if sex_encoded == 1:
                    risk_factors.append(("Male gender", "Men generally have a higher risk of heart disease"))
                if cp_encoded == 3:
                    risk_factors.append(("Asymptomatic chest pain", "Can be an indicator of underlying heart problems"))
                if trestbps > 140:
                    risk_factors.append(("High blood pressure", f"Your value: {trestbps} mmHg (>140 is considered high)"))
                if chol > 240:
                    risk_factors.append(("High cholesterol", f"Your value: {chol} mg/dl (>240 is considered high)"))
                if fbs_encoded == 1:
                    risk_factors.append(("High fasting blood sugar", "Indicates possible diabetes, a heart disease risk factor"))
                if exang_encoded == 1:
                    risk_factors.append(("Exercise-induced angina", "Pain during exercise can indicate coronary artery disease"))
                
                # Display risk factors in a table
                if risk_factors:
                    risk_df = pd.DataFrame(risk_factors, columns=["Risk Factor", "Explanation"])
                    st.table(risk_df)
                else:
                    st.info("No major risk factors identified in your provided data.")
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Heart disease prediction model not available. Please check the model files.")

# Diabetes Prediction
with tab2:
    st.markdown("""
    <div class="card">
        <h4>Diabetes Risk Assessment</h4>
        <p>Enter your health metrics to assess your diabetes risk. This tool uses a machine learning model trained on clinical data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for form layout
    col1, col2 = st.columns(2)
    
    with col1:
        pregnancies = st.number_input("Number of Pregnancies", 0, 20, 0)
        glucose = st.number_input("Glucose Level (mg/dL)", 50, 300, 120)
        blood_pressure = st.number_input("Blood Pressure (mm Hg)", 40, 200, 80)
        skin_thickness = st.number_input("Skin Thickness (mm)", 0, 100, 20)
    
    with col2:
        insulin = st.number_input("Insulin Level (μU/mL)", 0, 900, 79)
        bmi = st.number_input("BMI", 10.0, 50.0, 25.0)
        diabetes_pedigree = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.5, 
                                           help="A function that scores likelihood of diabetes based on family history")
        diabetes_age = st.number_input("Age (Diabetes Assessment)", 18, 100, 45)
    
    # Center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        diabetes_predict_btn = st.button("Predict Diabetes Risk", use_container_width=True)
    
    # Prediction
    if diabetes_predict_btn:
        if diabetes_model:
            # Create feature array
            diabetes_features = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, 
                                         insulin, bmi, diabetes_pedigree, diabetes_age]])
            
            # Make prediction
            with st.spinner('Analyzing your diabetes risk...'):
                diabetes_prediction = diabetes_model.predict(diabetes_features)
                diabetes_prediction_proba = diabetes_model.predict_proba(diabetes_features)
                
                # Display results
                st.markdown("<div class='card fade-in'>", unsafe_allow_html=True)
                st.subheader("Diabetes Risk Assessment Results")
                
                if diabetes_prediction[0] == 1:
                    st.markdown(f"""
                    <div style="background-color: rgba(255, 84, 84, 0.2); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="color: #ff5454;">Elevated Risk Detected</h3>
                        <p>Based on the provided health metrics, our model indicates a <b>{diabetes_prediction_proba[0][1]*100:.1f}%</b> probability of diabetes risk.</p>
                        <p>Please consult with a healthcare professional for a proper diagnosis and advice.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: rgba(84, 255, 118, 0.2); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="color: #54ff76;">Low Risk Detected</h3>
                        <p>Based on the provided health metrics, our model indicates a <b>{diabetes_prediction_proba[0][1]*100:.1f}%</b> probability of diabetes risk.</p>
                        <p>Continue maintaining a healthy lifestyle and regular check-ups.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Risk factors explanation
                st.markdown("### Key Risk Factors Analysis")
                
                # Identify top risk factors
                risk_factors = []
                
                if glucose > 140:
                    risk_factors.append(("High glucose level", f"Your value: {glucose} mg/dL (>140 is considered high)"))
                if bmi > 30:
                    risk_factors.append(("Obesity", f"Your BMI: {bmi:.1f} (>30 is considered obese)"))
                if diabetes_pedigree > 0.8:
                    risk_factors.append(("Family history of diabetes", "Your diabetes pedigree function indicates genetic risk"))
                if blood_pressure > 140:
                    risk_factors.append(("High blood pressure", f"Your value: {blood_pressure} mmHg (>140 is considered high)"))
                if insulin > 150 and glucose > 140:
                    risk_factors.append(("Insulin resistance", "High insulin with high glucose may indicate insulin resistance"))
                
                # Display risk factors in a table
                if risk_factors:
                    risk_df = pd.DataFrame(risk_factors, columns=["Risk Factor", "Explanation"])
                    st.table(risk_df)
                else:
                    st.info("No major risk factors identified in your provided data.")
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Diabetes prediction model not available. Please check the model files.")

# Disclaimer section
st.markdown("""
<div class="card fade-in" style="margin-top: 2rem;">
    <h4>⚠️ Medical Disclaimer</h4>
    <p>This tool provides an estimate of disease risk based on a machine learning model. 
    It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always consult with a qualified healthcare provider regarding any medical questions or conditions.</p>
</div>
""", unsafe_allow_html=True)

# Interpretation guide
st.markdown("""
<div class="card fade-in">
    <h4>How to Interpret Results</h4>
    <ul>
        <li><strong>Risk Assessment:</strong> Our AI model analyzes your data against patterns found in clinical datasets</li>
        <li><strong>Probability:</strong> The percentage indicates the statistical likelihood of having the condition</li>
        <li><strong>Risk Factors:</strong> These are specific inputs that contributed most to your risk profile</li>
        <li><strong>Next Steps:</strong> Regardless of results, regular check-ups with healthcare providers are recommended</li>
    </ul>
</div>
""", unsafe_allow_html=True)
