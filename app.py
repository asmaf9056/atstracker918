import streamlit as st
import google.generativeai as genai
import os
import PyPDF2

# ===============================
# Configure Gemini API
# ===============================
genai.configure(api_key=os.getenv("AIzaSyBF0PClmBX6Ca29cWUbcL9enGRJ0Dbv17M"))

# ===============================
# Streamlit UI
# ===============================
st.set_page_config(page_title="ATS Resume Checker", layout="centered")
st.title("📄 ATS Resume & Cover Letter Checker (Gemini)")

st.write("Upload your CV (PDF), add your cover letter, paste a job description, and let Gemini analyze your match.")

# Job description input
job_desc = st.text_area("Paste the Job Description", height=200)

# CV upload
cv_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

# Cover letter input
cover_letter = st.text_area("Paste your Cover Letter", height=200)

if st.button("🔍 Analyze"):
    if not job_desc:
        st.warning("⚠️ Please paste a job description.")
    elif not cv_file:
        st.warning("⚠️ Please upload your CV (PDF).")
    else:
        # ===============================
        # Extract text from PDF CV
        # ===============================
        pdf_reader = PyPDF2.PdfReader(cv_file)
        cv_text = ""
        for page in pdf_reader.pages:
            cv_text += page.extract_text() or ""

        # ===============================
        # Build Gemini prompt
        # ===============================
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""
        You are an ATS (Applicant Tracking System).
        Compare the following Resume and Cover Letter against the Job Description. 
        Provide:
        1. A match score out of 100.
        2. Key strengths of the candidate.
        3. Weaknesses or gaps compared to the JD.
        4. Suggestions to improve the resume or cover letter.

        --- Job Description ---
        {job_desc}

        --- Resume (from PDF) ---
        {cv_text}

        --- Cover Letter ---
        {cover_letter}
        """

        with st.spinner("Analyzing with Gemini..."):
            response = model.generate_content(prompt)

        # ===============================
        # Display results
        # ===============================
        st.subheader("📊 ATS Analysis")
        st.write(response.text)
