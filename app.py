from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, satisfaction_survey

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yeet'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

responses = []
question_num = 1

@app.route('/')
def home_page():
    global question_num
    global responses
    question_num = 1
    responses = []
    return render_template('home.html', title=satisfaction_survey.title, instructions=satisfaction_survey.instructions, num=question_num)

@app.route('/questions/<num>')
def questions(num):
    global question_num
    if int(num) == question_num:
        if int(num) <= len(satisfaction_survey.questions):
            question = satisfaction_survey.questions[int(num) - 1]
            choices = question.choices
            return render_template('question.html', question_num=int(num), question=question.question, choices=choices)
        return redirect('/thankyou')
    else:
        flash('Invalid question! Please do the survey in order.')
        return redirect(f'/questions/{question_num}')

@app.route('/answer', methods=['POST'])
def add_answer():
    global question_num
    question_num += 1
    answer = request.form['choice']
    responses.append(answer)
    return redirect(f'/questions/{question_num}')

@app.route('/thankyou')
def thank_you():
    return render_template('thank_you.html')