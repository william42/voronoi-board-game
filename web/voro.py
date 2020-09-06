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

import sqlite3
import flask
from flask import Flask, render_template, g, request, redirect, url_for
from flask_sockets import Sockets
import click
import numpy as np
import io
import json
import os
from unionfind import UnionFind

#getting a lot of false positives on app.logger
#pylint: disable=no-member

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'voro.db'),
))

sockets = Sockets(app)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.cli.command('initdb')
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    app.logger.info('Database initialized.')

@app.cli.command('addboard')
@click.option('--name', type=str, default=None, help='Name to give the board')
@click.argument('file', type=click.File('r'))
def add_board(name, file):
    board = json.load(file)
    if name is None:
        name = file.name
    db = get_db()
    db.execute("""INSERT INTO boards
        (board_name, board_json)
        VALUES (?,?)""", [name, json.dumps(board)])
    db.commit()
    app.logger.info("Board added!")

def layout_board(id):
    db = get_db()
    cursor = db.execute("""SELECT board_name, board_json
        FROM boards
        WHERE board_id=?
        LIMIT 1""", [id])
    board_info = cursor.fetchone()
    board = json.loads(board_info['board_json'])
    # with open('board.json', 'r') as f:
    #     board = json.load(f)
    trueboard = np.array(board['tokens'])
    edges = board['edges']

    def edge(i, j):
        p1 = trueboard[i]
        p2 = trueboard[j]
        return {
            'x1': p1[0]+22,
            'y1': p1[1]+22,
            'x2': p2[0]+22,
            'y2': p2[1]+22,
        }

    def cell(i):
        p = trueboard[i]
        return {
            'num': i,
            'x': p[0]+22,
            'y': p[1]+22,
        }
    
    return {
        'board_id': id,
        'board_name': board_info['board_name'],
        'edges': [edge(i, j) for (i, j) in edges],
        'cells': [cell(i) for i in range(len(trueboard))],
        'radius': min(np.linalg.norm(trueboard[i]-trueboard[j])
                      for (i, j) in edges) * 0.45,
    }

@app.route('/boards/<id>')
def view_board(id):
    board = layout_board(id)
    return render_template('board.html', **board)
    
def get_game_status(id):
    db = get_db()
    raw_status = db.execute("""SELECT game_status_json
        FROM games
        WHERE game_id=?""", (id,)).fetchone()['game_status_json']
    return json.loads(raw_status)

def set_game_status(id, status, commit=True):
    db = get_db()
    raw_status = json.dumps(status)
    db.execute("""UPDATE games
        SET game_status_json=?
        WHERE game_id=?""", (raw_status,id))
    if commit:
        db.commit()

@app.route('/games/new', methods=['POST'])
def new_game():
    game_name = request.form['game_name']
    board_id = int(request.form['board_id'])
    default_status = json.dumps({
        'to_move': 1,
        'moves_left': 1,
    })
    db = get_db()
    cur = db.execute("""INSERT INTO games
        (game_name, board_id, game_status_json)
        VALUES (?,?,?)""",
        (game_name, board_id, default_status))
    game_id = cur.lastrowid
    db.commit()
    return redirect(url_for('view_game',id=game_id))

@app.route('/games/<int:id>')
def view_game(id):
    db = get_db()
    cur = db.execute("""SELECT game_name, board_id, game_status_json
        FROM games
        WHERE game_id=?""",(id,))
    game_info = cur.fetchone()
    board_id = game_info['board_id']
    board = layout_board(board_id)
    board['game_name'] = game_info['game_name']
    cur = db.execute("""SELECT location, player
        FROM tokens
        WHERE game_id=?""",(id,))
    for row in cur:
        location = int(row['location'])
        player = int(row['player'])
        board['cells'][location]['color'] = player
    return render_template('game.html',
        game_status_json=game_info['game_status_json'],
        **board)

@app.route('/')
def home():
    db = get_db()
    boards = db.execute("""SELECT board_id, board_name
        FROM boards""").fetchall()
    games = db.execute("""SELECT game_id, game_name
        FROM games""").fetchall()
    return render_template('board_list.html', boards=boards, games=games)

def broadcast(ws, game_id, message):
    # TODO: understand this, maybe use something less hacky?
    clients = ws.handler.server.clients.values()
    for client in clients:
        if client.game_id != game_id: continue
        client.ws.send(json.dumps(message))

def check_game(game_id, game_status):
    db = get_db()

    cur = db.execute("""SELECT b.board_json
        FROM boards AS b
        JOIN games AS g
            ON b.board_id = g.board_id
        WHERE g.game_id=?""", (game_id,))
    board_info = cur.fetchone()
    board = json.loads(board_info['board_json'])

    num_cells = len(board['tokens'])
    edges = board['edges']
    num_border = board['num_border']

    cells = [None for i in range(num_cells)]
    cur = db.execute("""SELECT location, player
        FROM tokens
        WHERE game_id=?""", (game_id,))
    for row in cur:
        cells[row['location']] = row['player']
    
    for i in range(num_border):
        if cells[i] is None:
            app.logger.info('Border not full')
            game_status['border_full'] = False
            return
    app.logger.info('Border full.')
    game_status['border_full'] = True
    uf = UnionFind(num_cells)
    for i in range(num_border):
        uf.custom_weights[i]=1
    for (i,j) in edges:
        if i>=num_border or j>=num_border:
            continue
        if cells[i] != cells[j]:
            continue
        uf.merge(i,j)
    num_outer_groups = len(uf.positive_weight_groups()) / 2
    for (i,j) in edges:
        if cells[i] != cells[j] or cells[i] is None:
            continue
        uf.merge(i,j)
    remaining_connections = len(uf.positive_weight_groups()) - num_outer_groups - 1
    game_status['connections_remaining'] = remaining_connections
    if remaining_connections > 0:
        return
    game_status['game_complete'] = True
    scores = [0, 0]
    for cell, weight in uf.positive_weight_groups():
        player = 0 if cells[cell] == 1 else 1
        if weight > 1:
            scores[player] += weight - 4
        else:
            scores[1 - player] += 1
    game_status['score_1'], game_status['score_2'] = scores
    app.logger.info('Score: %s', scores)

    

def play_token(ws, game_id, location, color):
    db = get_db()
    game_status = get_game_status(game_id)
    if game_status['to_move'] != color:
        return
    cur = db.execute("""SELECT 1 FROM tokens
        WHERE game_id = ?
            AND location = ?""", (game_id, location))
    if len(cur.fetchall()) > 0:
        return
    game_status['moves_left'] -= 1
    if game_status['moves_left'] == 0:
        game_status['to_move'] = 2 if game_status['to_move'] == 1 else 1
        game_status['moves_left'] = 2
    db.execute("""INSERT INTO tokens
        (game_id, player, location)
        VALUES (?,?,?)""", (game_id, color, location))
    check_game(game_id, game_status)
    set_game_status(game_id, game_status, False)
    db.commit()
    message = {
        'action': 'PLAY_TOKEN',
        'location': location,
        'color': color,
    }
    broadcast(ws, game_id, message)
    message = {
        'action': 'NEW_GAME_STATUS',
        'status': game_status
    }
    broadcast(ws, game_id, message)

@sockets.route('/games/<int:id>')
def game_socket(ws, id):
    client_address = ws.handler.client_address
    server = ws.handler.server
    client = server.clients[client_address]
    client.game_id = id
    app.logger.info('Opening socket at %s for game %d', client_address, id)
    while not ws.closed:
        try:
            raw_message = ws.receive()
            if raw_message is None:
                app.logger.info('None message received and ignored...')
                continue
            message = json.loads(raw_message)
            if message['action'] == 'PLAY_TOKEN':
                location = int(message['location'])
                color = int(message['color'])
                play_token(ws, id, location, color)
            else:
                app.logger.warning('Unknown message %s', message)
        except Exception as e:
            app.logger.exception('Error in websocket', e)
            app.logger.warning('Raw message was: %s', raw_message)
    app.logger.info('Closing socket...')
        

@app.cli.command('runws')
@click.option('--port', default=5000, help='Port to run websocket/HTTP server on.')
def run_ws(port):
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    app.logger.setLevel('INFO')
    server = pywsgi.WSGIServer(('', port), app, handler_class=WebSocketHandler)
    server.serve_forever()