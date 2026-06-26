"""
app.py - AI Resume Analyzer (Streamlit UI)
--------------------------------------------
Ye file UI dikhata hai. Saari analysis logic analyzer_core.py mein hai.

Run karne ka tareeka (apne laptop/Colab pe):
    streamlit run app.py
"""

import streamlit as st
from analyzer_core import analyze

# ---------- Page settings ----------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 AI Resume Analyzer")
st.write("Apna resume upload karo (PDF ya DOCX) aur instant analysis paao — skills, score, aur improvement suggestions.")

# ---------- File upload widget ----------
uploaded_file = st.file_uploader(
    "Resume upload karo",
    type=["pdf", "docx", "txt"],
    help="PDF, DOCX, ya TXT format supported hai.",
)

# ---------- Analyze button ----------
if uploaded_file is not None:
    if st.button("🔍 Analyze Resume", type="primary"):
        with st.spinner("Resume analyze ho raha hai..."):
            result = analyze(uploaded_file, uploaded_file.name)

        if result["error"]:
            st.error(result["error"])
        else:
            # ---------- Score (sabse upar, sabse important) ----------
            score = result["score"]
            st.subheader("Resume Score")
            st.progress(score / 100)
            st.metric(label="Score out of 100", value=score)

            if score >= 80:
                st.success("Excellent resume! 🎉")
            elif score >= 60:
                st.warning("Achha hai, but improvement ki gunjaish hai.")
            else:
                st.error("Resume ko kaafi improve karne ki zaroorat hai.")

            st.divider()

            # ---------- Candidate Info ----------
            st.subheader("Candidate Info")
            col1, col2, col3 = st.columns(3)
            col1.metric("Name", result["name"])
            col2.metric("Email", result["email"] if result["email"] != "Not found" else "❌ Not found")
            col3.metric("Phone", result["phone"] if result["phone"] != "Not found" else "❌ Not found")

            st.divider()

            # ---------- Skills ----------
            st.subheader(f"Skills Detected ({len(result['skills'])})")
            if result["skills"]:
                # Skills ko nice tags jaisa dikhane ke liye
                skill_html = " ".join(
                    f"<span style='background-color:#e0f2fe; color:#0369a1; "
                    f"padding:4px 10px; border-radius:12px; margin:3px; "
                    f"display:inline-block; font-size:14px;'>{s.title()}</span>"
                    for s in result["skills"]
                )
                st.markdown(skill_html, unsafe_allow_html=True)
            else:
                st.write("Koi skill detect nahi hui.")

            st.divider()

            # ---------- Sections ----------
            st.subheader("Sections Found")
            sec_cols = st.columns(3)
            for i, (sec, present) in enumerate(result["sections"].items()):
                icon = "✅" if present else "❌"
                sec_cols[i % 3].write(f"{icon} {sec.title()}")

            st.divider()

            # ---------- Suggestions ----------
            st.subheader("Suggestions for Improvement")
            if result["suggestions"]:
                for s in result["suggestions"]:
                    st.write(f"- {s}")
            else:
                st.write("Resume bahut achha hai, koi major suggestion nahi!")

            # ---------- Footer info ----------
            st.caption(f"NLP engine used: {result['nlp_engine']} | Text length: {result['char_count']} characters")

else:
    st.info("Resume upload karne ke baad 'Analyze Resume' button dabao.")
