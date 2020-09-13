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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()

class Board(Base):
    __tablename__ = 'boards'

    board_id=Column(Integer, primary_key=True)
    board_name=Column(String)
    board_json=Column(String)

class Game(Base):
    __tablename__ = 'games'

    game_id=Column(Integer, primary_key=True)
    game_name=Column(String)
    board_id=Column(Integer, ForeignKey('boards.board_id'))
    game_status_json=Column(String)

    board=relationship("Board", back_populates="games")

Board.games=relationship("Game", order_by=Game.game_id, back_populates="board")

class Token(Base):
    __tablename__ = 'tokens'

    token_id=Column(Integer, primary_key=True)
    game_id=Column(Integer, ForeignKey('games.game_id'))
    player=Column(Integer) # TODO: enum 1 or 2
    location=Column(Integer)
    placed_on=Column(DateTime(timezone=True), default=func.now())

    game=relationship("Game", back_populates="tokens")

Game.tokens=relationship("Token", order_by=Token.location, back_populates='game')