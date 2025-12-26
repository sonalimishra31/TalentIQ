import re
import pandas as pd
from nltk.corpus import stopwords

# -------------------------
# Load stopwords
# -------------------------
STOPWORDS = set(stopwords.words("english"))

# -------------------------
# Preprocess text
# -------------------------
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z ]", " ", text)
    words = text.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return set(words)

# -------------------------
# Extract skills from text
# -------------------------
def extract_skills(text):
    return preprocess_text(text)

# -------------------------
# ATS Score Calculation
# -------------------------
def ats_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    if len(jd_skills) == 0:
        return 0

    matched = resume_skills.intersection(jd_skills)
    score = int((len(matched) / len(jd_skills)) * 100)

    # Cap score to realistic ATS behavior
    return min(score, 95)

# -------------------------
# Skill-wise Match Table
# -------------------------
def skill_match_table(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    data = []
    for skill in sorted(jd_skills):
        data.append({
            "Skill": skill,
            "Status": "✅ Matched" if skill in resume_skills else "❌ Missing"
        })

    return pd.DataFrame(data)

# -------------------------
# Missing Skills
# -------------------------
def missing_skills(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    return sorted(list(jd_skills - resume_skills))

# -------------------------
# Strengths / Talents
# -------------------------
def strengths(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    return sorted(list(resume_skills.intersection(jd_skills)))

# -------------------------
# Resume Improvement Tips
# -------------------------
def resume_improvement_tips(resume_text, jd_text):
    missing = missing_skills(resume_text, jd_text)
    tips = []

    if len(missing) > 0:
        tips.append(
            "🔧 Add these missing skills to your resume (if applicable): "
            + ", ".join(missing[:10])
        )

    tips.extend([
        "📌 Use exact job description keywords to improve ATS ranking.",
        "📄 Add measurable achievements (e.g., 'Improved accuracy by 20%').",
        "🧠 Include tools, technologies, and certifications explicitly.",
        "🎯 Tailor your resume summary for each job role.",
        "📑 Avoid images, tables, and fancy formatting for ATS compatibility."
    ])

    return tips

# -------------------------
# Full Resume Analysis (Optional helper)
# -------------------------
def full_resume_analysis(resume_text, jd_text):
    return {
        "ats_score": ats_score(resume_text, jd_text),
        "matched_skills": strengths(resume_text, jd_text),
        "missing_skills": missing_skills(resume_text, jd_text),
        "skill_table": skill_match_table(resume_text, jd_text),
        "tips": resume_improvement_tips(resume_text, jd_text)
    }

def best_job_for_student(resume_text):
    resume_text = resume_text.lower()

    job_roles = {
        "Data Scientist": ["python", "machine learning", "data", "statistics", "pandas"],
        "AI Engineer": ["deep learning", "neural", "tensorflow", "pytorch", "ai"],
        "Data Analyst": ["excel", "sql", "power bi", "tableau", "analysis"],
        "Web Developer": ["html", "css", "javascript", "react", "frontend"],
        "Backend Developer": ["django", "flask", "api", "backend"],
        "Cloud Engineer": ["aws", "azure", "gcp", "cloud"],
        "Cybersecurity Analyst": ["security", "network", "cyber", "penetration"],
        "QA Engineer": ["testing", "selenium", "automation", "qa"]
    }

    scores = {}
    for role, skills in job_roles.items():
        scores[role] = sum(1 for skill in skills if skill in resume_text)

    best_role = max(scores, key=scores.get)
    return best_role, scores
