# 📄 AI Resume Analyzer

Ek AI-powered web app jo resume (PDF/DOCX/TXT) analyze karta hai aur instant feedback deta hai — skills detection, section analysis, aur resume score with improvement suggestions.

## 🔗 Live Demo

**[👉 Try it here](https://resume-analyzer-ceqmtnh6wf362yjfofdpln.streamlit.app)**

Upload karo apna resume, "Analyze Resume" dabao, aur instant result dekho — kisi installation ki zaroorat nahi.

## ✨ Features

- **Contact Info Extraction** — Name, Email, Phone automatically nikalta hai (spaCy NER model use karta hai)
- **Skill Detection** — 40+ technical skills ki database se match karta hai (Python, ML, AWS, React, etc.)
- **Section Analysis** — checks karta hai ki Summary, Experience, Education, Skills, Projects, Certifications sections present hain ya nahi
- **Resume Scoring** — 100-point scoring system based on contact info, skills count, sections, action verbs, aur quantified achievements
- **Improvement Suggestions** — personalized suggestions deta hai resume ko behtar banane ke liye

## 🛠️ Tech Stack

- **Python** — core language
- **Streamlit** — web UI framework
- **spaCy** — NLP/NER for name extraction
- **pdfplumber** — PDF text extraction
- **python-docx** — DOCX text extraction

## 📂 Project Structure

```
resume-analyzer/
├── app.py              # Streamlit UI
├── analyzer_core.py    # Core analysis logic (extraction, scoring)
└── requirements.txt    # Dependencies
```

## 🚀 Run Locally

```bash
git clone https://github.com/swatimishra206/resume-analyzer.git
cd resume-analyzer
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```

## 📊 How It Works

1. Resume upload hota hai (PDF/DOCX/TXT)
2. Text extract hota hai aur clean kiya jata hai
3. spaCy ka NER model name detect karta hai; regex patterns email/phone nikalte hain
4. Predefined skill database se text match karke skills detect hote hain
5. Standard resume sections check kiye jaate hain
6. Rule-based scoring system 100-point score generate karta hai with actionable suggestions

## 🔮 Future Improvements

- TF-IDF/embeddings based semantic skill matching (synonyms handle karne ke liye)
- Resume ko job description se compare karna (job matching feature)
- Larger, dynamic skills database
- Custom fine-tuned NER model specifically resumes ke liye
