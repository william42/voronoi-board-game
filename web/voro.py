import sqlite3
import flask
from flask import Flask, render_template, g, request, redirect, url_for
from flask_sockets import Sockets
import click
import numpy as np
import io
import json
import os

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
@click.argument('filename')
def add_board(filename):
    with open(filename, 'r') as f:
        board = json.load(f)
    db = get_db()
    db.execute("""INSERT INTO boards
        (board_name, board_json)
        VALUES (?,?)""", [filename, json.dumps(board)])
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

@app.route('/games/new', methods=['POST'])
def new_game():
    game_name = request.form['game_name']
    board_id = int(request.form['board_id'])
    default_status = json.dumps({})
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
    #TODO: everything
    db = get_db()
    cur = db.execute("""SELECT game_name, board_id
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
    return render_template('game.html', **board)

@app.route('/')
def home():
    db = get_db()
    cursor = db.execute("""SELECT board_id, board_name
        FROM boards""")
    boards = cursor.fetchall()
    return render_template('board_list.html', boards=boards)

def broadcast(ws, game_id, message):
    # TODO: understand this, maybe use something less hacky?
    clients = ws.handler.server.clients.values()
    for client in clients:
        if client.game_id != game_id: continue
        client.ws.send(json.dumps(message))

def play_token(ws, game_id, location, color):
    db = get_db()
    db.execute("""INSERT INTO tokens
        (game_id, player, location)
        VALUES (?,?,?)""", (game_id, color, location))
    db.commit()
    message = {
        'action': 'PLAY_TOKEN',
        'location': location,
        'color': color,
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
            app.logger.warning('Error: %s', e)
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