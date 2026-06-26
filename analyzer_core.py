"""
analyzer_core.py
------------------
Resume analysis ki saari core logic yahan hai - is file mein koi
print() statements nahi hain, sirf functions hain jo data RETURN karte
hain. Isse hum isi logic ko terminal script mein bhi use kar sakte hain
aur Streamlit UI mein bhi, bina code duplicate kiye.
"""

import os
import re

SPACY_AVAILABLE = False
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    nlp = None
    SPACY_AVAILABLE = False


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_obj):
    """
    PDF se text nikalta hai.
    file_obj: ya to ek file path (string) ho sakta hai, ya ek file-like
    object (jaise Streamlit ka uploaded_file) - pdfplumber dono handle kar leta hai.
    """
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
    return "\n".join(para.text for para in doc.paragraphs)


def extract_text(file_obj, filename):
    """filename ke extension ke hisaab se sahi extractor chunta hai."""
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


# ============================================================
# CONTACT INFO EXTRACTION
# ============================================================

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else "Not found"


def extract_phone(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}", text)
    return match.group(0) if match else "Not found"


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
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    lines = [l for l in lines if l.lower() not in NON_NAME_WORDS]
    if lines:
        return lines[0]
    return "Not found"


# ============================================================
# SKILL EXTRACTION
# ============================================================

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
    found_skills = []
    for skill in SKILL_DATABASE:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return sorted(set(found_skills))


# ============================================================
# SECTION DETECTION
# ============================================================

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


# ============================================================
# SCORING & SUGGESTIONS
# ============================================================

def calculate_score_and_suggestions(text, skills, sections, email, phone):
    score = 0
    suggestions = []

    if email != "Not found":
        score += 8
    else:
        suggestions.append("Email address resume mein clearly dikhao.")

    if phone != "Not found":
        score += 7
    else:
        suggestions.append("Phone number add karo taaki recruiters contact kar sakein.")

    skill_count = len(skills)
    if skill_count >= 10:
        score += 25
    elif skill_count >= 5:
        score += 15
        suggestions.append(f"Thodi aur relevant technical skills add karo (abhi sirf {skill_count} mili).")
    else:
        score += 5
        suggestions.append("Skills section bahut kam hai. Job-relevant skills clearly list karo.")

    key_sections = ["summary", "experience", "education", "skills", "projects"]
    for sec in key_sections:
        if sections.get(sec):
            score += 8
        else:
            suggestions.append(f"'{sec.title()}' section missing lag raha hai - isko add karo.")

    action_verbs = ["developed", "built", "improved", "led", "designed", "implemented",
                    "created", "managed", "increased", "reduced", "optimized", "automated"]
    text_lower = text.lower()
    verb_count = sum(1 for v in action_verbs if v in text_lower)
    if verb_count >= 4:
        score += 10
    elif verb_count >= 2:
        score += 5
        suggestions.append("Aur strong action verbs use karo (developed, improved, led, etc.).")
    else:
        suggestions.append("Bullet points mein action verbs ka use kam hai. 'Developed X', 'Improved Y by Z%' jaisa likho.")

    has_numbers = bool(re.search(r"\d+%|\d+\s*(percent|years|months)", text_lower))
    if has_numbers:
        score += 10
    else:
        suggestions.append("Achievements ko numbers/percentages se quantify karo (e.g., 'improved performance by 30%').")

    return min(score, 100), suggestions


# ============================================================
# MAIN ANALYSIS FUNCTION (UI aur script dono yahi call karenge)
# ============================================================

def analyze(file_obj, filename):
    """
    Pura analysis pipeline ek hi function mein.
    Return karta hai ek dictionary - jisse UI ya terminal script
    apne hisaab se display kar sake.
    """
    raw_text = extract_text(file_obj, filename)
    if not raw_text.strip():
        return {"error": "Resume se koi text extract nahi hua. File scanned image ho sakti hai."}

    text = clean_text(raw_text)
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    sections = detect_sections(text)
    score, suggestions = calculate_score_and_suggestions(text, skills, sections, email, phone)

    return {
        "error": None,
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "sections": sections,
        "score": score,
        "suggestions": suggestions,
        "nlp_engine": "spaCy" if SPACY_AVAILABLE else "regex fallback",
        "char_count": len(text),
    }
