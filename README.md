# Voronoi board game

This repository consists of the code for a Flask app running a game based on Ea Ea's game *Star, as well as a builder for game boards, based on the Centroidal Voronoi Tesselation.

This is not an officially supported Google project.

## How to use

Before using, you'll need the dependencies. (TODO: actually run through the code and list them in requirements.txt files)

### builder

The code in the `builder` directory creates the actual game boards.

Simply run

### web

The code in the `web` directory uses the Flask CLI.

```
source activate-venv.sh
flask initdb # Creates the database, wiping out anything previously there.
flask addboard board.json
flask runws # Runs the WebSocket and HTTP server.
```

## Warning

This is very much a work-in-progress.  In particular:

* There's no login/account system.
* The rules are unexplained.
* The protocol is incredibly flimsy, and probably vulnerable to cross-site hijacking.