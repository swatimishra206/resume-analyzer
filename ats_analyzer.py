import re
from text_utils import get_words, split_bullets

# note: real ATS systems (Workday, Taleo etc) all have their own
# closed-source scoring logic, so this is just an estimate based on
# publicly known best practices - not an exact match to any real ATS

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "must", "can", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "this", "that",
    "these", "those", "it", "its", "i", "you", "he", "she", "we", "they",
    "my", "your", "his", "her", "our", "their", "not", "no", "so", "if",
    "than", "then", "there", "here", "what", "which", "who", "whom",
    "about", "into", "through", "during", "before", "after", "above",
    "below", "up", "down", "out", "off", "over", "under", "again",
    "further", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "only", "own", "same", "etc",
    "looking", "plus", "knowledge", "strong", "must", "good", "great",
    "ideal", "candidate", "role", "job", "work", "working", "year",
    "years", "team", "company", "responsibilities", "requirements",
    "preferred", "required", "ability", "skills", "experience",
}

MULTI_WORD_TERMS = [
    "machine learning", "deep learning", "data science", "data analysis",
    "artificial intelligence", "natural language processing", "computer vision",
    "project management", "team leadership", "problem solving",
    "critical thinking", "rest api", "cloud computing", "version control",
    "agile methodology", "software development", "web development",
]


def extract_keywords(text, top_n=30):
    text_lower = text.lower()
    phrases = [t for t in MULTI_WORD_TERMS if t in text_lower]

    freq = {}
    for w in get_words(text):
        if w not in STOPWORDS and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1

    top_words = [w for w, c in sorted(freq.items(), key=lambda x: -x[1])[:top_n]]
    return phrases + top_words


def keyword_density(text, top_n=15):
    words = get_words(text)
    total = len(words)
    if total == 0:
        return []

    freq = {}
    for w in words:
        if w not in STOPWORDS and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1

    top = sorted(freq.items(), key=lambda x: -x[1])[:top_n]
    return [{"word": w, "count": c, "density": round((c / total) * 100, 2)} for w, c in top]


def match_resume_to_jd(resume_text, jd_text):
    # simple keyword overlap, not semantic - so "ML" won't match
    # "Machine Learning" unless both literally appear. good enough
    # for a quick gap check though
    jd_keywords = set(extract_keywords(jd_text, top_n=40))
    resume_words = set(get_words(resume_text))
    resume_lower = resume_text.lower()

    matched, missing = [], []
    for kw in jd_keywords:
        in_resume = (kw in resume_lower) if " " in kw else (kw in resume_words)
        (matched if in_resume else missing).append(kw)

    total = len(matched) + len(missing)
    match_pct = round((len(matched) / total) * 100, 1) if total else 0.0

    return {
        "match_percentage": match_pct,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing)[:15],
    }


SPECIAL_CHAR_PATTERN = r"[★☆♦♥▶◆]"


def calculate_ats_score(text, sections_found):
    score = 0
    issues = []

    sections_present = sum(1 for v in sections_found.values() if v)
    score += min(40, sections_present * 7)
    if sections_present < 4:
        issues.append("Standard sections (Experience, Education, Skills, Summary) kam hain - ATS parsers inhi headers ko dhundte hain.")

    special_chars = re.findall(SPECIAL_CHAR_PATTERN, text)
    if not special_chars:
        score += 15
    else:
        issues.append(f"{len(special_chars)} decorative symbols mile (★, ♦, etc.) - ye ATS parsers ko confuse kar sakte hain.")

    bullets = split_bullets(text)
    if len(bullets) >= 5:
        score += 20
    elif len(bullets) >= 2:
        score += 10
        issues.append(f"Thode aur bullet points use karo (abhi sirf {len(bullets)} mile) - paragraphs ke bajaye bullets ATS-friendly hote hain.")
    else:
        issues.append("Bullet points bahut kam hain - dense paragraphs ATS parsers ke liye padhna mushkil banate hain.")

    word_count = len(get_words(text))
    if 250 <= word_count <= 900:
        score += 15
    elif word_count < 250:
        score += 5
        issues.append(f"Resume bahut short hai ({word_count} words) - ATS aur recruiters dono ke liye content kam lagega.")
    else:
        score += 8
        issues.append(f"Resume bahut lamba hai ({word_count} words) - ideally 1-2 page (≈400-700 words) rakho.")

    if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text):
        score += 10
    else:
        issues.append("Email format clearly detect nahi hua - ATS isko parse nahi kar payega.")

    return min(score, 100), issues
