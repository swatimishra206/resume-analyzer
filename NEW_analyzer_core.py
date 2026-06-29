import os
import re

from text_utils import flesch_reading_ease
from grammar_checker import (
    check_spelling, detect_passive_voice, detect_weak_bullets,
    detect_duplicate_content,
)
from ats_analyzer import calculate_ats_score, match_resume_to_jd, keyword_density
from content_analyzer import (
    detect_quantified_bullets, analyze_action_verbs, detect_soft_skills,
    generate_strengths_weaknesses, rank_priority_improvements,
)

SPACY_AVAILABLE = False
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    nlp = None
    SPACY_AVAILABLE = False


def extract_text_from_pdf(file_obj):
    import pdfplumber
    text = ""
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_obj):
    import docx
    doc = docx.Document(file_obj)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(file_obj, filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_obj)
    elif ext == ".docx":
        return extract_text_from_docx(file_obj)
    elif ext == ".txt":
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")
        return content
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def clean_text(raw_text):
    text = re.sub(r"\n{2,}", "\n", raw_text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else "Not found"


def extract_phone(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}", text)
    return match.group(0) if match else "Not found"


# words that show up at the top of resumes but aren't actually names
NON_NAME_WORDS = {
    "resume", "curriculum vitae", "cv", "details", "detail",
    "personal details", "personal information", "contact",
    "contact details", "contact information", "profile", "bio-data",
    "biodata",
}


def extract_name(text):
    if SPACY_AVAILABLE:
        doc = nlp(text[:300])
        for ent in doc.ents:
            if ent.label_ == "PERSON" and ent.text.strip().lower() not in NON_NAME_WORDS:
                return ent.text
    # fallback - just grab the first real line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    lines = [l for l in lines if l.lower() not in NON_NAME_WORDS]
    return lines[0] if lines else "Not found"


SKILL_DATABASE = [
    "python", "java", "c++", "c", "javascript", "typescript", "r", "go", "rust", "php", "kotlin", "swift",
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask", "express", "next.js",
    "machine learning", "deep learning", "data analysis", "data science", "nlp",
    "computer vision", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "matplotlib", "seaborn", "opencv",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "ci/cd", "jenkins",
    "excel", "power bi", "tableau", "rest api", "agile", "scrum",
]


def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SKILL_DATABASE:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


SECTION_HEADERS = {
    "summary": ["summary", "objective", "profile"],
    "experience": ["experience", "work experience", "employment history"],
    "education": ["education", "academic background"],
    "skills": ["skills", "technical skills", "core competencies"],
    "projects": ["projects", "personal projects"],
    "certifications": ["certifications", "certificates"],
}


def detect_sections(text):
    text_lower = text.lower()
    return {sec: any(kw in text_lower for kw in kws) for sec, kws in SECTION_HEADERS.items()}


def calculate_overall_score(skills, sections, email, phone, ats_score, quant_pct, weak_verb_count, soft_skills_count):
    score = 0
    score += 5 if email != "Not found" else 0
    score += 5 if phone != "Not found" else 0
    score += min(15, len(skills) * 1.5)

    key_sections = ["summary", "experience", "education", "skills", "projects"]
    score += sum(5 for s in key_sections if sections.get(s))  # max 25

    score += ats_score * 0.25
    score += quant_pct * 0.15
    score -= min(10, weak_verb_count * 2)
    score += min(10, soft_skills_count * 2)

    return max(0, min(100, round(score)))


def analyze(file_obj, filename, jd_text=None):
    raw_text = extract_text(file_obj, filename)
    if not raw_text.strip():
        return {"error": "Resume se koi text extract nahi hua. File scanned image ho sakti hai."}

    text = clean_text(raw_text)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    sections = detect_sections(text)

    spelling_errors = check_spelling(text)
    passive_bullets = detect_passive_voice(text)
    weak_bullets = detect_weak_bullets(text)
    duplicate_pairs = detect_duplicate_content(text)
    readability = flesch_reading_ease(text)

    ats_score, ats_issues = calculate_ats_score(text, sections)
    kw_density = keyword_density(text, top_n=10)

    jd_match_result = match_resume_to_jd(text, jd_text) if jd_text and jd_text.strip() else None

    quant_data = detect_quantified_bullets(text)
    action_verb_data = analyze_action_verbs(text)
    soft_skills = detect_soft_skills(text)

    overall_score = calculate_overall_score(
        skills, sections, email, phone, ats_score,
        quant_data["quant_percentage"],
        len(action_verb_data["weak_verb_bullets"]),
        len(soft_skills),
    )

    summary_data = {
        "quant_percentage": quant_data["quant_percentage"],
        "ats_score": ats_score,
        "weak_verb_count": len(action_verb_data["weak_verb_bullets"]),
        "total_bullets": action_verb_data["total_bullets"],
        "soft_skills_count": len(soft_skills),
        "passive_count": len(passive_bullets),
        "jd_match_percentage": jd_match_result["match_percentage"] if jd_match_result else None,
    }
    strengths, weaknesses = generate_strengths_weaknesses(summary_data)

    if spelling_errors:
        weaknesses.append(f"{len(spelling_errors)} spelling mistakes mili - inhe fix karo (e.g. '{spelling_errors[0]['wrong']}' -> '{spelling_errors[0]['correct']}').")
    if duplicate_pairs:
        weaknesses.append(f"{len(duplicate_pairs)} bullets ek dusre se bahut similar hain - content ko diversify karo.")
    if readability < 30:
        weaknesses.append(f"Readability score kam hai ({readability}/100) - sentences zyada complex hain, simplify karo.")

    priority_improvements = rank_priority_improvements(weaknesses, max_items=5)

    return {
        "error": None,
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "sections": sections,
        "nlp_engine": "spaCy" if SPACY_AVAILABLE else "regex fallback",
        "char_count": len(text),
        "overall_score": overall_score,
        "ats_score": ats_score,
        "ats_issues": ats_issues,
        "readability_score": readability,
        "spelling_errors": spelling_errors,
        "passive_bullets": passive_bullets,
        "weak_bullets": weak_bullets,
        "duplicate_pairs": duplicate_pairs,
        "quantified": quant_data["quantified"],
        "not_quantified": quant_data["not_quantified"],
        "quant_percentage": quant_data["quant_percentage"],
        "weak_verb_bullets": action_verb_data["weak_verb_bullets"],
        "strong_verb_count": action_verb_data["strong_verb_count"],
        "soft_skills": soft_skills,
        "keyword_density": kw_density,
        "jd_match": jd_match_result,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "priority_improvements": priority_improvements,
        "raw_text": text,
    }
