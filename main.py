import os
from flask import Flask, request, jsonify, render_template
from google import genai
import PyPDF2
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  
# =====================
# CONFIG
# =====================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = Flask(__name__, template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# =====================
# HOME
# =====================
@app.route("/")
def home():
    return render_template("index.html")

# =====================
# PDF TEXT EXTRACTION
# =====================
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


# ==============================
# RESUME PARSER (LLM)
# ==============================
def parse_resume(resume_text):
    prompt = f"""
You are a resume parser.

Extract:
- Skills
- Experience summary
- Education
- Tools & technologies

Resume:
{resume_text}

Return in bullet points.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ==============================
# JOB DESCRIPTION PARSER
# ==============================
def parse_job_description(jd_text):
    prompt = f"""
Extract:
- Required skills
- Responsibilities
- Preferred qualifications

Job Description:
{jd_text}

Return in bullet points.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ==============================
# ATS MATCHING
# ==============================
def ats_match(parsed_resume, parsed_jd):
    prompt = f"""
You are an Applicant Tracking System.

Compare the resume and job description.

Resume:
{parsed_resume}

Job Description:
{parsed_jd}

Provide:
1. Match percentage (0-100)
2. Matching skills
3. Missing skills
4. Strengths
5. Improvement suggestions
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# =====================
# ATS ANALYSIS ROUTE
# =====================
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "Resume PDF required"}), 400

    resume = request.files["resume"]
    jd = request.form.get("job_description")

    if not jd:
        return jsonify({"error": "Job description required"}), 400

    path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
    resume.save(path)

    resume_text = extract_text_from_pdf(path)

    prompt = f"""
You are an ATS system.

Resume:
{resume_text}

Job Description:
{jd}

Return:
- ATS score (0-100)
- Matching skills
- Missing skills
- Improvements
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return jsonify({
        "ats_result": response.text
    })

# =====================
# RUN SERVER
# =====================
if __name__ == "__main__":
    app.run(debug=True, port=8000)