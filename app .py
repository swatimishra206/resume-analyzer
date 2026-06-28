import streamlit as st
import io
from analyzer_core import analyze
from report_generator import generate_pdf_report

st.set_page_config(page_title="Resume Desk | AI Analysis", page_icon="🖋️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background-color: #faf8f3;
}

h1, h2, h3 {
    font-family: 'Lora', serif !important;
    color: #1e293b !important;
}

.desk-header {
    background: #1e293b;
    color: #faf8f3;
    padding: 28px 32px;
    border-radius: 4px;
    margin-bottom: 24px;
    border-left: 6px solid #d97706;
}
.desk-header h1 {
    color: #faf8f3 !important;
    font-size: 28px;
    margin: 0 0 4px 0;
}
.desk-header p {
    color: #cbd5e1;
    margin: 0;
    font-size: 14px;
}

.stamp-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 6px;
    padding: 16px 18px;
    text-align: center;
    position: relative;
}
.stamp-score {
    font-family: 'Lora', serif;
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
}
.stamp-label {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}
.score-good { color: #15803d; }
.score-mid { color: #b45309; }
.score-bad { color: #b91c1c; }

.margin-note {
    border-left: 3px solid #d97706;
    background: #fffbeb;
    padding: 10px 14px;
    margin: 6px 0;
    border-radius: 0 4px 4px 0;
    font-size: 14px;
    color: #1e293b;
}
.margin-note-bad { border-left: 3px solid #b91c1c; background: #fef2f2; }
.margin-note-good { border-left: 3px solid #15803d; background: #f0fdf4; }

.skill-chip {
    display: inline-block;
    background: #eef2ff;
    color: #3730a3;
    padding: 4px 12px;
    border-radius: 14px;
    margin: 3px;
    font-size: 13px;
    font-weight: 500;
}
.skill-chip-soft { background: #fef3c7; color: #92400e; }

.section-divider {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 28px 0 16px 0;
}

.bullet-flag {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: 13.5px;
}
.bullet-ok {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: 13.5px;
}
</style>
""", unsafe_allow_html=True)


def score_class(score):
    if score >= 75:
        return "score-good"
    elif score >= 50:
        return "score-mid"
    return "score-bad"


def stamp_card(label, score, suffix="/100"):
    cls = score_class(score)
    return f"""
    <div class="stamp-card">
        <div class="stamp-score {cls}">{score}{suffix}</div>
        <div class="stamp-label">{label}</div>
    </div>
    """


st.markdown("""
<div class="desk-header">
    <h1>🖋️ Resume Desk</h1>
    <p>Deep AI-powered resume review — ATS scoring, JD matching, grammar, and editorial feedback.</p>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns([1, 1])
with col_a:
    uploaded_file = st.file_uploader("Resume upload karo", type=["pdf", "docx", "txt"])
with col_b:
    jd_text = st.text_area(
        "Job description (optional)",
        placeholder="Paste the job description here to get a match score and missing-keyword analysis...",
        height=120,
    )

analyze_clicked = st.button("🔍 Analyze Resume", type="primary", disabled=uploaded_file is None)

if analyze_clicked and uploaded_file is not None:
    with st.spinner("Resume ko line-by-line review kiya ja raha hai..."):
        result = analyze(uploaded_file, uploaded_file.name, jd_text=jd_text if jd_text.strip() else None)
    st.session_state["result"] = result

if "result" in st.session_state:
    result = st.session_state["result"]

    if result["error"]:
        st.error(result["error"])
    else:
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        score_cols = st.columns(4 if result.get("jd_match") else 3)
        with score_cols[0]:
            st.markdown(stamp_card("Overall Score", result["overall_score"]), unsafe_allow_html=True)
        with score_cols[1]:
            st.markdown(stamp_card("ATS Friendliness", result["ats_score"]), unsafe_allow_html=True)
        with score_cols[2]:
            st.markdown(stamp_card("Readability", result["readability_score"]), unsafe_allow_html=True)
        if result.get("jd_match"):
            with score_cols[3]:
                st.markdown(stamp_card("JD Match", result["jd_match"]["match_percentage"], suffix="%"), unsafe_allow_html=True)

        st.caption(f"Candidate: **{result['name']}** | {result['email']} | {result['phone']} | NLP engine: {result['nlp_engine']}")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Strengths")
            if result["strengths"]:
                for s in result["strengths"]:
                    st.markdown(f"<div class='margin-note margin-note-good'>{s}</div>", unsafe_allow_html=True)
            else:
                st.write("Koi major strength flag nahi hua.")
        with col2:
            st.subheader("🎯 Priority Improvements")
            if result["priority_improvements"]:
                for w in result["priority_improvements"]:
                    st.markdown(f"<div class='margin-note margin-note-bad'>{w}</div>", unsafe_allow_html=True)
            else:
                st.write("Koi major issue nahi mila - bahut badhiya!")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader("📋 ATS Friendliness — Detail")
        if result["ats_issues"]:
            for i in result["ats_issues"]:
                st.markdown(f"<div class='margin-note'>{i}</div>", unsafe_allow_html=True)
        else:
            st.write("Koi ATS formatting issue nahi mila.")

        if result.get("jd_match"):
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.subheader("🧩 Job Description Match")
            jd = result["jd_match"]
            st.write(f"**{jd['match_percentage']}%** of job-description keywords found in resume.")
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.write("**Matched:**")
                st.markdown(" ".join(f"<span class='skill-chip'>{k}</span>" for k in jd["matched_keywords"][:20]), unsafe_allow_html=True)
            with mcol2:
                st.write("**Missing (consider adding):**")
                st.markdown(" ".join(f"<span class='skill-chip skill-chip-soft'>{k}</span>" for k in jd["missing_keywords"]), unsafe_allow_html=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader("✍️ Grammar & Writing Quality")

        gcol1, gcol2 = st.columns(2)
        with gcol1:
            st.write(f"**Spelling errors** ({len(result['spelling_errors'])})")
            if result["spelling_errors"]:
                for e in result["spelling_errors"]:
                    st.markdown(f"<div class='bullet-flag'>'{e['wrong']}' → should be '<b>{e['correct']}</b>'</div>", unsafe_allow_html=True)
            else:
                st.write("None found.")

            st.write(f"**Passive voice bullets** ({len(result['passive_bullets'])})")
            if result["passive_bullets"]:
                for p in result["passive_bullets"]:
                    st.markdown(f"<div class='bullet-flag'>{p}</div>", unsafe_allow_html=True)
            else:
                st.write("None found — good, active voice used throughout.")

        with gcol2:
            st.write(f"**Weak / generic bullets** ({len(result['weak_bullets'])})")
            if result["weak_bullets"]:
                for w in result["weak_bullets"]:
                    st.markdown(f"<div class='bullet-flag'>{w['bullet']}<br><small>— {w['reason']}</small></div>", unsafe_allow_html=True)
            else:
                st.write("None found.")

            if result["duplicate_pairs"]:
                st.write(f"**Repetitive bullets** ({len(result['duplicate_pairs'])} pairs)")
                for a, b in result["duplicate_pairs"]:
                    st.markdown(f"<div class='bullet-flag'>\"{a}\"<br>is very similar to<br>\"{b}\"</div>", unsafe_allow_html=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader("💪 Action Verbs & Quantified Impact")
        acol1, acol2 = st.columns(2)
        with acol1:
            st.write(f"**{result['quant_percentage']}%** of bullets have quantified results (numbers/%/metrics).")
            if result["weak_verb_bullets"]:
                st.write("**Weak starting verbs — try these instead:**")
                for w in result["weak_verb_bullets"]:
                    suggestions = ", ".join(w["suggestions"])
                    st.markdown(
                        f"<div class='bullet-flag'>\"{w['bullet']}\"<br>"
                        f"<small>'{w['weak_verb']}' → try: <b>{suggestions}</b></small></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No weak starting verbs detected.")
        with acol2:
            st.write("**Bullets without measurable impact:**")
            if result["not_quantified"]:
                for nq in result["not_quantified"][:6]:
                    st.markdown(f"<div class='bullet-flag'>{nq}</div>", unsafe_allow_html=True)
            else:
                st.write("All bullets have measurable impact — excellent!")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader(f"🛠️ Technical Skills ({len(result['skills'])})")
        st.markdown(" ".join(f"<span class='skill-chip'>{s.title()}</span>" for s in result["skills"]) or "None detected", unsafe_allow_html=True)

        st.subheader(f"🤝 Soft Skills ({len(result['soft_skills'])})")
        if result["soft_skills"]:
            st.markdown(" ".join(f"<span class='skill-chip skill-chip-soft'>{s.title()}</span>" for s in result["soft_skills"]), unsafe_allow_html=True)
        else:
            st.markdown("<div class='margin-note margin-note-bad'>No soft skills detected — consider mentioning communication, leadership, teamwork, etc.</div>", unsafe_allow_html=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader("📊 Keyword Density (Top words)")
        if result["keyword_density"]:
            kd_cols = st.columns(5)
            for i, kw in enumerate(result["keyword_density"][:10]):
                with kd_cols[i % 5]:
                    st.metric(kw["word"].title(), f"{kw['count']}x", f"{kw['density']}%")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader("📑 Resume Sections")
        sec_cols = st.columns(6)
        for i, (sec, present) in enumerate(result["sections"].items()):
            with sec_cols[i % 6]:
                icon = "✅" if present else "❌"
                st.write(f"{icon} {sec.title()}")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader("📥 Download Full Report")
        pdf_buffer = io.BytesIO()
        generate_pdf_report(result, pdf_buffer)
        pdf_buffer.seek(0)
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name=f"resume_analysis_{result['name'].replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

else:
    st.info("Upload a resume aur (optionally) job description paste karo, phir 'Analyze Resume' dabao.")
