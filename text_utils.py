import re


def split_sentences(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sentences = []
    for line in lines:
        parts = re.split(r'(?<=[.!?])\s+', line)
        for p in parts:
            p = p.strip(" -•*\t")
            if p:
                sentences.append(p)
    return sentences


def split_bullets(text):
    # bullets are usually lines starting with -, •, * etc
    bullets = []
    for line in text.split("\n"):
        stripped = line.strip()
        if re.match(r'^[-•*▪➤‣◦]\s*', stripped):
            cleaned = re.sub(r'^[-•*▪➤‣◦]\s*', '', stripped)
            if len(cleaned) > 5:
                bullets.append(cleaned)
    return bullets


def count_words(text):
    return len(re.findall(r"[a-zA-Z']+", text))


def get_words(text):
    return re.findall(r"[a-zA-Z']+", text.lower())


def count_syllables(word):
    word = re.sub(r'[^a-z]', '', word.lower())
    if not word:
        return 0

    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # silent e at the end usually doesn't add a syllable
    if word.endswith("e") and count > 1:
        count -= 1

    return max(count, 1)


def flesch_reading_ease(text):
    # standard Flesch formula, doing it manually since there's no
    # textstat lib here - 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    sentences = split_sentences(text)
    words = get_words(text)

    if not sentences or not words:
        return 0.0

    total_syllables = sum(count_syllables(w) for w in words)
    wps = len(words) / len(sentences)
    spw = total_syllables / len(words)

    score = 206.835 - (1.015 * wps) - (84.6 * spw)
    return round(max(0, min(100, score)), 1)
