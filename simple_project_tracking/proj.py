#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from __future__ import with_statement
from contextlib import closing
from datetime import date, datetime, timedelta
from hashlib import md5
import sqlite3

import config
import forms
from generators import dict_gen

from flask import (abort, flash, Flask, g, request, session, 
                    redirect, render_template, url_for)
from werkzeug import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.debug = config.DEBUG
app.config['DATABASE'] = config.DATABASE_URI

def tsformat(value, format='%Y-%d-%m'):
    ''' Jinja2 filter, as suggested here:
        http://jinja.pocoo.org/2/documentation/api#custom-filters
    '''
    return value.strftime(format)

app.jinja_env.filters['tsformat'] = tsformat

def connect_db():
    ''' Connect to SQLite db with support for ISO dates/timestamps.
    
        More information here:
        http://docs.python.org/library/sqlite3.html#default-adapters-and-converters
    '''
    return sqlite3.connect(app.config['DATABASE'], 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

def init_db():
    with closing(connect_db()) as db:
        with open('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = g.db.execute('select user_id from users where username = ?',
                       [username]).fetchone()
    return rv[0] if rv else None

@app.errorhandler(401)
def page_not_found(error):
    return render_template('not_authorized.html'), 401

@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404

@app.route('/clients', methods=['GET', 'POST'])
def clients():
    form = forms.ClientCreateForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        department = form.department.data
        
        g.db.execute('''
            INSERT INTO 
                clients (name, department, created, updated) 
            VALUES (?,?,?,?)''', 
            (name, department, datetime.now(), datetime.now())
        )
        
        flash('Client added')
        g.db.commit()
            
        return redirect(url_for('clients'))
        
    cur = g.db.execute('''
        SELECT 
            name, department, created, updated
        FROM 
            clients 
        ORDER BY 
            id DESC;''')
    clients = [r for r in dict_gen(cur)]
    
    return render_template('clients.html', clients=clients, form=form)

@app.route('/projects', methods=['GET', 'POST'])
def projects():
    ''' Interface to add a project, and optionally a client.
    
        Unfortunately this view has some slightly complex logic.
        
    '''
    form = forms.ProjectCreateForm(request.form)
    cur = g.db.execute('''
        SELECT 
            id, name 
        FROM 
            clients 
        ORDER BY 
            name;''')
    # blank option 
    # so that a project without a client can be created
    choices = [(0, '(choose/insert a client)')]
    try:
        choices.extend((row[0], row[1]) for row in cur.fetchall())
    except TypeError:
        # nothing in db yet!
        pass 
    
    # populate choices for <select> element of form
    form.client_id.choices = choices
        
    if request.method == 'POST' and form.validate():
        if len(form.name.data) != 0 or len(form.department.data) != 0:            
            name = form.name.data
            department = form.department.data
            
            g.db.execute('''
                INSERT INTO 
                    clients (name, department, created, updated) 
                VALUES (?,?,?,?)''', 
                (name, department, datetime.now(), datetime.now())
            )
            g.db.commit()
            # fetch most recently inserted client.id
            max_cid = g.db.execute('''
                SELECT MAX(id) 
                FROM clients;''').fetchone()[0]
            
        title = form.title.data
        description = form.description.data
        
        # get the most recently inserted client; 
        # if that doesn't work, grab data from form
        try:
            client_id = max_cid
        except NameError:
            client_id = form.client_id.data
        
        # don't insert a client id 
        # if name is empty
        try:
            g.db.execute('''
                INSERT INTO 
                    projects (title, description, client_id, 
                        created, updated) 
                VALUES (?,?,?,?,?)''', 
                (title, description, client_id, datetime.now(), 
                datetime.now())
            )
        except NameError: # no `client_id` yet!
            g.db.execute('''
                INSERT INTO 
                    projects (title, description, created, updated) 
                VALUES (?,?,?,?)''', 
                (title, description, datetime.now(), datetime.now())
            )
            
        flash('Project added')
        g.db.commit()
        return redirect(url_for('projects'))
    cur = g.db.execute('''
        SELECT 
            p.title, p.description, c.name, p.created, p.updated
        FROM 
            projects p
            LEFT JOIN clients c
            ON c.id = p.client_id
        ORDER BY 
            p.id DESC;''')
    projs = [r for r in dict_gen(cur)]
    
    return render_template('projects.html', projs=projs, form=form)
    
@app.route('/edit_client', methods=['GET', 'POST'])
def edit_client():
    ''' Delete/edit a client. '''
    if 'user_id' not in session:
        abort(401)
    cur = g.db.execute('''
            SELECT 
                id, name, department
            FROM 
                clients 
            ORDER BY 
                id DESC;''')
    clients = [r for r in dict_gen(cur)]
    
    if request.method == 'POST':
        if 'delete' in request.form:
            cur = g.db.execute('''DELETE FROM clients WHERE id = ?''', 
                request.form['id'])
            g.db.commit()
            flash('Client deleted')
            return redirect(url_for('index'))

        id = request.form['id']
        name = request.form['name']
        department = request.form['department']
    
        g.db.execute('''
                UPDATE clients 
                   SET name = ?, department = ?, updated = ?
                 WHERE id = ?''', 
                (name, department, datetime.now(), id)
            )
        g.db.commit()
        flash('Client edited')
        return redirect(url_for('edit_client'))
    return render_template('edit_client.html', clients=clients)

@app.route('/edit_project', methods=['GET', 'POST'])
def edit_project():
    ''' Delete/edit a project. '''
    if 'user_id' not in session:
        abort(401)
    cur = g.db.execute('''
        SELECT 
            id, title, description, client_id
        FROM 
            projects 
        ORDER BY 
            id DESC;''')
    projs = [r for r in dict_gen(cur)]
    
    qry = '''
        SELECT id, name 
          FROM clients 
         WHERE id IN (%s)''' % ','.join('?'*len(projs))
    cur = g.db.execute(qry, [proj['id'] for proj in projs])
    clients = [r for r in dict_gen(cur)]
    
    if request.method == 'POST':
        if 'delete' in request.form:
            cur = g.db.execute('''DELETE FROM projects WHERE id = ?''', 
                request.form['id'])
            g.db.commit()
            flash('Project deleted')
            return redirect(url_for('index'))
            
        id = request.form['id']
        title = request.form['title']
        description = request.form['description']
        client_id = request.form['client_id']
    
        g.db.execute('''
                UPDATE projects 
                   SET title = ?, description = ?,
                       client_id = ?, updated = ?
                 WHERE id = ?''', 
                (title, description, client_id, datetime.now(), id)
            )
        g.db.commit()
        flash('Project edited')
        return redirect(url_for('edit_project'))
    
    return render_template('edit_project.html', projs=projs, clients=clients)
    
@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        cur = g.db.execute('''SELECT * 
                                FROM users
                               WHERE user_id = ?''', [session['user_id']])
        g.user = cur.fetchone()[0]

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/', methods=['GET'])
def index():
    cur = g.db.execute('''
          SELECT title, description 
            FROM projects 
        ORDER BY id DESC;''')
    projs = [r for r in dict_gen(cur)]
    
    cur = g.db.execute('''
          SELECT name, department 
            FROM clients 
        ORDER BY id DESC;''')
    clients = [r for r in dict_gen(cur)]
    
    return render_template('index.html', clients=clients, projs=projs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        user = query_db('''SELECT * 
                                 FROM users 
                                WHERE username = ?;''', 
                                [request.form['username']], one=True)
        if user is None:
            error = 'invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'invalid password'
        else:
            flash('you were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    ''' register the user '''
    if g.user:
        flash('you are already logged in')
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'please enter a username'
        elif not request.form['password']:
            error = 'please enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'passwords must match'
        elif get_user_id(request.form['username']) is not None:
            error = 'username already taken'
        else:
            g.db.execute('''INSERT INTO users (
                username, email, pw_hash) VALUES (?,?,?)''', 
                [request.form['username'], request.form['email'], 
                generate_password_hash(request.form['password'])]
            )
            g.db.commit()
            flash('registration successful. you may now log in.')
            return redirect(url_for('login')) # s/b 'login' instead of '/'
    return render_template('register.html', error=error)
    #error = None
    #return render_template('register.html', error=error)

if __name__ == "__main__":
    app.run()
