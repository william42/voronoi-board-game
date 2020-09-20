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

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from flask import current_app, g
from werkzeug.local import LocalProxy

from web import models


def setup():
    database_url = current_app.config['ALCHEMY_DATABASE']
    g.engine = create_engine(database_url)
    g.db_session = sessionmaker(autocommit=False,autoflush=False,bind=g.engine)()
    # models.Base.query = g.db_session.query_property()

def get_db_session():
    if 'db_session' not in g:
        setup()
    return g.db_session

db_session = LocalProxy(get_db_session)

def init(engine):
    models.Base.metadata.create_all(bind=engine)
