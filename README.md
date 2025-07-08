# -SkillSync.AI-is-an-AI-powered-resume-screening-and-candidate-analysis-tool-
 SkillSync.AI — AI-Powered Resume Screening Tool
SkillSync.AI is an intelligent resume analyzer built with Streamlit, LangChain, and Groq's Llama3 model. It streamlines the recruitment process by comparing candidate resumes against job descriptions, extracting key details, and offering AI-driven insights to HR professionals.

🚀 Features
PDF Resume Upload: Upload resumes in PDF format and extract clean text using PyPDF2.

Job Description Matching: Enter a job description, and the AI will analyze how well the candidate fits the role.

LLM-Powered Insights: Uses llama3-8b-8192 via Groq API to generate a detailed report:

Resume summary

Match percentage

Gaps & suggestions for improvement

Email Integration: Automatically send shortlist or rejection emails to candidates via Gmail SMTP.

Database Logging: Stores resumes, AI responses, and status (PENDING, SELECTED, or REJECTED) using MySQL + SQLAlchemy.

Interactive UI: Built with Streamlit for an easy-to-use, dark-themed interface.

🔧 Tech Stack
Frontend: Streamlit (Python)

Backend: LangChain + Groq (LLM)

Database: MySQL + SQLAlchemy

Email: SMTP via smtplib

Env Config: python-dotenv

🛠 Use Cases
HR teams looking to automate initial resume screening

Startups and SMEs without dedicated recruiters

Resume optimization tools for candidates

🎯 SkillSync.AI saves time and improves hiring accuracy using the power of AI.

👉 Try it out or fork the repo to build your own AI recruiter
