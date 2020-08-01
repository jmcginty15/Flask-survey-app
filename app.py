from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, satisfaction_survey, personality_quiz, surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yeet'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

responses = []
survey_id = ''
question_num = 1

@app.route('/')
def home_page():
    """Displays the home page"""
    global question_num
    global responses
    question_num = 1
    responses = []
    return render_template('home.html')

@app.route('/survey-choice', methods=['POST'])
def survey_choice():
    """Takes form response and redirects to the chosen survey's start page"""
    global survey_id
    survey_id = request.form['survey']
    return redirect(f'/surveys/{survey_id}')

@app.route('/surveys/<surv>')
def survey_home(surv):
    """Displys start page for chosen survey"""
    survey = surveys[surv]
    return render_template('survey-home.html', title=survey.title, instructions=survey.instructions)

@app.route('/session-init', methods=['POST'])
def session_init():
    """Initiates session responses list to an empty list to start the survey"""
    global question_num
    global survey_id
    session['responses'] = []
    return redirect(f'/questions/{survey_id}/{question_num}')

@app.route('/questions/<surv>/<num>')
def questions(surv, num):
    """Displays next survey question"""
    global question_num
    global survey_id
    survey = surveys[surv]
    if int(num) == question_num:
        if question_num <= len(survey.questions):
            question = survey.questions[question_num - 1]
            choices = question.choices
            return render_template('question.html', question_num=question_num, question=question.question, choices=choices)
        return redirect('/thankyou')
    else:
        flash('Invalid question! Please do the survey in order.')
        return redirect(f'/questions/{survey_id}/{question_num}')

@app.route('/answer', methods=['POST'])
def add_answer():
    """Adds the answer to the list of responses"""
    global question_num
    global survey_id
    question_num += 1
    answer = request.form['choice']
    responses = session['responses']
    responses.append(answer)
    session['responses'] = responses
    return redirect(f'/questions/{survey_id}/{question_num}')

@app.route('/thankyou')
def thank_you():
    return render_template('thank_you.html')