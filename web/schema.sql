DROP TABLE IF EXISTS boards;
CREATE TABLE boards (
    board_id INTEGER PRIMARY KEY,
    board_name TEXT,
    board_json TEXT
);

DROP TABLE IF EXISTS games;
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY,
    game_name TEXT,
    board_id INTEGER, -- foreign key to boards?
    game_status_json TEXT
);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens (
    token_id INTEGER PRIMARY KEY,
    game_id INTEGER, -- foreign
    player INTEGER, -- 1 or 2
    location INTEGER,
    placed_on DATETIME DEFAULT CURRENT_TIMESTAMP
);