import os
import time
import re
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st
from PyPDF2 import PdfReader
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama3-8b-8192", temperature=0)

Base = declarative_base()

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    content = Column(Text)
    llm_result = Column(Text)
    status = Column(String(50))

password = quote_plus("Ansari@2004")
engine = create_engine(f"mysql+mysqlconnector://root:{password}@localhost:3306/dropbox")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Utils
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def send_email(receiver_email, subject, content):
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = receiver_email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            smtp.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Error sending email:", e)
        st.error(f"❌ Email sending failed: {e}")

st.set_page_config(page_title="🧠🔗SkillSync.AI", layout="wide")

def clear_all():
    for key in st.session_state.keys():
        del st.session_state[key]

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif !important;
    background-color: #121212 !important;
    color: #e0e0e0 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] {
    background-color: lightblack !important;
    border-right: 1px solid #333 !important;
}
h1, h2, h3, h4 {
    color: black !important;
    font-size: 24px !important;
}
div[data-testid="stFileDropzone"] {
    padding: 12px !important;
    border: 1px dashed #888 !important;
    border-radius: 8px !important;
    background-color: #1e1e1e !important;
    font-size: 14px !important;
    min-height: 350px !important;
    max-width: 600px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
.stButton > button {
    background: linear-gradient(to right, #1f2937, #111827) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    transition: 0.3s ease-in-out !important;
    box-shadow: 0 2px 6px rgba(59,130,246,0.3) !important;
}
.stButton > button:hover {
    transform: scale(1.03) !important;
    box-shadow: 0 0 10px rgba(0, 224, 255, 0.4) !important;
}
.response-box {
    padding: 20px !important;
    border-radius: 10px !important;
    margin: 25px auto !important;
    font-size: 15px !important;
    line-height: 1.6em !important;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
    background-color: #1a1a1a !important;
    color: #f0f0f0 !important;
    max-width: 700px !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📩Upload Resume")
    pdf_doc = st.file_uploader("Upload PDF", type=["pdf"])
    st.write("Limit: 200MB")
    submit_button = st.button("Submit")
    st.markdown("__________________")
    new_chat = st.button("New Chat", key="new_chat")
    if new_chat:
        clear_all()
        st.rerun()

st.title("🧠🔗SkillSync.AI")

job_description = st.text_area(
    label="Eg: Looking for a Python Developer with Django, REST, SQL, Git...",
    height=80,
    placeholder="Upload your Job Description............."
)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for chats in st.session_state.chat_history:
    with st.chat_message(chats["role"]):
        st.markdown(chats["content"])

if pdf_doc is not None and job_description and submit_button:
    with st.spinner("Analyzing resume... Please wait ⏳"):
        resume_text = get_pdf_text([pdf_doc])
        email_extracted = extract_email(resume_text)

        system_msg = {
            "role": "system",
            "content":"""You are a career assistant analyzing resumes against job descriptions. 
            Your task is to:
            1. Extract and display all key details from the resume (name, contact info, education, work experience, skills, etc.)
            2. Compare these details against the job description
            3. Provide a detailed analysis of how well the resume matches the job requirements
            4. Suggest improvements for better alignment
            
            Format your response with clear sections:
            - Resume Summary
            - Job Requirements Analysis
            - Match Percentage
            - Suggested Improvements"""
        }

        human_msg = {
            "role": "user",
            "content": f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"
        }

        prompt = [system_msg, human_msg]
        llm_response = llm.invoke(prompt)

        # Save to DB
        new_resume = Resume(
            filename=pdf_doc.name,
            content=resume_text,
            llm_result=llm_response.content,
            status="PENDING"
        )
        session.add(new_resume)
        session.commit()

        with st.chat_message("Assistant"):
            full_response = ""
            message_placeholder = st.empty()
            for chunk in llm_response.content:
                full_response += chunk
                message_placeholder.markdown(full_response)
                time.sleep(0.01)

            st.session_state.chat_history.append({"role": "User", "content": "Resume & JD Uploaded."})
            st.session_state.chat_history.append({"role": "Assistant", "content": full_response})

        if email_extracted:
           st.markdown(f"**Email ID Extracted**: `{email_extracted}`")
           col1, col2 = st.columns(2)

           with col1:
                if st.button("✅ Select", use_container_width=True):
                    subject = "Congratulations! You're Shortlisted!"
                    content = (
                       "Dear Candidate,\n\n"
                        "You have been shortlisted for the role based on your resume.\n\n"
                       "Best,\nSkillSync.AI"
                    )
                    send_email(email_extracted, subject, content)
                    st.success("Shortlist email sent.")
                    st.toast("Email sent to candidate!", icon="📨")

                    existing_resume = session.query(Resume).filter_by(filename=pdf_doc.name).first()
                    if existing_resume:
                       existing_resume.status = "SELECTED"
                       existing_resume.llm_result += "\n\n[STATUS]: ✅ SELECTED\n📨 Email sent to candidate!"
                       session.commit()

                       st.markdown("### 🤖 LLM Response with Status")
                       st.code(existing_resume.llm_result, language="markdown")

                with col2:
                    if st.button("❌ Reject", use_container_width=True):
                        subject = "Regret to Inform"
                        content = (
                           "Dear Candidate,\n\n"
                           "Thank you for your interest, but you're not shortlisted at this moment.\n\n"
                           "Regards,\nSkillSync.AI"
                        )
                        send_email(email_extracted, subject, content)
                        st.warning("Rejection email sent.")
                        st.toast("Rejection email sent", icon="📨")

                        update_resume = session.query(Resume).filter_by(filename=pdf_doc.name).first()
                        if update_resume:
                         update_resume.status = "REJECTED"
                         update_resume.llm_result += "\n\n[STATUS]: ❌ REJECTED\n📨 Rejection email sent to candidate!"
                         session.commit()

        else:
            if submit_button:
                st.error("❌ Please upload both a resume PDF and job description before submitting")
        