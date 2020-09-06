/**
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var game_status = {};
var protocol = location.protocol == 'http:' ? 'ws:' : 'wss:';
var sock = new WebSocket(protocol + location.host + location.pathname);

function set_status(new_status) {
    old_status = game_status;
    var board_holder = document.getElementById('board-holder');
    var status_holder = document.getElementById('status-holder');
    if ('to_move' in old_status) {
        var css_class = 'voro-holder-'+old_status.to_move;
        board_holder.classList.remove(css_class);
        status_holder.classList.remove(css_class);
    }
    if ('to_move' in new_status) {
        var css_class = 'voro-holder-'+new_status.to_move;
        board_holder.classList.add(css_class);
        status_holder.classList.add(css_class);
    }
    if ('moves_left' in new_status) {
        document.getElementById('moves-left-counter').textContent = new_status.moves_left;
    }
    if ('connections_remaining' in new_status) {
        status_holder.classList.add('voro-border-filled');
        document.getElementById('connections-remaining-counter').textContent = new_status.connections_remaining;
    } else {
        status_holder.classList.remove('voro-border-filled');
    }
    if ('game_complete' in new_status && new_status.game_complete) {
        status_holder.classList.add('voro-game-complete');
        document.getElementById('score-holder').classList.add('voro-game-complete');
        document.getElementById('score-1-counter').textContent = new_status.score_1;
        document.getElementById('score-2-counter').textContent = new_status.score_2;
    }
    game_status = new_status;
}

sock.onmessage = function(event) {
    data = JSON.parse(event.data);
    console.log(data)
    if (data.action === 'PLAY_TOKEN') {
        var token_id = data.location;
        var cell = document.getElementById('cell-' + token_id);
        cell.classList.add('voro-token-' + data.color)
        cell.classList.add('voro-cell-clicked');
    }
    if (data.action === 'NEW_GAME_STATUS') {
        set_status(data.status);
        //TODO: interface to show game status
    }
};

sock.onclose = function(event) {
    document.getElementById('websocket-closed').classList.remove('voro-hide');
}

function send_json(message) {
    raw_message = JSON.stringify(message);
    sock.send(raw_message);
}

var cells = document.getElementsByClassName('voro-cell');
for (var cell of cells) {
    cell.addEventListener('click', function() {
        var color = game_status.to_move;
        send_json({
            action: 'PLAY_TOKEN',
            location: this.dataset.num,
            color: color,
        });
        console.log(this)
    });
}
