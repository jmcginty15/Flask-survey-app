from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, satisfaction_survey, personality_quiz, surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yeet'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

responses = []
comments = []
completed_surveys = []
incomplete_surveys = [{'ident': 'satisfaction', 'title': satisfaction_survey.title}, {'ident': 'personality', 'title': personality_quiz.title}]
survey_id = ''
question_num = 1

@app.route('/')
def home_page():
    """Displays the home page"""
    global question_num
    global responses
    global completed_surveys
    global incomplete_surveys
    question_num = 1
    responses = []
    comments = []
    try:
        completed_surveys = session['completed']
        incomplete_surveys = session['incomplete']
    finally:
        all_complete = False if incomplete_surveys else True
        return render_template('home.html', incomplete=incomplete_surveys, completed=completed_surveys, all_complete=all_complete)

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
    session['comments'] = []
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
            return render_template('question.html', question_num=question_num, question=question.question, choices=question.choices, allow_text=question.allow_text)
        return redirect(f'/thankyou/{surv}')
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
    try:
        comment = request.form['comment']
        comments = session['comments']
        comments.append(comment)
        session['comments'] = comments
    finally:
        return redirect(f'/questions/{survey_id}/{question_num}')

@app.route('/thankyou/<surv>')
def thank_you(surv):
    """Displays the Thank You page with a list of questions and answers"""
    global incomplete_surveys
    survey = surveys[surv]
    questions = survey.questions
    completed_surveys.append({'ident': surv, 'title': survey.title})
    incomplete_surveys = [incomplete for incomplete in incomplete_surveys if incomplete['ident'] != surv]
    session['completed'] = completed_surveys
    session['incomplete'] = incomplete_surveys
    responses = session['responses']
    comments = session['comments']
    j = 0
    for i in range(len(questions)):
        questions[i].response = responses[i]
        if questions[i].allow_text:
            questions[i].comment = comments[j]
            j += 1
    survey.questions = questions
    return render_template('thank_you.html', title=survey.title, questions=questions)

@app.route('/see-answers/<surv>')
def see_answers(surv):
    """Displays answers for the chosen completed survey"""
    survey = surveys[surv]
    return render_template('answers.html', title=survey.title, questions=survey.questions)