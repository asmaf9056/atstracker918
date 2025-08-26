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
st.set_page_config(page_title="ATS Tracker", layout="centered")
st.title("📄 ATS Resume & Cover Letter Analyzer (Gemini)")

st.write("Upload your CV (PDF), paste your cover letter, and provide a job description. "
         "The app will evaluate your profile using Google's Gemini AI.")

# Job description input
job_desc = st.text_area("📌 Paste Job Description", height=200)

# CV upload
cv_file = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"])

# Cover letter input
cover_letter = st.text_area("✉️ Paste Cover Letter", height=200)

# Run analysis
if st.button("🔍 Analyze Resume & Cover Letter"):
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

        if not cv_text.strip():
            st.error("❌ Could not extract text from PDF. Please upload a text-based PDF.")
        else:
            # ===============================
            # Build Gemini prompt
            # ===============================
            model = genai.GenerativeModel("models/gemini-pro")
            prompt = f"""
            You are an advanced ATS (Applicant Tracking System).
            Compare the Resume and Cover Letter against the Job Description. Provide:

            1. Overall match score (0–100).
            2. Key strengths.
            3. Weaknesses or gaps compared to the JD.
            4. Suggestions to improve the resume and cover letter.

            --- Job Description ---
            {job_desc}

            --- Resume (from PDF) ---
            {cv_text}

            --- Cover Letter ---
            {cover_letter}
            """

            with st.spinner("🤖 Analyzing with Gemini..."):
                try:
                    response = model.generate_content(prompt)
                    st.subheader("📊 ATS Analysis Result")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

