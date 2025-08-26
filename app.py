import streamlit as st
import google.generativeai as genai
import os

# Configure API key
genai.configure(api_key=os.getenv("AIzaSyBF0PClmBX6Ca29cWUbcL9enGRJ0Dbv17M"))

# Choose a supported Gemini model
MODEL_NAME = "gemini-1.5-pro-latest"

def analyze_resume(resume_text, job_description):
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
    Compare the following resume with the job description. 
    Highlight strengths, weaknesses, missing skills, and give an ATS-style match score (0-100).

    Resume:
    {resume_text}

    Job Description:
    {job_description}
    """
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI
st.title("ATS Resume Checker (Gemini)")

resume_text = st.text_area("Paste Resume Text")
job_description = st.text_area("Paste Job Description")

if st.button("Analyze"):
    if resume_text and job_description:
        result = analyze_resume(resume_text, job_description)
        st.subheader("Analysis Result")
        st.write(result)
    else:
        st.warning("Please paste both resume and job description.")

