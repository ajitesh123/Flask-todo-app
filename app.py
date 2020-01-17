from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate, MigrateCommand

app=Flask(__name__)
#Creates an application names after your file. It's an instance of flask
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://ajitesh@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
#Links SQLAlchemy with flask app

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__='todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False,
    default=False)

    def __repr__(self):
        return f"<Todo {self.id}: {self.description}>"

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo=Todo.query.get(todo_id)
        todo.completed=completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

#Sort of function to call function. Decoraters could be used to call function multiple times.
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description=request.get_json()['description']
        todo=Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
        #we have to do thsi here as todo.descritpion becomes out of date if we close the session. So we
        #can't do this assignment in the jsonify stage
    except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)
#Index is the name of route handler for the home page

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.order_by('id').all())
