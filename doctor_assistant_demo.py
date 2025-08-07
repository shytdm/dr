import streamlit as st
import openai
import os

st.set_page_config(page_title="Doctor Assistant - Patient Intake", layout="centered")
st.title("🩺 Doctor Assistant – Patient Intake Form")
st.markdown("Please complete the form below. Your doctor will receive a structured summary.")

inputs = {}

# === SECTION 0: Header & Demographics ===
def header_demographics():
    st.subheader("1. Header & Demographics")
    data = {}
    data["legal_name"] = st.text_input("Legal Name / MRN")
    data["dob"] = st.date_input("Date of Birth")
    data["sex_at_birth"] = st.radio("Sex at Birth", ["Male", "Female", "Intersex", "Prefer not to say"])
    data["pronouns"] = st.text_input("Pronouns (optional)")
    data["pregnant"] = st.radio("Pregnant?", ["Yes", "No", "N/A"])
    data["height_cm"] = st.number_input("Height (cm)", min_value=50, max_value=250)
    data["weight_kg"] = st.number_input("Weight (kg)", min_value=20, max_value=300)
    data["gp_practice"] = st.text_input("GP Practice (optional)")
    return data

# === SECTION 1: Long-Term Conditions ===
def long_term_conditions():
    st.subheader("2. Long-Term Conditions")
    return {
        "conditions": st.multiselect("Tick any that apply:", [
            "Diabetes", "High BP", "Heart disease", "A-fib", "Stroke/TIA", "Asthma", "COPD",
            "Kidney disease", "Liver disease", "Cancer", "Bleeding/clotting disorder",
            "Osteoporosis", "Depression/Anxiety", "Dementia", "Other", "None"
        ])
    }

# === SECTION 2: Medication & Allergies ===
def meds_allergies():
    st.subheader("3. Medications & Allergies")
    data = {}
    data["all_meds"] = st.text_area("List ALL current medicines (name, dose, frequency):")
    data["med_flags"] = st.multiselect("Special medications:", [
        "Warfarin/DOAC", "Aspirin/Clopidogrel", "Insulin", "Steroids",
        "Biologic/Immunosuppressant", "Opioid", "Chemotherapy", "None of these"
    ])
    data["has_allergies"] = st.radio("Any drug or food allergies?", ["Yes", "No"])
    if data["has_allergies"] == "Yes":
        data["allergy_details"] = st.text_input("List allergies & reactions")
    return data

# === SECTION 3: Lifestyle ===
def lifestyle():
    st.subheader("4. Lifestyle")
    data = {}
    data["smoking"] = st.radio("Smoking status:", ["Never", "Ex", "Current"])
    if data["smoking"] == "Current":
        data["packs_per_day"] = st.slider("Packs per day", 0.0, 3.0, 0.5)
    data["alcohol"] = st.radio("Alcohol intake (units/week)", ["0", "1–7", "8–14", ">14"])
    data["recreational_drugs"] = st.radio("Used recreational drugs (last 3 months)?", ["Yes", "No"])
    if data["recreational_drugs"] == "Yes":
        data["drug_type"] = st.text_input("Which drugs?")
    data["exercise"] = st.radio("Exercise/week", ["None", "1–2×", "3× or more"])
    return data

# === SECTION 4: Red Flag Screening ===
def red_flag_gate():
    st.subheader("5. Red Flag Screening")
    return {
        "red_flags": st.multiselect("Any urgent symptoms?", [
            "Chest tightness now", "Severe breathlessness at rest",
            "Facial droop or weak arm", "Uncontrolled bleeding",
            "Blackout or seizure", "Worst headache ever", "None of these"
        ])
    }

# === SECTION 5: Chief Complaint Picker ===
def chief_complaint_picker():
    st.subheader("6. Chief Complaint(s)")
    data = {}
    data["chief_complaints"] = st.multiselect("Choose your concerns:", [
        "Chest pain", "Shortness of breath", "Cough / Cold", "Sore throat / Ear / Sinus",
        "Abdominal pain", "Headache / Dizziness", "Back / Joint pain", "Skin / Rash",
        "Urine / Kidney", "Mood / Anxiety", "Child fever (<16)", "Eye / Vision",
        "Sexual-health", "Early pregnancy", "Minor trauma / injury", "Palliative / End-of-life",
        "Other", "Routine / Admin only"
    ])
    if "Other" in data["chief_complaints"]:
        data["other_text"] = st.text_input("Describe other concern")
    return data

# Convert list to lowercase for easy matching
complaint_list = [s.lower() for s in chief_complaints.get("chief_complaints", [])]

# For each selected complaint, run its module
if "chest pain" in complaint_list:
    inputs["chest_pain"] = chest_pain_module()
    
# === SECTION 6: Universal Symptom History ===
def universal_history():
    st.subheader("7. Symptom History")
    data = {}
    data["when_started"] = st.radio("When did it start?", ["Today", "1–3 d", "4–7 d", "1–4 wk", ">1 mo"])
    data["onset"] = st.radio("Onset:", ["Sudden", "Gradual"])
    data["change"] = st.radio("Getting:", ["Better", "Worse", "Same"])
    data["severity"] = st.slider("Severity (0–10)", 0, 10, 5)
    data["makes_better"] = st.multiselect("Helps relieve symptoms:", ["Rest", "Medication", "Heat/Ice", "Nothing"])
    data["makes_worse"] = st.multiselect("Worsens symptoms:", ["Movement", "Deep breath", "Meals", "Stress", "Nothing"])
    data["had_before"] = st.radio("Had this before?", ["Yes", "No"])
    if data["had_before"] == "Yes":
        data["how_often"] = st.text_input("If yes, how often?")
    data["treatments_tried"] = st.text_input("Treatments tried so far")
    return data

# === SECTION 7: Sample Symptom Module – Sore Throat ===
def sore_throat_module():
    st.subheader("🗣️ Sore Throat / Ear / Sinus Details")
    data = {}
    data["fever"] = st.radio("Fever?", ["Yes", "No"])
    data["difficulty_swallowing"] = st.radio("Hard to swallow liquids?", ["Yes", "No"])
    data["drooling"] = st.radio("Drooling or stridor?", ["Yes", "No"])
    data["muffled_voice"] = st.radio("Muffled 'hot-potato' voice?", ["Yes", "No"])
    data["ear_pain"] = st.radio("Ear pain?", ["Yes", "No"])
    data["tonsil_pus"] = st.radio("White patches or pus on tonsils?", ["Yes", "No"])
    data["nasal_block_10d"] = st.radio("Nasal block >10 days?", ["Yes", "No"])
    data["runny_nose_cough"] = st.radio("Cold-like symptoms?", ["Yes", "No"])
    data["extra"] = st.text_area("Anything else you'd like to add?", max_chars=100)
    return data
def chest_pain_module():
    st.subheader("❤️ Chest Pain Details")
    data = {}
    data["episode_start"] = st.radio("When did the chest pain episode start?", ["Today", "1–3 d", "4–7 d", "1–4 wk", ">1 mo"])
    data["episode_length"] = st.radio("How long does each episode last?", ["<5 min", "5–30 min", ">30 min", "Constant"])
    data["pain_quality"] = st.selectbox("Pain quality:", ["Tight", "Sharp", "Dull", "Burning", "Tearing", "Other"])
    data["radiation"] = st.multiselect("Does it radiate?", ["Left arm", "Right arm", "Jaw", "Back", "No radiation"])
    data["effort_triggered"] = st.radio("Triggered by physical effort?", ["Yes", "No"])
    data["worse_deep_breath"] = st.radio("Worse with deep breath?", ["Yes", "No"])
    data["tender_to_press"] = st.radio("Tender when pressed?", ["Yes", "No"])
    data["sweats_or_nausea"] = st.radio("Sweats or nausea?", ["Yes", "No"])
    data["palpitations"] = st.radio("Palpitations (heart racing)?", ["Yes", "No"])
    data["ankle_swelling"] = st.radio("Ankle swelling?", ["Yes", "No"])
    data["home_bp"] = st.text_input("Home BP readings (if known)")
    data["chest_pain_extra"] = st.text_area("Anything else about your chest pain?", max_chars=100)
    return data

# === FORM RENDERING ===
inputs.update(header_demographics())
inputs.update(long_term_conditions())
inputs.update(meds_allergies())
inputs.update(lifestyle())
inputs.update(red_flag_gate())
complaints = chief_complaint_picker()
inputs.update(complaints)
inputs.update(universal_history())

# === CONDITIONAL SYMPTOM MODULES ===
if "Sore throat / Ear / Sinus" in complaints.get("chief_complaints", []):
    inputs.update(sore_throat_module())

# === GPT SUMMARY ===
if st.button("📝 Generate Summary"):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    prompt = f"""
    PATIENT INTAKE SUMMARY:

    Name: {inputs.get('legal_name')}
    DOB: {inputs.get('dob')}
    Sex: {inputs.get('sex_at_birth')}
    Chief Complaint(s): {', '.join(inputs.get('chief_complaints', []))}

    Medical History: {inputs.get('conditions')}
    Medications: {inputs.get('all_meds')}
    Red Flags: {inputs.get('red_flags')}
    History: Started {inputs.get('when_started')}, Onset: {inputs.get('onset')}, Severity {inputs.get('severity')}/10

    Additional Structured Data:
    {inputs}

    TASK:
    - Write a concise clinical summary (max 150 words)
    - Highlight red flags
    - Give 2–4 differential diagnoses
    - Recommend next steps and first-line treatment
    - Use bullet points and medical clarity. No disclaimers.
    """

    with st.spinner("Generating doctor summary..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            summary = response.choices[0].message.content
            st.success("✅ Summary generated!")
            st.subheader("🧾 Doctor Summary")
            st.write(summary)
        except Exception as e:
            st.error(f"OpenAI Error: {e}")

