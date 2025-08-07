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
symptom = st.selectbox("Main Symptom", ["Select...", "Fever", "Chest Pain", "Cough", "Headache" , "Sore Throat"])

# === SYMPTOM FOLLOW-UP LOGIC ===
inputs = {}
if symptom == "Sore Throat":
     st.subheader("A. Your Details")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    smoker = st.radio("Smoker?", ["Yes", "No"])
    illnesses = st.multiselect(
        "Any long-term illnesses:",
        ["Asthma", "Diabetes", "Heart disease", "Immune problems", "None"]
    )

    st.subheader("B. Sore-Throat Checklist")

    def sore_throat_checkbox(q_num, label):
        col1, col2, col3 = st.columns([3, 1, 3])
        with col1:
            st.markdown(f"**{q_num}. {label}**")
        with col2:
            answer = st.radio("", ["Yes", "No"], horizontal=True, key=q_num)
        with col3:
            detail = st.text_input("Detail (if yes)", key=f"{q_num}_detail") if answer == "Yes" else ""
        return {"answer": answer, "detail": detail}

    checklist = {
        "1": sore_throat_checkbox("1", "Started more than 7 days ago?"),
        "2": sore_throat_checkbox("2", "Temperature >38 °C / 100.4 °F?"),
        "3": sore_throat_checkbox("3", "Hard to swallow liquids?"),
        "4": sore_throat_checkbox("4", "Unable to swallow saliva / drooling?"),
        "5": sore_throat_checkbox("5", "Muffled or 'hot-potato' voice?"),
        "6": sore_throat_checkbox("6", "Severe one-sided pain?"),
        "7": sore_throat_checkbox("7", "Swollen or tender neck glands?"),
        "8": sore_throat_checkbox("8", "White patches / pus on tonsils?"),
        "9": sore_throat_checkbox("9", "New skin rash (e.g. sandpaper)?"),
        "10": sore_throat_checkbox("10", "Ear pain on same side?"),
        "11": sore_throat_checkbox("11", "Difficulty or noisy breathing?"),
        "12": sore_throat_checkbox("12", "Recent contact with strep throat?"),
        "13": sore_throat_checkbox("13", "Recent COVID-19 exposure or test?"),
        "14": sore_throat_checkbox("14", "Cold-like symptoms (runny nose, cough)?"),
        "15": sore_throat_checkbox("15", "Fatigue, swollen glands, belly pain (mono)?"),
        "16": sore_throat_checkbox("16", "Sexual contact involving oral sex in past month?"),
        "17": sore_throat_checkbox("17", "Up-to-date with tetanus/diphtheria vaccine?"),
        "18": sore_throat_checkbox("18", "Pregnant (if applicable)?"),
    }

    st.subheader("C. Medicines Taken for Throat Pain")
    med1 = st.text_input("Medication 1:")
    med1_helped = st.radio("Did it help?", ["Yes", "No"], key="med1")
    med2 = st.text_input("Medication 2:")
    med2_helped = st.radio("Did it help?", ["Yes", "No"], key="med2")

    st.subheader("D. Anything Else?")
    extra_notes = st.text_area("Other info you'd like the doctor to know")

    # Pack sore throat form into `inputs`
    inputs["age"] = age
    inputs["smoker"] = smoker
    inputs["illnesses"] = illnesses
    inputs["sore_throat_checklist"] = checklist
    inputs["medications"] = {
        med1: med1_helped,
        med2: med2_helped
    }
    inputs["extra_notes"] = extra_notes
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
You are a virtual physician assistant reviewing a pre-visit questionnaire for a patient.

Here are the details:

Patient Name: {name}
Doctor: {doctor}
Age: {inputs.get("age", "N/A")}
Smoker: {inputs.get("smoker", "N/A")}
Chronic Illnesses: {', '.join(inputs.get("illnesses", []))}

Chief Complaint: {symptom}

Structured Symptom Data:
{inputs}

TASK:
- Write a highly concise summary (max 150 words) for the physician
- Highlight **red flags** clearly
- Include 2–4 **differential diagnoses**
- Mention key findings that support or refute each differential
- List next **suggested diagnostic steps**
- Suggest first-line treatment options if applicable
- Bullet formatting preferred
- Write as if for a physician, not a patient

Avoid disclaimers. Focus on medical clarity and brevity.
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
