import datetime
import os
import pytz
from flask import Flask, Blueprint, flash, redirect, url_for, render_template, request, get_flashed_messages
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, current_user, logout_user, login_user, UserMixin


app = Flask(__name__)
db = SQLAlchemy(app=app)
scheduler = APScheduler()

app.config['SECRET_KEY'] = os.getenv('SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # because user_id is primary key:
    return User.query.get(int(user_id))



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    def __repr__(self):
        return '<User %r>' % self.id


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email_me = db.Column(db.Boolean, default=False)
    email_date = db.Column(db.DateTime)
    def __repr__(self):
        return '<Todo %r>' % self.id


@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        todos = Todo.query.filter_by(person_id=current_user.id).order_by(Todo.date_added.desc()).all()
        if todos:
            return render_template('todos.html', todos=todos, datetime=datetime.datetime)
        flash('No todos, please add a todo')
        return render_template('todos.html', datetime=datetime.datetime)
    flash('Sign in to start adding todos')
    return render_template('todos.html', datetime=datetime.datetime)

@app.route('/', methods=['POST'])
@login_required
def index_post():
    if current_user.is_authenticated:
        todo_content = request.form.get('content')
        new_todo = Todo(content=todo_content, person_id=current_user.id)
        new_todo.email_me = True if request.form.get('email_me') else False
        if new_todo.email_me:
            date_in = request.form.get('email_date')
            date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
            date_processing = [int(v) for v in date_processing]
            date_out = datetime.datetime(*date_processing)
            new_todo.email_date = date_out.astimezone(tz=pytz.utc)
            print(new_todo.email_date)
        else:
            new_todo.email_date = None
        try:
            db.session.add(new_todo)
            db.session.commit()
            return redirect('/')
        except:
            flash('There was a problem adding your todo')
            return redirect(url_for('index'))
    flash('Please sign in to do that')
    return redirect(url_for('login'))


def timed_email():
    time = datetime.datetime.utcnow()
    for todo in db.session.query(Todo).filter_by(email_me=True).all():
        if str(todo.email_date).split(',')[0][0:10] == str(time).split(' ')[0]:
            email_time = str(todo.email_date).split(',')[0].split(' ')[1][0:5]
            print(time, email_time, todo.content)
            if email_time == time.strftime('%H:%M'):
                user = db.session.query(User).filter_by(id=todo.person_id).all()
                user_email = user[0].email
                import smtplib
                gmailaddress = os.getenv('EMAIL')
                gmailpassword = os.getenv('EMAIL_PASSWORD')
                mailto = user_email
                subject = 'Todo Reminder'
                msg = todo.content
                message = f"Subject: {subject}\n\n{msg}".encode('utf-8')
                mailServer = smtplib.SMTP('smtp.gmail.com', 587)
                mailServer.starttls()
                mailServer.login(gmailaddress, gmailpassword)
                mailServer.sendmail(gmailaddress, mailto, message)
                mailServer.quit()


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    todo_to_delete = Todo.query.get_or_404(id)
    if current_user.id == todo_to_delete.person_id:
        try:
            db.session.delete(todo_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a probleme deleting that todo'
    flash('You do not have permission to do that')
    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    todo = Todo.query.get_or_404(id)
    if todo.person_id == current_user.id:
        if request.method == 'POST':
            todo.content = request.form['content']
            try:
                db.session.commit()
                return redirect('/')
            except:
                return 'There was an issue updating your todo'
        else:
            return render_template('updateTodo.html', todo=todo)
    flash('You do not have permission to do that')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash('Please check your email and password and try again')
        return redirect(url_for('login'))
    login_user(user, remember=remember)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    if email and name and password:
        # if user query returns a value for the email field, the email is then already tied to a user
        if db.session.query(User).filter_by(email=email).first():
            # this return will short circuit the route, redirecting to the signup get route
            flash('Email address already exists')
            return redirect(url_for('register'))
        # user is created and added to db
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        # redirecrts to login route
        return redirect(url_for('login'))
    flash('Please fill out the form')
    return redirect(url_for('register'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


scheduler.add_job(id='Timed Email', func=timed_email, trigger='interval', seconds=30)
scheduler.start()