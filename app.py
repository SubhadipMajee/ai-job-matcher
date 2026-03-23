from html import escape

import streamlit as st
from src.resume_parser import extract_text_from_pdf
from src.job_scraper import fetch_jobs
from src.skill_extractor import extract_skills, ats_score
from src.matcher import match_skills
from src.resume_optimizer import optimize_resume
from src.email_generator import generate_email

st.set_page_config(
    page_title="AI Job Match & Resume Optimizer",
    layout="wide",
    page_icon="AI",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    :root {
        --bg: #f4efe6;
        --surface: rgba(255, 255, 255, 0.82);
        --surface-strong: rgba(255, 255, 255, 0.94);
        --ink: #1b1f18;
        --muted: #5e6557;
        --line: rgba(40, 56, 32, 0.10);
        --accent: #1f6f5f;
        --accent-2: #d86f45;
        --accent-soft: rgba(31, 111, 95, 0.12);
        --warm-soft: rgba(216, 111, 69, 0.14);
        --shadow: 0 24px 80px rgba(58, 43, 26, 0.10);
        --radius-xl: 28px;
        --radius-lg: 22px;
        --radius-md: 16px;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(216, 111, 69, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(31, 111, 95, 0.18), transparent 32%),
            linear-gradient(180deg, #f8f3eb 0%, var(--bg) 46%, #efe7d8 100%);
        color: var(--ink);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    [data-testid="stSidebar"] {
        background: rgba(27, 31, 24, 0.94);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #f7f3eb;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.65);
        border: 1.5px dashed rgba(31, 111, 95, 0.35);
        border-radius: 18px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, rgba(27, 31, 24, 0.96), rgba(31, 111, 95, 0.90));
        color: #f8f3eb;
        border-radius: var(--radius-xl);
        padding: 2.4rem 2.6rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(255, 255, 255, 0.10);
        margin-bottom: 1.2rem;
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: auto -10% -38% auto;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(216, 111, 69, 0.55), transparent 68%);
    }

    .hero-kicker {
        display: inline-block;
        font-size: 0.82rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #cdd9cf;
        margin-bottom: 0.85rem;
    }

    .hero h1 {
        font-size: clamp(2rem, 4vw, 3.5rem);
        line-height: 1.02;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.03em;
    }

    .hero p {
        margin: 1rem 0 0;
        max-width: 700px;
        color: rgba(248, 243, 235, 0.82);
        font-size: 1.02rem;
        line-height: 1.6;
    }

    .glass-card {
        background: var(--surface);
        backdrop-filter: blur(12px);
        border-radius: var(--radius-lg);
        padding: 1.35rem;
        border: 1px solid var(--line);
        box-shadow: 0 18px 40px rgba(67, 52, 34, 0.07);
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--ink);
        margin: 0 0 0.35rem;
    }

    .section-copy {
        color: var(--muted);
        margin: 0;
        line-height: 1.55;
    }

    .metric-card {
        background: var(--surface-strong);
        border-radius: var(--radius-md);
        border: 1px solid var(--line);
        padding: 1rem 1.1rem;
        box-shadow: 0 14px 32px rgba(60, 46, 29, 0.06);
    }

    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted);
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: var(--ink);
    }

    .metric-sub {
        color: var(--muted);
        font-size: 0.95rem;
    }

    .job-shell {
        margin-bottom: 1rem;
        border-radius: var(--radius-lg);
        background: rgba(255, 255, 255, 0.66);
        border: 1px solid rgba(40, 56, 32, 0.08);
        overflow: hidden;
        box-shadow: 0 16px 42px rgba(77, 62, 44, 0.08);
    }

    .job-head {
        padding: 1.2rem 1.25rem 0.4rem;
    }

    .job-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--ink);
        margin: 0;
        letter-spacing: -0.02em;
    }

    .job-company {
        margin-top: 0.35rem;
        color: var(--muted);
        font-size: 0.98rem;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.85rem;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 0.88rem;
        font-weight: 600;
    }

    .pill.warm {
        background: var(--warm-soft);
        color: var(--accent-2);
    }

    .skill-group {
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(40, 56, 32, 0.08);
        border-radius: 16px;
        padding: 0.95rem;
        height: 100%;
    }

    .skill-group h4 {
        margin: 0 0 0.7rem;
        font-size: 0.95rem;
        color: var(--ink);
    }

    .skill-tag {
        display: inline-block;
        padding: 0.28rem 0.62rem;
        border-radius: 999px;
        margin: 0 0.45rem 0.45rem 0;
        background: rgba(31, 111, 95, 0.10);
        color: #184e43;
        font-size: 0.84rem;
        font-weight: 600;
    }

    .skill-tag.missing {
        background: rgba(216, 111, 69, 0.12);
        color: #9c4d2b;
    }

    .mini-note {
        color: var(--muted);
        font-size: 0.92rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 999px;
        border: none;
        padding: 0.72rem 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1f6f5f, #184e43);
        color: white;
        box-shadow: 0 14px 28px rgba(31, 111, 95, 0.22);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #195c4f, #123d35);
        color: white;
    }

    .stTextInput > div > div > input,
    .stTextArea textarea {
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(40, 56, 32, 0.12);
        color: var(--ink);
        caret-color: var(--ink);
    }

    .stTextInput > label,
    .stFileUploader > label,
    .stTextArea > label {
        color: var(--ink) !important;
        font-weight: 600;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: rgba(27, 31, 24, 0.42) !important;
        opacity: 1;
    }

    [data-testid="stFileUploaderDropzone"] * {
        color: var(--ink) !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzone"] svg {
        color: var(--muted) !important;
        fill: var(--muted) !important;
    }

    .stFileUploader [data-testid="stBaseButton-secondary"] {
        background: linear-gradient(135deg, #1f6f5f, #184e43) !important;
        color: #f8f3eb !important;
        border: none !important;
        border-radius: 14px !important;
        box-shadow: 0 12px 24px rgba(31, 111, 95, 0.18);
    }

    .stFileUploader [data-testid="stBaseButton-secondary"]:hover {
        background: linear-gradient(135deg, #195c4f, #123d35) !important;
        color: #f8f3eb !important;
    }

    .stFileUploader [data-testid="stBaseButton-secondary"] * {
        color: #f8f3eb !important;
    }

    .stExpander {
        border: none !important;
        background: transparent !important;
    }

    .stAlert {
        border-radius: 16px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_tags(items, empty_message, missing=False):
    if not items:
        return f"<span class='mini-note'>{escape(empty_message)}</span>"

    tag_class = "skill-tag missing" if missing else "skill-tag"
    return "".join(f"<span class='{tag_class}'>{escape(str(item))}</span>" for item in items)


st.sidebar.markdown("## Control Room")
st.sidebar.write("Upload your resume, set a target role, and review the strongest job matches with ATS guidance.")
st.sidebar.markdown("### Workflow")
st.sidebar.markdown("1. Upload a PDF resume")
st.sidebar.markdown("2. Enter the role you want")
st.sidebar.markdown("3. Analyze job matches")
st.sidebar.markdown("4. Refine your resume and outreach")

st.markdown(
    """
    <section class="hero">
        <div class="hero-kicker">Career Intelligence Studio</div>
        <h1>AI Job Match & Resume Optimizer</h1>
        <p>
            Turn one resume into a sharper application workflow. Compare your profile against live job listings,
            spot the missing skills fast, improve resume language, and draft tailored outreach from one screen.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

intro_col, action_col = st.columns([1.05, 1.4], gap="large")

with intro_col:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">How this helps</div>
            <p class="section-copy">
                The app extracts your resume skills, scans matching openings, and highlights the gaps that matter.
                Once results load, you can generate a stronger resume draft, ATS analysis, and an application email per role.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with action_col:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Start a search</div>
            <p class="section-copy">Use a specific role title for better matches, such as Data Analyst, Backend Engineer, or Product Designer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Resume PDF", type="pdf", help="Upload a PDF resume to analyze skills and ATS compatibility.")
    job_role = st.text_input("Target job role", placeholder="e.g. Python Developer")
    analyze = st.button("Analyze Jobs", use_container_width=True)

if analyze:
    if not uploaded_file or not job_role:
        st.error("Upload a resume and enter a job role before starting the analysis.")
    else:
        with open("temp_resume.pdf", "wb") as file_obj:
            file_obj.write(uploaded_file.read())

        with st.spinner("Reading your resume..."):
            resume_text = extract_text_from_pdf("temp_resume.pdf")
            resume_skills = extract_skills(resume_text, "resume")

        with st.spinner("Finding matching jobs..."):
            jobs = fetch_jobs(job_role)

        analyzed_jobs = []
        with st.spinner("Scoring job matches..."):
            for job in jobs:
                description = job.get("description") or ""
                job_skills = extract_skills(description, "job description") if description else []
                result = match_skills(resume_skills, job_skills)
                enriched_job = dict(job)
                enriched_job["job_skills"] = job_skills
                enriched_job["match"] = result
                analyzed_jobs.append(enriched_job)

        st.session_state["jobs"] = analyzed_jobs
        st.session_state["resume_text"] = resume_text
        st.session_state["resume_skills"] = resume_skills
        st.session_state["job_role"] = job_role
        st.success(f"Analysis complete. Found {len(analyzed_jobs)} jobs for {job_role}.")

jobs = st.session_state.get("jobs")
resume_text = st.session_state.get("resume_text")
resume_skills = st.session_state.get("resume_skills", [])
saved_role = st.session_state.get("job_role", job_role)

if jobs is not None:
    metrics = st.columns(3)
    metrics[0].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Target Role</div>
            <div class="metric-value">{saved_role or 'N/A'}</div>
            <div class="metric-sub">Current search focus</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metrics[1].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Jobs Found</div>
            <div class="metric-value">{len(jobs)}</div>
            <div class="metric-sub">Listings pulled into this session</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metrics[2].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Resume Skills</div>
            <div class="metric-value">{len(resume_skills)}</div>
            <div class="metric-sub">Extracted from your uploaded PDF</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Match results</div>
            <p class="section-copy">Open any role to inspect matched skills, missing skills, ATS detail, and AI-generated application assets.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    if not jobs:
        st.warning("No jobs were returned for that role. Try a broader title or verify the job search API setup.")

    for index, job in enumerate(jobs):
        description = job.get("description") or ""
        title = job.get("title") or "Untitled role"
        company = job.get("company") or "Unknown company"
        apply_link = job.get("link") or "Not available"
        result = job.get("match", {})
        matched_skills = result.get("matched_skills", [])
        missing_skills = result.get("missing_skills", [])
        score = result.get("score", 0)
        safe_title = escape(title)
        safe_company = escape(company)

        st.markdown("<div class='job-shell'>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="job-head">
                <div class="job-title">{safe_title}</div>
                <div class="job-company">{safe_company}</div>
                <div class="badge-row">
                    <span class="pill">Match Score: {score}%</span>
                    <span class="pill warm">Missing Skills: {len(missing_skills)}</span>
                    <span class="pill">Matched Skills: {len(matched_skills)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"Review role details for {title}"):
            detail_cols = st.columns(2, gap="large")
            with detail_cols[0]:
                st.markdown(
                    f"""
                    <div class="skill-group">
                        <h4>Matched skills</h4>
                        {render_tags(matched_skills, 'No direct skill overlap detected yet.')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with detail_cols[1]:
                st.markdown(
                    f"""
                    <div class="skill-group">
                        <h4>Missing skills</h4>
                        {render_tags(missing_skills, 'No missing skills were identified.', missing=True)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            st.caption(f"Apply link: {apply_link}")
            if apply_link != "Not available":
                st.link_button("Open job application", apply_link, use_container_width=True)

            action_cols = st.columns(3)

            with action_cols[0]:
                if st.button("Improve Resume", key=f"resume_{index}", use_container_width=True):
                    with st.spinner("Optimizing resume..."):
                        st.session_state[f"improved_{index}"] = optimize_resume(resume_text, missing_skills)

            with action_cols[1]:
                if st.button("Generate Email", key=f"email_{index}", use_container_width=True):
                    with st.spinner("Generating email..."):
                        st.session_state[f"emailout_{index}"] = generate_email(resume_text, title, company)

            with action_cols[2]:
                if st.button("ATS Score", key=f"ats_{index}", use_container_width=True):
                    with st.spinner("Analyzing ATS compatibility..."):
                        st.session_state[f"ats_{index}"] = ats_score(resume_text, description)

            improved_resume = st.session_state.get(f"improved_{index}")
            if improved_resume:
                st.text_area("Improved resume draft", improved_resume, height=280, key=f"improved_area_{index}")

            email_output = st.session_state.get(f"emailout_{index}")
            if email_output:
                st.text_area("Application email draft", email_output, height=220, key=f"email_area_{index}")

            ats_result = st.session_state.get(f"ats_{index}")
            if ats_result:
                st.markdown("### ATS analysis")
                ats_cols = st.columns(4)
                ats_cols[0].metric("ATS Score", f"{ats_result.get('ats_score', 0)}%")
                ats_cols[1].metric("Keyword Match", f"{ats_result.get('keyword_match', 0)}%")
                ats_cols[2].metric("Format Score", f"{ats_result.get('format_score', 0)}%")
                ats_cols[3].metric("Experience Match", f"{ats_result.get('experience_match', 0)}%")

                strength_col, improve_col = st.columns(2, gap="large")
                with strength_col:
                    st.success("Strengths\n\n" + "\n".join(f"- {item}" for item in ats_result.get("strengths", [])))
                with improve_col:
                    st.warning("Improvements\n\n" + "\n".join(f"- {item}" for item in ats_result.get("improvements", [])))

        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Upload a resume and run an analysis to populate the dashboard.")
