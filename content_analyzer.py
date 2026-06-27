import re
from text_utils import split_bullets

QUANT_PATTERN = re.compile(
    r"\d+%|\$\d+|\d+x\b|\d+\s*(percent|users|customers|clients|hours|days|months|"
    r"years|times|million|thousand|crore|lakh|requests|projects|members|people|"
    r"employees|sales|revenue|engineers|developers|designers|analysts|teams|"
    r"interns|stakeholders|countries|languages|platforms|apis|features|rs\.?\s*\d+)",
    re.IGNORECASE,
)


def detect_quantified_bullets(text):
    bullets = split_bullets(text)
    quantified = [b for b in bullets if QUANT_PATTERN.search(b)]
    not_quantified = [b for b in bullets if not QUANT_PATTERN.search(b)]
    pct = round((len(quantified) / len(bullets)) * 100, 1) if bullets else 0.0

    return {
        "quantified": quantified,
        "not_quantified": not_quantified,
        "quant_percentage": pct,
    }


# weak verb -> a few stronger options for it
WEAK_VERB_ALTERNATIVES = {
    "did": ["executed", "performed", "accomplished"],
    "made": ["built", "developed", "engineered", "created"],
    "worked": ["collaborated", "contributed", "partnered"],
    "helped": ["facilitated", "supported", "enabled"],
    "got": ["achieved", "secured", "obtained"],
    "used": ["leveraged", "utilized", "applied"],
    "handled": ["managed", "oversaw", "administered"],
    "dealt": ["resolved", "addressed", "managed"],
    "tried": ["attempted", "pursued", "initiated"],
}

STRONG_VERBS = {
    "developed", "built", "improved", "led", "designed", "implemented",
    "created", "managed", "increased", "reduced", "optimized", "automated",
    "launched", "spearheaded", "architected", "engineered", "streamlined",
    "delivered", "achieved", "executed", "transformed", "established",
    "pioneered", "accelerated", "negotiated", "mentored", "orchestrated",
}


def analyze_action_verbs(text):
    bullets = split_bullets(text)
    weak_bullets = []
    strong_count = 0

    for bullet in bullets:
        words = bullet.strip().split()
        if not words:
            continue
        first_verb = re.sub(r"[^a-z]", "", words[0].lower())

        if first_verb in WEAK_VERB_ALTERNATIVES:
            weak_bullets.append({
                "bullet": bullet,
                "weak_verb": first_verb,
                "suggestions": WEAK_VERB_ALTERNATIVES[first_verb],
            })
        elif first_verb in STRONG_VERBS:
            strong_count += 1

    return {
        "weak_verb_bullets": weak_bullets,
        "strong_verb_count": strong_count,
        "total_bullets": len(bullets),
    }


SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "collaboration",
    "problem solving", "critical thinking", "adaptability", "creativity",
    "time management", "conflict resolution", "negotiation", "mentoring",
    "decision making", "emotional intelligence", "work ethic",
    "attention to detail", "multitasking", "presentation", "public speaking",
    "stakeholder management", "cross-functional", "self-motivated",
    "analytical thinking", "interpersonal",
]


def detect_soft_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SOFT_SKILLS:
        pattern = r"(?<![a-zA-Z])" + re.escape(skill) + r"(?![a-zA-Z])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def generate_strengths_weaknesses(data):
    strengths = []
    weaknesses = []

    quant_pct = data.get("quant_percentage", 0)
    if quant_pct >= 50:
        strengths.append(f"{quant_pct}% bullets mein quantified results hain - recruiters ko ye bahut pasand aata hai.")
    elif quant_pct < 25:
        weaknesses.append(f"Sirf {quant_pct}% bullets mein numbers/metrics hain. Achievements ko measurable banao.")

    ats_score = data.get("ats_score", 0)
    if ats_score >= 75:
        strengths.append("Resume ATS-friendly hai - standard sections aur formatting sahi hai.")
    elif ats_score < 50:
        weaknesses.append("ATS score kam hai - resume parsing tools ko ye samajhne mein dikkat ho sakti hai.")

    weak_verbs = data.get("weak_verb_count", 0)
    total_bullets = data.get("total_bullets", 0)
    if total_bullets == 0:
        weaknesses.append("Koi bullet points detect nahi hue - achievements ko '-' ya '•' se start karke bullet format mein likho.")
    elif weak_verbs == 0:
        strengths.append("Koi weak starting verb nahi mila - bullets confidently likhe gaye hain.")
    elif weak_verbs >= 3:
        weaknesses.append(f"{weak_verbs} bullets weak verbs (did, made, helped) se start hote hain - stronger verbs use karo.")

    soft_count = data.get("soft_skills_count", 0)
    if soft_count >= 3:
        strengths.append("Resume mein achhi tarah soft skills mention hain (leadership, communication, etc.)")
    elif soft_count == 0:
        weaknesses.append("Koi soft skill mention nahi hai - sirf technical skills kaafi nahi hote, communication/leadership jaise skills bhi dikhao.")

    passive_count = data.get("passive_count", 0)
    if passive_count >= 2:
        weaknesses.append(f"{passive_count} bullets passive voice mein hain ('was developed by') - active voice ('I developed') zyada confident lagta hai.")

    jd_match = data.get("jd_match_percentage")
    if jd_match is not None:
        if jd_match >= 60:
            strengths.append(f"Job description ke saath {jd_match}% keywords match karte hain - achha alignment hai.")
        elif jd_match < 35:
            weaknesses.append(f"Job description ke saath sirf {jd_match}% match hai - missing keywords resume mein add karo.")

    return strengths, weaknesses


def rank_priority_improvements(weaknesses, max_items=5):
    priority_keywords = ["ats", "email", "keyword", "match"]

    def score(w):
        wl = w.lower()
        for i, kw in enumerate(priority_keywords):
            if kw in wl:
                return i
        return len(priority_keywords)

    return sorted(weaknesses, key=score)[:max_items]
