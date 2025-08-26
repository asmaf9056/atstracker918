import streamlit as st
import google.generativeai as genai
import PyPDF2

# Configure Gemini
genai.configure(api_key="AIzaSyBF0PClmBX6Ca29cWUbcL9enGRJ0Dbv17M")

# Pick a valid Gemini model
MODEL = "gemini-1.5-flash"  # you can also try "gemini-1.5-pro"

def extract_text_from_pdf(pdf_file):
    """Extract all text from a PDF file."""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def analyze_cv(cv_text, job_description):
    """Send CV and job description to Gemini for analysis."""
    prompt = f"""
    You are an AI recruitment assistant. Compare the following CV to the job description
    and provide:
    1. A match score (0–100)
    2. Key strengths
    3. Missing skills or experience
    4. A short summary recommendation

    Job Description:
    {job_description}

    CV:
    {cv_text}
    """

    response = genai.GenerativeModel(MODEL).generate_content(prompt)
    return response.text

# ---- Streamlit UI ----
st.set_page_config(page_title="CV Analyzer", layout="wide")
st.title("📄 CV Analyzer with Gemini AI")

job_description = st.text_area("Paste Job Description", height=150)

cv_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])

if st.button("Analyze CV"):
    if not job_description:
        st.warning("Please paste a job description first.")
    elif not cv_file:
        st.warning("Please upload a CV in PDF format.")
    else:
        with st.spinner("Analyzing CV..."):
            cv_text = extract_text_from_pdf(cv_file)
            result = analyze_cv(cv_text, job_description)
        st.subheader("Analysis Result")
        st.write(result)

   

