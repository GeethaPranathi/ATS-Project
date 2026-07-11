import os
import json
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
import PyPDF2
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ATSAnalysisResponse(BaseModel):
    score: int = Field(description="ATS compatibility score from 0 to 100")
    matching_skills: List[str] = Field(description="List of matching skills found in both the resume and the job description")
    missing_skills: List[str] = Field(description="List of critical skills or keywords present in the job description but missing or weak in the resume")
    strengths: List[str] = Field(description="Key strengths highlighted in the resume that align with the job")
    recommendations: List[str] = Field(description="Actionable feedback and specific improvements to optimize the resume for this job description")

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
        model="gemini-flash-latest",
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
        model="gemini-flash-latest",
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
        model="gemini-flash-latest",
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

    try:
        path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
        resume.save(path)

        resume_text = extract_text_from_pdf(path)

        prompt = f"""
You are an ATS system. Compare the resume text with the job description.
Extract the match score, matching skills, missing skills, strengths, and recommendations.

Resume text:
{resume_text}

Job Description:
{jd}
"""

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ATSAnalysisResponse,
            temperature=0.2
        )

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=config
        )

        result_data = json.loads(response.text)
        return jsonify(result_data)

    except Exception as e:
        error_msg = str(e)
        status_code = 500
        
        # Provide user-friendly errors for common failure scenarios
        if "429" in error_msg or "quota" in error_msg.lower() or "exhausted" in error_msg.lower():
            error_msg = "Gemini API Quota Exceeded. Please try again in a few minutes, or upgrade your API plan."
            status_code = 429
        elif "api key" in error_msg.lower() or "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower() or "401" in error_msg:
            error_msg = "Invalid Gemini API Key. Please verify the GEMINI_API_KEY in your .env file."
            status_code = 401
        elif "503" in error_msg or "unavailable" in error_msg.lower() or "overloaded" in error_msg.lower():
            error_msg = "Gemini API is currently experiencing high demand (503 Service Unavailable). Please wait a few seconds and try again."
            status_code = 503
            
        return jsonify({"error": error_msg}), status_code

# =====================
# RUN SERVER
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=False, host="0.0.0.0", port=port)