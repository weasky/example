 # -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request

from model.model import Model
from datetime import datetime
from pymongo.objectid import ObjectId
from pymongo import DESCENDING
from helper import humanizeTime
from markdown import markdown
from jinja2 import Markup
from wtforms import Form, BooleanField, TextField, TextAreaField, HiddenField, validators


app = Flask(__name__)
app.jinja_env.filters.update(humanizeTime = humanizeTime,
                             markdown = lambda e: Markup(markdown(e)))


class Post(Model):
    def __init__(self, **kwd):
        Model.__init__(self, **kwd)

    
    
@app.route('/')
def index():
    posts = Post().find().sort('date', direction=DESCENDING)
    return render_template('index.html', 
                           title = 'Liste des posts', 
                           posts = posts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = SaveForm(request.form)
    if request.method == 'POST' and form.validate():
        Post(title=form.title.data, 
             text=form.text.data,
             date=datetime.now()).save()
        return redirect(url_for('index'))
    return render_template('save_form.html', title='Nouveau post', 
                           form=form, action_url=url_for('add'))



@app.route('/edit/<id_to_edit>', methods=['GET', 'POST'])
def edit(id_to_edit):
    form = SaveForm(request.form)
    if request.method == 'POST' and form.validate:
        Post(_id = ObjectId(form.object_id.data),
             title = form.title.data, 
             text = form.text.data,
             date = datetime.now()).save()
        return redirect(url_for('index'))
    
    p = Post(_id=ObjectId(id_to_edit)).find_one()
    form = SaveForm(object_id = p['_id'], title = p['title'], text = p['text'], date = p['date'] )
    return render_template('save_form.html', 
                           title = 'Modifier post', 
                           form = form, 
                           action_url = url_for('edit', id_to_edit = id_to_edit))


class SaveForm(Form):
    object_id = HiddenField()
    title = TextField('Titre', [validators.Length(min=4, max=25),  validators.Required()])
    text = TextAreaField('Texte')


@app.route('/delete/<object_id>')
def delete(object_id):
    Post(_id=ObjectId(object_id)).remove()
    return redirect(url_for('index'))


@app.route('/view/<object_id>')
def view(object_id):
    p = Post(_id=ObjectId(object_id)).find_one()
    return render_template('view.html', **p)


if __name__ == '__main__':
    app.run(debug=True)

