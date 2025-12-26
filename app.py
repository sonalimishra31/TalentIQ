import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import pdfplumber
import docx
from io import StringIO
import streamlit.components.v1 as components

from resume_analyzer import (
    ats_score,
    skill_match_table,
    missing_skills,
    strengths,
    resume_improvement_tips,
    best_job_for_student
)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="TalentIQ AI – Smart Career & Hiring Platform",
    page_icon="🎓",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.main { background-color: #f8fafc; }
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.big-title { font-size: 38px; font-weight: 700; }
.subtitle { font-size: 18px; color: #555; }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================
def get_db():
    return sqlite3.connect("users.db", check_same_thread=False)

db = get_db()

db.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS history(
    user TEXT,
    role TEXT,
    jd_match INTEGER,
    time DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
db.commit()

# ================= AUTH =================
def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login_user(u, p):
    return db.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (u, hash_pwd(p))
    ).fetchone()

def signup_user(u, p):
    try:
        db.execute("INSERT INTO users VALUES (?,?)", (u, hash_pwd(p)))
        db.commit()
        return True
    except:
        return False

# ================= FILE READ =================
def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".txt"):
        return StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    elif uploaded_file.name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    elif uploaded_file.name.endswith(".docx"):
        d = docx.Document(uploaded_file)
        return "\n".join(p.text for p in d.paragraphs)
    return ""

# ================= JOB SUGGESTIONS =================
def suggest_jobs(matched_skills):
    job_map = {
        "python": "Python Developer",
        "machine": "Machine Learning Engineer",
        "learning": "AI Engineer",
        "sql": "Data Analyst",
        "data": "Data Scientist",
        "analysis": "Business Analyst",
        "java": "Java Developer",
        "html": "Web Developer",
        "css": "Front-End Developer",
        "javascript": "Full Stack Developer",
        "cloud": "Cloud Engineer",
        "aws": "AWS Engineer",
        "azure": "Cloud Architect",
        "cyber": "Cybersecurity Analyst",
        "network": "Network Engineer",
        "testing": "QA Engineer"
    }

    suggestions = set()
    for skill in matched_skills:
        for key, job in job_map.items():
            if key in skill:
                suggestions.add(job)
    return list(suggestions)

# ================= GOOGLE ANALYTICS =================
def add_google_analytics():
    GA_ID = "G-DF30V0Q0CT"   # replace if needed
    components.html(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{GA_ID}');
        </script>
        """,
        height=0,
    )

add_google_analytics()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= LOGIN / SIGNUP =================
if not st.session_state.user:
    st.image(
        "https://images.unsplash.com/photo-1522071820081-009f0129c71c",
        use_container_width=True
    )

    st.markdown('<div class="big-title">🎓 TalentIQ AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Smart Resume Analysis • Job Matching • ATS Simulation</div>',
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u2 = st.text_input("New Username")
        p2 = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if signup_user(u2, p2):
                st.success("Account created successfully 🎉")
            else:
                st.error("User already exists")

    st.stop()

# ================= SIDEBAR =================
st.sidebar.success(f"👤 {st.session_state.user}")

menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Student Dashboard", "📄 Resume & Job Analyzer", "🚪 Logout"]
)

# ================= STUDENT DASHBOARD =================
if menu == "🏠 Student Dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 Student Career Dashboard")

    df = pd.read_sql(
        "SELECT jd_match, time FROM history WHERE user=?",
        db,
        params=(st.session_state.user,)
    )

    if df.empty:
        st.info("Analyze resumes to see insights here.")
    else:
        df["time"] = pd.to_datetime(df["time"])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Analyses", len(df))
            st.line_chart(df.set_index("time")["jd_match"])

        with col2:
            avg = int(df["jd_match"].mean())
            pie_df = pd.DataFrame({
                "Status": ["Matched", "Gap"],
                "Value": [avg, 100 - avg]
            }).set_index("Status")
            st.pyplot(pie_df.plot.pie(y="Value", autopct="%1.1f%%").figure)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= ANALYZER =================
elif menu == "📄 Resume & Job Analyzer":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🤖 Resume & Job Intelligence")

    uploaded_file = st.file_uploader("Upload Resume", ["pdf", "docx", "txt"])
    job_description = st.text_area("Paste Job Description", height=220)

    if st.button("🔍 Analyze Resume"):
        if not uploaded_file or not job_description:
            st.error("Upload resume and paste job description.")
            st.stop()

        resume_text = extract_text(uploaded_file)

        # Best role
        best_role, role_data = best_job_for_student(resume_text)
        st.success(f"🎯 Best Job Role: **{best_role}**")

        # ATS
        score = ats_score(resume_text, job_description)
        st.metric("ATS Score", f"{score}%")
        st.progress(score / 100)

        # Skill table
        st.subheader("🧠 Skill Match Table")
        st.dataframe(skill_match_table(resume_text, job_description))

        # Strengths & gaps
        col1, col2 = st.columns(2)
        with col1:
            st.success("💪 Strengths")
            matched = strengths(resume_text, job_description)
            st.write(matched or "No strong matches")
        with col2:
            st.error("❌ Missing Skills")
            missing = missing_skills(resume_text, job_description)
            st.write(missing or "No major gaps")

        # Job suggestions
        st.subheader("🎯 Skill-Based Job Suggestions")
        for job in suggest_jobs(matched):
            st.info(job)

        # Tips
        st.subheader("✨ Resume Improvement Tips")
        for tip in resume_improvement_tips(resume_text, job_description):
            st.write("•", tip)

        db.execute(
            "INSERT INTO history (user, role, jd_match) VALUES (?,?,?)",
            (st.session_state.user, best_role, score)
        )
        db.commit()

    st.markdown('</div>', unsafe_allow_html=True)

# ================= LOGOUT =================
else:
    st.session_state.user = None
    st.rerun()

# ================= FOOTER =================
st.markdown("---")
st.caption("© 2025 TalentIQ AI | Built for Students 🎓 & Recruiters 👔")
