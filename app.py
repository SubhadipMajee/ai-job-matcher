import streamlit as st
from src.resume_parser import extract_text_from_pdf
from src.job_scraper import fetch_jobs
from src.skill_extractor import extract_skills
from src.matcher import match_skills
from src.resume_optimizer import optimize_resume
from src.email_generator import generate_email

st.set_page_config(page_title="AI Job Matcher", layout="wide")
st.title("🎯 AI Job Match & Resume Optimizer")

# Step 1: Upload Resume
st.header("1. Upload Your Resume")
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

# Step 2: Job Role Input
st.header("2. Enter Job Role")
job_role = st.text_input("Job Role (e.g. Python Developer)")

if st.button("Analyze Jobs"):
    if not uploaded_file or not job_role:
        st.error("Please upload a resume and enter a job role.")
    else:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.read())
        resume_text = extract_text_from_pdf("temp_resume.pdf")
        resume_skills = extract_skills(resume_text, "resume")

        with st.spinner("Fetching jobs..."):
            jobs = fetch_jobs(job_role)

        st.success(f"Found {len(jobs)} jobs")
        st.session_state["jobs"] = jobs
        st.session_state["resume_text"] = resume_text
        st.session_state["resume_skills"] = resume_skills

if "jobs" in st.session_state:
    jobs = st.session_state["jobs"]
    resume_text = st.session_state["resume_text"]
    resume_skills = st.session_state["resume_skills"]

    for i, job in enumerate(jobs):
        job_skills = extract_skills(job["description"], "job description")
        result = match_skills(resume_skills, job_skills)

        with st.expander(f"{job['title']} @ {job['company']} — Match: {result['score']}%"):
            st.write(f"**Match Score:** {result['score']}%")
            st.write(f"**Matched Skills:** {', '.join(result['matched_skills'])}")
            st.write(f"**Missing Skills:** {', '.join(result['missing_skills'])}")
            st.write(f"**Apply:** {job['link']}")

            if st.button("Improve Resume", key=f"resume_{i}"):
                with st.spinner("Optimizing resume..."):
                    improved = optimize_resume(resume_text, result["missing_skills"])
                st.text_area("Improved Resume", improved, height=300, key=f"improved_{i}")

            if st.button("Generate Email", key=f"email_{i}"):
                with st.spinner("Generating email..."):
                    email = generate_email(resume_text, job["title"], job["company"])
                st.text_area("Application Email", email, height=300, key=f"emailout_{i}")