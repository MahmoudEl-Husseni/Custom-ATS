from flask import Flask, render_template, request, redirect, url_for, session
import os, sys, json
import logging

import utils
from model import ATS

app = Flask(__name__)

# Set upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set secret key for session handling
with open('secrets/app_secret_key', 'r') as f:
    app.secret_key = f.read().strip()



if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Get the uploaded resume
    resume = request.files['resume']
    if resume:
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
        resume.save(resume_path)

        # Get absolute path for further processing
        absolute_resume_path = os.path.abspath(resume_path)

    # Get categories and values (key-value pairs)
    categories = request.form.getlist('keys[]')
    values = request.form.getlist('values[]')
    category_value_pairs = dict(zip(categories, values))

    # Process the resume with ATS
    extracted_skills = ats.process(absolute_resume_path, category_value_pairs)
    extracted_skills = extracted_skills.replace('[', '{').replace(']', '}')
    logging.info(50*'-')
    logging.info(f"Extracted skills: {extracted_skills}")
    logging.info(50*'-')
    extracted_skills = json.loads(extracted_skills)

    fitting_skills = ats.compare(extracted_skills, category_value_pairs)
    fitting_skills = fitting_skills.replace('[', '{').replace(']', '}')
    fitting_skills = '\n'.join(fitting_skills.split('\n')[1:-1])
    logging.info(50*'-')
    logging.info(fitting_skills)
    logging.info(50*'-')
    fitting_skills = json.loads(fitting_skills)

    # Store results in session
    session['extracted_skills'] = extracted_skills
    session['standard_skills'] = category_value_pairs
    session['fitting_skills'] = fitting_skills

    # Redirect to /results page
    return redirect(url_for('results'))

@app.route('/results', methods=['GET'])
def results():
    # Retrieve the data from session
    extracted_skills = session.get('extracted_skills', {})
    standard_skills = session.get('standard_skills', {})
    fitting_skills = session.get('fitting_skills', {})

    return render_template('result.html', 
                           extracted_skills=extracted_skills, 
                           standard_skills=standard_skills, 
                           result=fitting_skills)

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info("Starting the application\n\n")
    cfg = utils.load_config('config.json')
    ats = ATS(cfg)
    app.run(debug=True)
