import re

JOB_ROLES = {
    "Data Scientist": ["python", "machine learning", "statistics", "sql", "nlp"],
    "ML Engineer": ["python", "deep learning", "tensorflow", "pytorch"],
    "Data Analyst": ["python", "sql", "excel", "power bi"],
    "Python Developer": ["python", "django", "flask", "api"]
}

def clean_words(text):
    return set(re.findall(r"[a-zA-Z]+", text.lower()))

# 🔹 Best Job Role
def best_job_for_student(resume_text):
    results = {}
    words = clean_words(resume_text)

    for role, skills in JOB_ROLES.items():
        matched = [s for s in skills if s in words]
        score = int((len(matched) / len(skills)) * 100)
        results[role] = {
            "score": score,
            "talent": matched,
            "lack": list(set(skills) - set(matched))
        }

    best = max(results, key=lambda r: results[r]["score"])
    return best, results

# 🔹 JD vs Resume Match
def job_description_match(resume_text, jd_text):
    r = clean_words(resume_text)
    j = clean_words(jd_text)

    matched = list(r & j)
    missing = list(j - r)

    percent = int((len(matched) / len(j)) * 100) if j else 0
    decision = "Good Match ✅" if percent >= 60 else "Not a Good Match ❌"

    return percent, matched, missing, decision

# 🔹 ATS Simulation
def ats_score(match, matched, missing):
    score = min(100, max(0, int(match * 0.6 + len(matched) * 4 - len(missing) * 3)))
    verdict = "Strong" if score > 70 else "Average" if score > 45 else "Weak"
    return score, verdict
