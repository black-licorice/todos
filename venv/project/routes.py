from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user
import datetime
from time import sleep
from .models import Todo, User
from . import db

main = Blueprint('main', __name__)

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

