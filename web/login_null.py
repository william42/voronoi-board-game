# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Blueprint, render_template, redirect, url_for, request, session, current_app, g

from web import models
from web.database import db_session

blueprint = Blueprint('login_null', __name__,
                      template_folder='templates')

@blueprint.route('/login', methods=['POST','GET'])
def login():
    current_app.logger.info('session: %s', session)
    if request.method=='POST':
        username = request.form['username']
        user = db_session.query(models.User).filter_by(username=username).first()
        if user is None:
            return 'User does not exist'
        session['user_id'] = user.user_id
    elif 'user_id' in session:
        user = db_session.query(models.User).filter_by(user_id=session['user_id']).first()
    else:
        user = None
    return render_template('login_null.html',
         user=user)

@blueprint.route('/signup', methods=['POST'])
def signup():
    #TODO: more informative errors (or not, for this is for testing)
    if 'username' not in request.form:
        return 'No username entered'
    username = request.form['username']
    if db_session.query(models.User).filter_by(username=username).count() > 0:
        return 'User already exists'
    new_user = models.User(username=username)
    db_session.add(new_user)
    db_session.commit()
    return redirect(url_for('login_null.login'))