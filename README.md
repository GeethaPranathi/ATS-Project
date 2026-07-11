# 🧠 ATS-Project  
### Smart ATS Resume Analyzer using Gemini AI

ATS-Project is a Flask-based web application that analyzes a candidate’s resume against a given job description using Google Gemini AI.  
It simulates an Applicant Tracking System (ATS) by providing an ATS score, matching skills, missing skills, and improvement suggestions.

---

## 🚀 Features

- Upload resume in PDF format
- Paste job description
- Automatic resume text extraction
- AI-powered ATS analysis using Gemini LLM
- Provides:
  - ATS score (0–100)
  - Matching skills
  - Missing skills
  - Improvement suggestions
- Clean and responsive user interface with loading animation

---

## 🛠️ Tech Stack

Backend
- Python
- Flask
- Google Gemini API
- PyPDF2
- python-dotenv

Frontend
- HTML
- CSS
- JavaScript (Fetch API)

---

## 📁 Project Structure

ATS-Project/
│
├── templates/
│   └── index.html
│
├── uploads/
│   └── (uploaded resume PDFs)
│
├── .env
├── main.py
├── README.md
└── LICENSE

---

## 🔑 Environment Variables

Create a .env file in the root directory:

GEMINI_API_KEY=your_gemini_api_key_here

Do not expose your API key in public repositories.

---

## 📦 Installation

1. Clone the repository:
git clone https://github.com/your-username/ATS-Project.git
cd ATS-Project

2. Install required dependencies:
pip install flask google-generativeai PyPDF2 python-dotenv

---

## ▶️ Run the Application

python main.py

The application will start at:
http://localhost:8000

---

## 🧠 How It Works

1. User uploads a resume PDF  
2. User enters a job description  
3. Resume text is extracted using PyPDF2  
4. Gemini AI compares the resume and job description  
5. The system generates:
- ATS score
- Matching skills
- Missing skills
- Improvement recommendations

---

## 🔌 API Endpoint

POST /analyze

Inputs
- resume → PDF file
- job_description → Text

Response
{
  "ats_result": "AI-generated ATS analysis"
}

---

## 🎯 Use Cases

- Students optimizing resumes
- Job seekers checking ATS compatibility
- AI-based resume screening demos
- HR automation proof-of-concepts

---

## 🔮 Future Enhancements

- Resume keyword highlighting
- Downloadable ATS report (PDF)
- Multiple resume comparison
- User authentication
- Skill-wise scoring system

---

## 📜 License

This project is licensed under the MIT License.

---

## 👩‍💻 Author

Geetha Pranathi Kanala
