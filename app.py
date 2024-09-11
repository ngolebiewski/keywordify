import os
import re
import string
from collections import Counter
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)

# Database configuration from environment variables
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

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

def clean_text(text):
    # This regex removes punctuation except for those that are part of a word (e.g., "node.js")
    return re.sub(r'(?<!\w)[^\w\s](?!\w)', '', text).lower()

def extract_tech_keywords(job_description):
    tech_keywords = [
        '0 to 1', 'A11y', 'AI', 'API', 'API Integration', 'ASP.NET', 'AWS', 'AWS Lambda', 
        'Accessibility', 'Adaptability', 'Agile', 'Agile Development Methodologies', 'Android', 
        'Angular', 'Apollo GraphQL', 'App Store', 'Architecture', 'Assembly', 'Azure', 
        'B2B', 'Back-end Development', 'Bash', 'C', 'C#', 'C++', 'CI/CD', 'CSS', 
        'Cloud Infrastructure', 'Cloud Platforms', 'CloudFront', 'Continuous Deployment', 
        'Continuous Integration', 'Coroutines', 'Cross-functional', 'Dart', 'Data Science', 
        'Debugging', 'DevOps', 'Django', 'Docker', 'EC2', 'Elasticsearch', 'Electron', 
        'Elixir', 'Erlang', 'Express', 'Express.js', 'F#', 'FastAPI', 'Figma', 'Firebase', 
        'Flask', 'Framework', 'Front-end Development', 'Full Stack', 'GCP', 'GULP', 
        'Game Engine', 'Git', 'GitHub', 'Go', 'GraphQL', 'HTML', 'Hadoop', 'Haskell', 
        'Java', 'JavaScript', 'Jenkins', 'Jira', 'Julia', 'Keras', 'Kotlin', 'Kubernetes', 
        'Linux', 'Lua', 'MATLAB', 'MVVM with LiveData and Data Binding', 'Machine Learning', 
        'Material UI', 'Matplotlib', 'Mobile', 'MongoDB', 'MySQL', 'NoSQL', 
        'NoSQL Databases', 'Node', 'Node.js', 'NumPy', 'OAuth', 'PHP', 'PL/SQL', 
        'Perl', 'Phaser', 'Phaser3', 'Photoshop', 'Poetry', 'PostgreSQL', 'Postgres', 
        'PowerShell', 'Prisma ORM', 'Problem-solving', 'PyTest', 'PyTorch', 'Pyramid', 
        'Python', 'QA', 'R', 'REST APIs', 'Racket', 'Rails', 'React', 'React Native', 
        'Redis', 'Redux', 'Relational Database', 'Reliability', 'Render', 'Retrofit', 
        'Ruby', 'Ruby on Rails', 'Rust', 'SAML', 'SCIM', 'SDK', 'SFTP', 'SQL', 'SSH', 
        'SaaS', 'Scala', 'Scalability', 'Scheme', 'Security', 'Serverless', 
        'Shell Scripting', 'Single Sign-on', 'Socket.io', 'Spring', 'Spring Boot', 
        'Swift', 'T-SQL', 'Tailwind CSS', 'Team Collaboration', 'TensorFlow', 
        'Testing Frameworks', 'Triage', 'TypeScript', 'UI/UX', 'Unity', 'Unreal', 
        'User Privacy', 'VHDL', 'Verilog', 'Version Control', 'Vite', 'Vue', 
        'Vue.js', 'WCAG', 'Web Development', 'Web Performance', 'WordPress', 
        'backend', 'block-chain', 'data', 'frontend', 'frontend fundamentals', 
        'iOS', 'mobile platforms', 'modern frameworks', 'p5.js', 'pandas', 
        'product management', 'springboot'
    ]

    job_description = clean_text(job_description)
    keyword_counts = Counter()
    for keyword in tech_keywords:
        count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', job_description))
        if count > 0:
            keyword_counts[keyword] = count
    return keyword_counts

def analyze_resume_against_keywords(resume, keyword_counts):
    resume = clean_text(resume)
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

def save_job_description_to_db(resume_text):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        insert_query = """INSERT INTO job_descriptions (text, user_id, valid) VALUES (%s, %s, %s)"""
        cursor.execute(insert_query, (resume_text, None, True))
        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        print(f"Failed to insert record: {error}")

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

        # Save the sanitized job description to the database
        save_job_description_to_db(job_description)

        job_keywords = extract_tech_keywords(job_description)
        resume_keywords = analyze_resume_against_keywords(resume, job_keywords)

        matched_keywords, missing_keywords = compare_keywords(job_keywords, resume_keywords)

        return render_template('results.html', job_keywords=job_keywords, resume_keywords=resume_keywords, matched_keywords=matched_keywords, missing_keywords=missing_keywords)

    return redirect(request.url)


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)