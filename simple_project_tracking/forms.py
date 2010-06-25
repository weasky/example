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

from wtforms import (Form, SelectField, DateTimeField, 
                    TextField, validators)

class ProjectCreateForm(Form):
    ''' Generates flexible form boilerplate not tied to a schema.
    
        WTForms support static or dynamic form fields; 
        dynamic fields get populated in view code.
    '''
    title = TextField('Project Title', 
        [validators.Length(min=4, max=25)])
    description = TextField('Project Description', 
        [validators.Length(min=6, max=35)])
    # so that 
    name = TextField('Client Name', 
        [validators.optional(), validators.Length(min=4, max=25)])
    department = TextField('Client Department', 
        [validators.optional(), validators.Length(min=6, max=35)])
    # from http://wtforms.simplecodes.com/docs/0.5/fields.html
    # Note we didn’t pass a choices to the SelectField constructor, 
    # but rather created the list in the view function. 
    # Also, the coerce keyword arg to SelectField says that we use int() 
    # to coerce form data. The default coerce is unicode().
    client_id = SelectField(u'Client', coerce=int)


class ClientCreateForm(Form):
    name = TextField('Client Name', 
        [validators.Length(min=4, max=25)])
    department = TextField('Client Department', 
        [validators.Length(min=6, max=35)])


class ClientEditForm(Form):
    name = TextField('Client Name', 
        [validators.Length(min=4, max=25)])
    department = TextField('Client Department', 
        [validators.Length(min=6, max=35)])

