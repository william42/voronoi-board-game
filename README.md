# Voronoi board game

This repository consists of the code for a Flask app running a game based on Ea Ea's game *Star, as well as a builder for game boards, based on the Centroidal Voronoi Tesselation.

This is not an officially supported Google project.

## How to use

Before using, you'll need the dependencies. Running `source activate-venv.sh` will create a virtualenv and install the package for you.

### builder

The code in the `builder` directory creates the actual game boards.

After using `source activate-venv.sh` to create the virtualenv and install the package, use `vorobuilder [OPTIONS] filename` to generate boards usable for `flask addboard` below.  The example below uses `board.json` as the filename.

### web

The code in the `web` directory uses the Flask CLI.

```
source activate-venv.sh
flask initdb # Creates the database, wiping out anything previously there.
flask addboard "--name=My board" board.json
flask runws # Runs the WebSocket and HTTP server.
```

## Warning

This is very much a work-in-progress.  In particular:

* The login/account system is currently limited to the "null" account system which has (by design) no security.
* The rules are unexplained.
* The protocol is incredibly flimsy, and probably vulnerable to cross-site hijacking.