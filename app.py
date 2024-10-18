from flask import Flask, request, redirect, url_for, render_template
import os
import mysql.connector
import PyPDF2  # Library to read PDF files

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Ensure this directory exists

# Database configuration
db_config = {
    'user': 'root',  # Replace with your MySQL username
    'password': 'Jay@ry@20032005',  # Replace with your MySQL password
    'host': 'localhost',
    'database': 'JobMatchingDB'
}

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return "No file part"
    
    file = request.files['resume']
    
    if file.filename == '':
        return "No selected file"
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Process the PDF to extract text or skills
    skills = extract_skills_from_pdf(file_path)

    # Fetch job suggestions based on extracted skills
    job_suggestions = suggest_jobs(skills)

    # Redirect to results
    return render_template('result.html', skills=skills, job_suggestions=job_suggestions)

def extract_skills_from_pdf(file_path):
    skills = ""
    # Use PyPDF2 to extract text from PDF
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            skills += page.extract_text() + "\n"
    return skills.strip()

def suggest_jobs(skills):
    job_roles = fetch_job_roles()
    matching_roles = []
    
    for role in job_roles:
        role_name = role[0]
        # Check if any of the skills match the role's required skills
        if any(skill in skills for skill in get_required_skills_for_role(role_name)):
            matching_roles.append(role_name)
            
    
    return matching_roles

def fetch_job_roles():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT role_name FROM JobRoles")
    job_roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return job_roles

def get_required_skills_for_role(role_name):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.skill_name
        FROM Skills s
        JOIN JobRoleSkills jrs ON s.id = jrs.skill_id
        JOIN JobRoles jr ON jr.id = jrs.job_role_id
        WHERE jr.role_name = %s
    """, (role_name,))
    skills = cursor.fetchall()
    cursor.close()
    conn.close()
    return [skill[0] for skill in skills]

if __name__ == '__main__':
    app.run(debug=True)
