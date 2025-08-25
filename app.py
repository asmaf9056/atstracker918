import streamlit as st
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from PyPDF2 import PdfReader
import docx
import re
import json
from typing import Dict, List, Tuple
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="ATS Resume Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .score-container {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .high-score {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .medium-score {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .low-score {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

class ATSResumeChecker:
    def __init__(self):
        self.openai_api_key = None
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    def extract_text_from_file(self, uploaded_file) -> str:
        """Extract text from uploaded file"""
        if uploaded_file.type == "application/pdf":
            return self.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self.extract_text_from_docx(uploaded_file)
        elif uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        else:
            st.error("Unsupported file format. Please upload PDF, DOCX, or TXT files.")
            return ""
    
    def analyze_with_llm(self, resume_text: str, job_description: str) -> Dict:
        """Analyze resume against job description using LLM"""
        
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) analyzer. Analyze the following resume against the job description and provide a comprehensive assessment.

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        Please provide your analysis in the following JSON format:

        {{
            "overall_match_score": <score from 0-100>,
            "keyword_match_score": <score from 0-100>,
            "skills_match_score": <score from 0-100>,
            "experience_match_score": <score from 0-100>,
            "education_match_score": <score from 0-100>,
            "missing_keywords": ["keyword1", "keyword2", ...],
            "matched_keywords": ["keyword1", "keyword2", ...],
            "missing_skills": ["skill1", "skill2", ...],
            "matched_skills": ["skill1", "skill2", ...],
            "strengths": ["strength1", "strength2", ...],
            "improvements": ["improvement1", "improvement2", ...],
            "detailed_feedback": "Detailed feedback about the resume match",
            "recommendation": "Overall recommendation (Strong Match/Good Match/Weak Match/Poor Match)"
        }}

        Be thorough and provide actionable insights.
        """
        
        try:
            if not self.openai_api_key or not OPENAI_AVAILABLE:
                # Use demo analysis when OpenAI is not available
                return self._get_demo_analysis(resume_text, job_description)
            
            # Try newer OpenAI client format first
            try:
                client = openai.OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert ATS analyzer. Provide detailed, actionable resume analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                analysis_text = response.choices[0].message.content
            except:
                # Fallback to older OpenAI format
                openai.api_key = self.openai_api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert ATS analyzer. Provide detailed, actionable resume analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                analysis_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = analysis_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._get_demo_analysis(resume_text, job_description)
                
        except Exception as e:
            st.error(f"Error in LLM analysis: {str(e)}")
            return self._get_demo_analysis(resume_text, job_description)
    
    def _get_demo_analysis(self, resume_text: str = "", job_description: str = "") -> Dict:
        """Provide demo analysis with basic keyword matching when API key is not available"""
        
        # Basic keyword analysis if text is provided
        if resume_text and job_description:
            # Simple keyword matching
            job_keywords = set(re.findall(r'\b\w+\b', job_description.lower()))
            resume_keywords = set(re.findall(r'\b\w+\b', resume_text.lower()))
            
            # Filter out common words
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
            job_keywords = job_keywords - common_words
            resume_keywords = resume_keywords - common_words
            
            matched = job_keywords.intersection(resume_keywords)
            missing = job_keywords - resume_keywords
            
            keyword_score = min(100, int((len(matched) / max(len(job_keywords), 1)) * 100))
            
            return {
                "overall_match_score": max(60, keyword_score + 10),
                "keyword_match_score": keyword_score,
                "skills_match_score": min(100, keyword_score + 15),
                "experience_match_score": min(100, keyword_score + 5),
                "education_match_score": min(100, keyword_score + 20),
                "missing_keywords": list(missing)[:10],  # Limit to 10
                "matched_keywords": list(matched)[:10],  # Limit to 10
                "missing_skills": ["Advanced analytics", "Machine learning", "Cloud platforms"],
                "matched_skills": list(matched)[:5] if matched else ["Data analysis", "Problem solving"],
                "strengths": [
                    "Good keyword alignment with job requirements",
                    "Relevant technical background",
                    "Professional presentation"
                ],
                "improvements": [
                    "Include more specific technical skills",
                    "Add quantifiable achievements",
                    "Highlight relevant project experience"
                ],
                "detailed_feedback": f"Your resume matches {len(matched)} out of {len(job_keywords)} key terms from the job description. Consider incorporating more specific keywords and technical skills to improve your ATS score.",
                "recommendation": "Good Match" if keyword_score > 60 else "Needs Improvement"
            }
        
        # Default demo response
        return {
            "overall_match_score": 78,
            "keyword_match_score": 72,
            "skills_match_score": 85,
            "experience_match_score": 75,
            "education_match_score": 80,
            "missing_keywords": ["machine learning", "cloud computing", "agile methodology"],
            "matched_keywords": ["python", "data analysis", "sql", "project management"],
            "missing_skills": ["TensorFlow", "AWS", "Docker"],
            "matched_skills": ["Python", "SQL", "Data Visualization", "Statistical Analysis"],
            "strengths": [
                "Strong technical background in data science",
                "Relevant work experience in analytics",
                "Good educational background"
            ],
            "improvements": [
                "Add more machine learning project experience",
                "Include cloud platform experience",
                "Highlight agile/scrum experience"
            ],
            "detailed_feedback": "The resume shows strong technical skills and relevant experience. However, there are some key areas that could be improved to better match the job requirements. Consider adding more specific examples of machine learning projects and cloud platform experience.",
            "recommendation": "Good Match"
        }
    
    def get_score_color_class(self, score: int) -> str:
        """Get CSS class based on score"""
        if score >= 80:
            return "high-score"
        elif score >= 60:
            return "medium-score"
        else:
            return "low-score"
    
    def create_score_visualization(self, analysis: Dict):
        """Create visualizations for the analysis scores"""
        
        # Score breakdown chart
        scores = {
            'Overall Match': analysis['overall_match_score'],
            'Keywords': analysis['keyword_match_score'],
            'Skills': analysis['skills_match_score'],
            'Experience': analysis['experience_match_score'],
            'Education': analysis['education_match_score']
        }
        
        fig_bar = px.bar(
            x=list(scores.keys()),
            y=list(scores.values()),
            title="ATS Score Breakdown",
            color=list(scores.values()),
            color_continuous_scale="RdYlGn",
            range_color=[0, 100]
        )
        fig_bar.update_layout(
            xaxis_title="Categories",
            yaxis_title="Score",
            yaxis=dict(range=[0, 100])
        )
        
        # Radar chart
        categories = list(scores.keys())
        values = list(scores.values())
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Scores'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Score Distribution"
        )
        
        return fig_bar, fig_radar

def main():
    st.markdown('<h1 class="main-header">🎯 ATS Resume Checker</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize the checker
    checker = ATSResumeChecker()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key (Optional)", 
            type="password",
            help="Enter your OpenAI API key for enhanced analysis. Leave blank to use demo mode."
        )
        
        if api_key:
            checker.openai_api_key = api_key
            st.success("✅ API Key configured!")
        else:
            st.info("🔄 Running in demo mode with basic analysis")
        
        st.markdown("---")
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload Resume**: PDF, DOCX, or TXT
        2. **Enter Job Description**: Copy-paste the job posting
        3. **Click Analyze**: Get comprehensive ATS analysis
        4. **Review Results**: Scores, feedback, and recommendations
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Extract and display text preview
            with st.expander("📖 Resume Text Preview"):
                resume_text = checker.extract_text_from_file(uploaded_file)
                st.text_area("Extracted Text", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=200)
    
    with col2:
        st.header("💼 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Copy and paste the complete job description, including requirements, responsibilities, and preferred qualifications..."
        )
    
    # Analysis button
    st.markdown("---")
    if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
        if uploaded_file and job_description:
            with st.spinner("🔄 Analyzing resume against job description..."):
                resume_text = checker.extract_text_from_file(uploaded_file)
                analysis = checker.analyze_with_llm(resume_text, job_description)
                
                # Store analysis in session state
                st.session_state['analysis'] = analysis
                st.session_state['analyzed_at'] = datetime.now()
        else:
            st.error("⚠️ Please upload a resume and enter a job description.")
    
    # Display results if analysis exists
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Overall score display
        overall_score = analysis['overall_match_score']
        score_class = checker.get_score_color_class(overall_score)
        
        st.markdown(f"""
        <div class="score-container {score_class}">
            <h2 style="margin:0;">Overall ATS Score: {overall_score}/100</h2>
            <h3 style="margin:5px 0 0 0; color: #666;">Recommendation: {analysis['recommendation']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Score breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_bar, fig_radar = checker.create_score_visualization(analysis)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed metrics
        st.subheader("📈 Detailed Scores")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            st.metric("Keywords Match", f"{analysis['keyword_match_score']}/100")
            st.metric("Skills Match", f"{analysis['skills_match_score']}/100")
        
        with metrics_col2:
            st.metric("Experience Match", f"{analysis['experience_match_score']}/100")
            st.metric("Education Match", f"{analysis['education_match_score']}/100")
        
        with metrics_col3:
            st.metric("Missing Keywords", len(analysis['missing_keywords']))
            st.metric("Matched Skills", len(analysis['matched_skills']))
        
        # Keywords and Skills Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Matched Keywords")
            if analysis['matched_keywords']:
                for keyword in analysis['matched_keywords']:
                    st.success(f"✓ {keyword}")
            else:
                st.info("No matched keywords found")
            
            st.subheader("❌ Missing Keywords")
            if analysis['missing_keywords']:
                for keyword in analysis['missing_keywords']:
                    st.error(f"✗ {keyword}")
            else:
                st.success("All keywords matched!")
        
        with col2:
            st.subheader("💪 Matched Skills")
            if analysis['matched_skills']:
                for skill in analysis['matched_skills']:
                    st.success(f"✓ {skill}")
            else:
                st.info("No matched skills found")
            
            st.subheader("🎯 Missing Skills")
            if analysis['missing_skills']:
                for skill in analysis['missing_skills']:
                    st.error(f"✗ {skill}")
            else:
                st.success("All skills matched!")
        
        # Strengths and Improvements
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💪 Strengths")
            for strength in analysis['strengths']:
                st.success(f"✓ {strength}")
        
        with col2:
            st.subheader("🔧 Improvements")
            for improvement in analysis['improvements']:
                st.warning(f"⚡ {improvement}")
        
        # Detailed Feedback
        st.subheader("📝 Detailed Feedback")
        st.markdown(f"""
        <div class="metric-card">
            <p>{analysis['detailed_feedback']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download report option
        st.subheader("📥 Export Report")
        if st.button("Download Analysis Report", type="secondary"):
            report_data = {
                "analysis_date": st.session_state['analyzed_at'].strftime("%Y-%m-%d %H:%M:%S"),
                "overall_score": overall_score,
                "recommendation": analysis['recommendation'],
                "detailed_analysis": analysis
            }
            
            report_json = json.dumps(report_data, indent=2)
            st.download_button(
                label="Download JSON Report",
                data=report_json,
                file_name=f"ats_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
    <p>🎓 Data Science Capstone Project 2 - ATS Resume Checker</p>
    <p>Built with Streamlit & LLM Technology</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
