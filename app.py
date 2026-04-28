import streamlit as st
import pdfplumber
import google.generativeai as genai

st.set_page_config(page_title="AI Resume Screener", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f0f4f8; }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .score-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .score-number {
        font-size: 3rem;
        font-weight: bold;
        color: white;
    }
    .rank-gold { border-left: 5px solid #FFD700; padding-left: 1rem; }
    .rank-silver { border-left: 5px solid #C0C0C0; padding-left: 1rem; }
    .rank-bronze { border-left: 5px solid #CD7F32; padding-left: 1rem; }
    h1 { color: white !important; text-align: center; font-size: 2.5rem !important; }
    .subtitle { color: rgba(255,255,255,0.8); text-align: center; margin-bottom: 2rem; }
    .stButton>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: bold;
        width: 100%;
    }
    .stTextArea textarea { border-radius: 10px; border: 2px solid #667eea; }
</style>
""", unsafe_allow_html=True)

genai.configure(api_key="AIzaSyACc8vMveNoIV0y3euw4Zlx-g1P1a2uu64")
model = genai.GenerativeModel("models/gemini-2.5-flash")

def extract_text(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def score_cv(cv_text, job_description):
    prompt = f"""
You are an expert HR recruiter. Score this CV against the job description.

JOB DESCRIPTION:
{job_description}

CV CONTENT:
{cv_text}

Respond in exactly this format:
SCORE: [number from 0 to 100]
STRENGTHS: [2-3 key strengths]
WEAKNESSES: [2-3 key weaknesses]
VERDICT: [one sentence summary]
"""
    response = model.generate_content(prompt)
    return response.text

st.title("🎯 AI Resume Screener")
st.markdown('<p class="subtitle">Upload CVs and a job description to automatically score and rank candidates using AI</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📋 Job Description")
    job_desc = st.text_area("Paste the job description here:", height=250, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📄 Upload CVs")
    uploaded_files = st.file_uploader(
        "Upload CV files (PDF)",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} CV(s) uploaded")
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("🚀 Screen CVs Now"):
    if not job_desc:
        st.warning("⚠️ Please enter a job description!")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one CV!")
    else:
        results = []
        progress = st.progress(0)
        for i, pdf_file in enumerate(uploaded_files):
            with st.spinner(f"🔍 Analysing {pdf_file.name}..."):
                cv_text = extract_text(pdf_file)
                result = score_cv(cv_text, job_desc)
                score = 0
                for line in result.split('\n'):
                    if line.startswith('SCORE:'):
                        try:
                            score = int(line.replace('SCORE:', '').strip())
                        except:
                            score = 0
                results.append({'name': pdf_file.name, 'score': score, 'details': result})
            progress.progress((i + 1) / len(uploaded_files))

        results.sort(key=lambda x: x['score'], reverse=True)

        st.markdown("---")
        st.subheader("🏆 Candidate Rankings")

        for i, r in enumerate(results):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            rank_class = "rank-gold" if i == 0 else "rank-silver" if i == 1 else "rank-bronze"

            col_a, col_b = st.columns([3, 1])
            with col_a:
                with st.expander(f"{medal} {r['name']}"):
                    st.text(r['details'])
            with col_b:
                color = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32" if i == 2 else "#667eea"
                st.markdown(f"""
                <div style="background:{color}; border-radius:15px; padding:1rem; text-align:center; color:white;">
                    <div style="font-size:2rem; font-weight:bold;">{r['score']}</div>
                    <div>out of 100</div>
                </div>
                """, unsafe_allow_html=True)