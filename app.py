import os
import re
import string
from collections import Counter
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_resume(resume_text):
    # Remove email addresses
    resume_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', resume_text)
    # Remove phone numbers (various formats)
    resume_text = re.sub(r'\b(\+?\d{1,3}?[-.\s]?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\d{2}[-.\s]?\d{4}[-.\s]?\d{4}|\d{10}))\b', '', resume_text)
    return resume_text

def extract_text_from_txt(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def extract_tech_keywords(job_description):
    tech_keywords = [
        '0 to 1', 'AI', 'Adaptability', 'Agile', 'Agile Development Methodologies', 'Angular', 
        'API Integration', 'App Store', 'Architecture', 'AWS', 'AWS Lambda', 'Azure', 'Backend',
        'Back-end Development', 'Bash', 'C#', 'C++', 'CloudFront', 'Cloud Infrastructure', 
        'Cloud Platforms', 'Containerization', 'Continuous Deployment', 'Continuous Integration', 
        'Cross-functional', 'CSS', 'Data Science', 'Debugging', 'DevOps', 'Django', 'Docker', 
        'Elasticsearch', 'EC2', 'Express.js', 'Firebase', 'Flask', 'FastAPI', 'Frontend', 'Front-end Development', 
        'Full Stack', 'Fullstack', 'GCP', 'Git', 'github', 'GraphQL', 'Hadoop', 'Java', 'JavaScript', 'Jenkins', 'Jest', 'Keras', 
        'Kotlin', 'Kubernetes', 'Linux', 'Machine Learning', 'Matplotlib', 'Mocha', 'MongoDB', 'MySQL', 
        'Node', 'Node.js', 'NoSQL', 'NoSQL Databases', 'NumPy', 'Pandas', 'PHP', 'postgres', 'PostgreSQL', 
        'Problem-solving', 'PyTorch', 'PyTest', 'Pyramid', 'React', 'React Native', 'Redis', 'Reliability', 
        'Ruby', 'Ruby on Rails', 'Scalability', 'Scrum', 'Security', 'Serverless', 'Shell Scripting', 
        'SQL', 'Team Collaboration', 'Testing Frameworks', 'TensorFlow', 'TypeScript', 
        'Unix', 'UI/UX', 'User Privacy', 'Version Control', 'Vue.js', 'Web Development'
    ]

    job_description = job_description.translate(str.maketrans('', '', string.punctuation)).lower()
    keyword_counts = Counter()
    for keyword in tech_keywords:
        count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', job_description))
        if count > 0:
            keyword_counts[keyword] = count
    return keyword_counts

def analyze_resume_against_keywords(resume, keyword_counts):
    resume = resume.translate(str.maketrans('', '', string.punctuation)).lower()
    resume_counts = Counter()
    for keyword in keyword_counts:
        count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', resume))
        resume_counts[keyword] = count
    return resume_counts

def compare_keywords(job_keywords, resume_keywords):
    matched_keywords = {}
    missing_keywords = {}
    for keyword, count in job_keywords.items():
        if resume_keywords.get(keyword, 0) > 0:
            matched_keywords[keyword] = resume_keywords[keyword]
        else:
            missing_keywords[keyword] = count
    return matched_keywords, missing_keywords

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'job_description' not in request.files or 'resume' not in request.files:
        return redirect(request.url)

    job_file = request.files['job_description']
    resume_file = request.files['resume']

    if job_file and allowed_file(job_file.filename) and resume_file and allowed_file(resume_file.filename):
        job_filename = secure_filename(job_file.filename)
        resume_filename = secure_filename(resume_file.filename)

        job_file_path = os.path.join(app.config['UPLOAD_FOLDER'], job_filename)
        resume_file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)

        job_file.save(job_file_path)
        resume_file.save(resume_file_path)

        job_description = extract_text_from_txt(job_file_path)
        resume = extract_text_from_txt(resume_file_path)

        # Sanitize the resume
        resume = sanitize_resume(resume)

        job_keywords = extract_tech_keywords(job_description)
        resume_keywords = analyze_resume_against_keywords(resume, job_keywords)

        matched_keywords, missing_keywords = compare_keywords(job_keywords, resume_keywords)

        return render_template('results.html', job_keywords=job_keywords, resume_keywords=resume_keywords, matched_keywords=matched_keywords, missing_keywords=missing_keywords)

    return redirect(request.url)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
