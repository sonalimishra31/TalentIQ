import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import pdfplumber
import docx
import streamlit.components.v1 as components
from resume_analyzer import (
    best_job_for_student,
    job_description_match,
    ats_score
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TalentIQ AI – Smart Career & Hiring Platform",
    page_icon="🎓",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
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
.big-title {
    font-size: 38px;
    font-weight: 700;
}
.subtitle {
    font-size: 18px;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
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

# ---------------- AUTH ----------------
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

# ---------------- FILE READ ----------------
def read_resume(file):
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            return "".join(p.extract_text() or "" for p in pdf.pages)
    if file.name.endswith(".docx"):
        d = docx.Document(file)
        return " ".join(p.text for p in d.paragraphs)
    return file.read().decode("utf-8", errors="ignore")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- LOGIN ----------------
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
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u2 = st.text_input("New Username", key="signup_user")
        p2 = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Create Account"):
            if signup_user(u2, p2):
                st.success("Account created successfully 🎉")
            else:
                st.error("User already exists")

# ---------------- SIDEBAR ----------------
st.sidebar.image(
    "https://images.unsplash.com/photo-1521737604893-d14cc237f11d",
    use_container_width=True
)
st.sidebar.success(f"👤 {st.session_state.user}")

menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Student Dashboard", "📄 Resume & Job Analyzer", "🚪 Logout"]
)

# ---------------- STUDENT DASHBOARD ----------------
if menu == "🏠 Student Dashboard":
    st.image(
        "https://images.unsplash.com/photo-1516321497487-e288fb19713f",
        use_container_width=True
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 Student Career Dashboard")

    df = pd.read_sql(
        "SELECT jd_match, time FROM history WHERE user=?",
        db,
        params=(st.session_state.user,)
    )

    if df.empty:
        st.info("Start analyzing resumes to see insights here.")
    else:
        df["time"] = pd.to_datetime(df["time"])
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Resume Analyses", len(df))
            st.line_chart(df.set_index("time")["jd_match"])

        with col2:
            avg = int(df["jd_match"].mean())
            pie_df = pd.DataFrame({
                "Status": ["Matched", "Gap"],
                "Value": [avg, 100 - avg]
            }).set_index("Status")

            st.pyplot(
                pie_df.plot.pie(
                    y="Value",
                    autopct="%1.1f%%",
                    legend=False
                ).figure
            )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ANALYZER ----------------
elif menu == "📄 Resume & Job Analyzer":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🤖 Resume & Job Intelligence")

    file = st.file_uploader("Upload Resume (PDF / DOCX / TXT)", ["pdf", "docx", "txt"])

    if file:
        resume_text = read_resume(file)
        best_role, role_data = best_job_for_student(resume_text)

        st.success(f"🎯 Best Job Role for You: **{best_role}**")

        st.subheader("💡 Talent vs Skill Gap")
        st.write("✅ **Talents:**", role_data[best_role]["talent"])
        st.write("❌ **Lacks:**", role_data[best_role]["lack"])

        jd_text = st.text_area("📌 Paste Job Description")

        if jd_text:
            match, matched, missing, decision = job_description_match(resume_text, jd_text)
            ats, verdict = ats_score(match, matched, missing)

            col1, col2, col3 = st.columns(3)
            col1.metric("JD Match %", match)
            col2.metric("ATS Score", ats)
            col3.info(decision)

            chart_df = pd.DataFrame({
                "Category": ["Matched", "Missing"],
                "Count": [len(matched), len(missing)]
            }).set_index("Category")

            st.subheader("📊 Skill Match Visualization")
            c1, c2 = st.columns(2)
            c1.pyplot(chart_df.plot.pie(y="Count", autopct="%1.1f%%").figure)
            c2.bar_chart(chart_df)

            db.execute(
                "INSERT INTO history (user, role, jd_match) VALUES (?,?,?)",
                (st.session_state.user, best_role, match)
            )
            db.commit()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOGOUT ----------------
else:
    st.session_state.user = None
    st.rerun()

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© 2025 TalentIQ AI | Designed for Students 🎓 & Recruiters 👔")


def add_google_analytics():
    GA_ID = "G-DF30V0Q0CT"  # 🔴 REPLACE with your real ID

    components.html(
        f"""
        <!-- Google tag (gtag.js) -->
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
