import re
from text_utils import split_bullets

# common typos people make in resumes, found these by checking a bunch
# of resumes manually + some research online
MISSPELLINGS = {
    "managment": "management", "recieve": "receive", "acheive": "achieve",
    "seperate": "separate", "occured": "occurred", "untill": "until",
    "experiance": "experience", "knowlege": "knowledge", "sucessful": "successful",
    "responsibile": "responsible", "comunication": "communication",
    "enviroment": "environment", "developement": "development",
    "performent": "performance", "anaylsis": "analysis", "intrest": "interest",
    "buisness": "business", "calender": "calendar", "collegue": "colleague",
    "definately": "definitely", "excelent": "excellent", "fullfill": "fulfill",
    "garantee": "guarantee", "lisence": "license", "maintainance": "maintenance",
    "neccessary": "necessary", "ocassion": "occasion", "priviledge": "privilege",
    "recomend": "recommend", "skils": "skills", "techinical": "technical",
    "proffesional": "professional", "acomplish": "accomplish",
    "achivement": "achievement", "analysist": "analyst",
}


def check_spelling(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    errors = []
    seen = set()
    for w in words:
        if w in MISSPELLINGS and w not in seen:
            errors.append({"wrong": w, "correct": MISSPELLINGS[w]})
            seen.add(w)
    return errors


PASSIVE_HELPERS = ["was", "were", "been", "being", "is", "are", "be"]


def is_passive(sentence):
    # rough check - looking for "was/were + word ending in ed/en"
    # not a real grammar parser, just catches the common resume pattern
    words = sentence.lower().split()
    for i, w in enumerate(words):
        clean = re.sub(r"[^a-z]", "", w)
        if clean in PASSIVE_HELPERS and i + 1 < len(words):
            nxt = re.sub(r"[^a-z]", "", words[i + 1])
            if len(nxt) > 3 and (nxt.endswith("ed") or nxt.endswith("en")):
                return True
    return False


def detect_passive_voice(text):
    return [b for b in split_bullets(text) if is_passive(b)]


WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "involved in",
    "duties included", "tasked with", "in charge of", "assisted with",
    "various tasks", "day to day", "general", "etc",
]


def detect_weak_bullets(text):
    weak = []
    for bullet in split_bullets(text):
        lower = bullet.lower()
        reason = None

        for phrase in WEAK_PHRASES:
            if phrase in lower:
                reason = f"generic phrase '{phrase}'"
                break

        if not reason:
            has_number = bool(re.search(r'\d', bullet))
            if not has_number and len(bullet.split()) < 8:
                reason = "no measurable detail aur bahut short hai"

        if reason:
            weak.append({"bullet": bullet, "reason": reason})

    return weak


def detect_duplicate_content(text):
    bullets = split_bullets(text)
    dupes = []
    for i in range(len(bullets)):
        for j in range(i + 1, len(bullets)):
            w1 = set(re.findall(r"[a-z]+", bullets[i].lower()))
            w2 = set(re.findall(r"[a-z]+", bullets[j].lower()))
            if not w1 or not w2:
                continue
            overlap = len(w1 & w2) / min(len(w1), len(w2))
            if overlap > 0.6 and bullets[i] != bullets[j]:
                dupes.append((bullets[i], bullets[j]))
    return dupes
