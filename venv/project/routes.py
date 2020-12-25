import os
import datetime
from flask import Flask, Blueprint, flash, redirect, url_for, render_template, request, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from time import sleep
from .models import Todo, User


db = SQLAlchemy()
main = Flask(__name__)

main.config['SECRET_KEY'] = os.getenv('SECRET')
main.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(main)

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.init_app(main)


@login_manager.user_loader
def load_user(user_id):
    # because user_id is primary key:
    return User.query.get(int(user_id))


@main.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        # print(db.session.query(Todo).filter_by(person_id=current_user.id).all()[0].email_date)
        # print(db.session.query(Todo).filter_by(person_id=current_user.id).all()[0].email_me)
        print(datetime.datetime.utcnow().date())
        #  OLD Todo.query.order_by(Todo.date_added).all()
        todos = Todo.query.filter_by(person_id=current_user.id).order_by(Todo.date_added.desc()).all()
        if todos:
            return render_template('todos.html', todos=todos, datetime=datetime.datetime)
        flash('No todos, please add a todo')
        return render_template('todos.html', datetime=datetime.datetime)
    flash('Sign in to start adding todos')
    todo_list = Todo.query.filter_by(email_me=True).order_by(Todo.email_date.desc()).all()
    print(todo_list[0].email_date)
    print(datetime.datetime.utcnow())
    return render_template('todos.html', datetime=datetime.datetime)

@main.route('/', methods=['POST'])
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
            new_todo.email_date = date_out
        else:
            new_todo.email_date = None
        try:
            db.session.add(new_todo)
            db.session.commit()
            return redirect('/')
        except:
            flash('There was a problem adding your todo')
            return redirect(url_for('main.index'))
    flash('Please sign in to do that')
    return redirect(url_for('main.login'))


@main.route('/delete/<int:id>')
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
    return redirect(url_for('main.index'))


@main.route('/update/<int:id>', methods=['GET', 'POST'])
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
    return redirect(url_for('main.index'))


@main.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@main.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash('Please check your email and password and try again')
        return redirect(url_for('main.login'))
    login_user(user, remember=remember)
    return redirect(url_for('main.index'))


@main.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@main.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # if user query returns a value for the email field, the email is then already tied to a user
    if db.session.query(User).filter_by(email=email).first():
        # this return will short circuit the route, redirecting to the signup get route
        flash('Email address already exists')
        return redirect(url_for('main.register'))
    # user is created and added to db
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    # redirecrts to login route
    return redirect(url_for('main.login'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

