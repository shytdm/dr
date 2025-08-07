# doctor_assistant_demo.py

import streamlit as st
import openai
import os

# === PAGE SETUP ===
st.set_page_config(page_title="Doctor Assistant - Patient Intake", layout="centered")
st.title("🩺 Doctor Assistant – Patient Intake Form")

st.markdown("Please fill out the form below. Your responses will be summarized and sent to your doctor.")

# === PATIENT INFO ===
name = st.text_input("Your Full Name")
doctor = st.text_input("Doctor's Name")
symptom = st.selectbox("Main Symptom", ["Select...", "Fever", "Chest Pain", "Cough", "Headache"])

# === SYMPTOM FOLLOW-UP LOGIC ===
inputs = {}
if symptom == "Fever":
    inputs["fever_duration"] = st.text_input("How many days have you had the fever?")
    inputs["fever_temperature"] = st.text_input("What was your highest temperature?")
    inputs["has_chills"] = st.radio("Do you have chills?", ["Yes", "No"])
    inputs["has_body_aches"] = st.radio("Do you have body aches?", ["Yes", "No"])

elif symptom == "Chest Pain":
    inputs["pain_location"] = st.text_input("Where is the pain located?")
    inputs["pain_type"] = st.radio("Is it a sharp or dull pain?", ["Sharp", "Dull"])
    inputs["pain_on_exertion"] = st.radio("Does it worsen with physical activity?", ["Yes", "No"])
    inputs["breath_difficulty"] = st.radio("Are you experiencing shortness of breath?", ["Yes", "No"])

elif symptom == "Cough":
    inputs["cough_type"] = st.radio("Is your cough dry or productive?", ["Dry", "Productive"])
    inputs["cough_duration"] = st.text_input("How many days have you been coughing?")
    inputs["sputum_color"] = st.text_input("What color is your phlegm/sputum?")

elif symptom == "Headache":
    inputs["headache_duration"] = st.text_input("How long has the headache lasted?")
    inputs["headache_location"] = st.text_input("Where does it hurt?")
    inputs["sensitivity"] = st.radio("Do you have sensitivity to light or sound?", ["Yes", "No"])
    inputs["nausea"] = st.radio("Do you feel nauseated?", ["Yes", "No"])

# === SUBMISSION & SUMMARY ===
if st.button("📝 Generate Summary"):
    if not name or symptom == "Select...":
        st.warning("Please enter your name and select a main symptom.")
    else:
        openai.api_key = st.secrets["OPENAI_API_KEY"]  # Replace with your key or set as env variable

        # Prompt generation
        prompt = f"""
        Patient Name: {name}
        Doctor: {doctor}
        Chief Complaint: {symptom}
        Responses: {inputs}

        Please create a clinical summary with:
        - History of Present Illness (HPI)
        - Relevant Symptoms
        - Possible Differential Diagnoses
        - Recommended Next Steps
        """

        # Call OpenAI API
        with st.spinner("Summarizing..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                summary = response.choices[0].message.content
                st.success("Summary generated!")
                st.subheader("🧾 Doctor Summary")
                st.write(summary)
            except Exception as e:
                st.error(f"Error calling OpenAI API: {e}")
