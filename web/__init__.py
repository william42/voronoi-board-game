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

from flask import Flask, g
from flask_sockets import Sockets
import click

from web import database
from web.voro import app as blueprint
from web.voro import sockets as voro_sockets

def create_app():
    app = Flask(__name__)

    app.config.from_object('web.default_settings')
    try:
        app.config.from_envvar('VORO_SETTINGS')
    except RuntimeError as e:
        app.logger.warning('Error in custom configuration: %s', e) 

    app.register_blueprint(blueprint, cli_group=None)

    if 'LOGIN_SYSTEM' not in app.config:
        # TODO: decide on whether to do a default login system
        raise RuntimeError('LOGIN_SYSTEM not defined.')
    else:
        app.register_blueprint(app.config['LOGIN_SYSTEM'])

    app.logger.setLevel('INFO')

    return app