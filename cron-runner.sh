#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && DIR )"

command python3 $DIR/sonarr.py --missing --upcoming --queue
command python3 $DIR/radarr.py --missing_avl --queue
command python3 $DIR/ombi.py --total --counts
command python3 $DIR/tautulli.py

sleep 30

command python3 $DIR/sonarr.py --missing --upcoming --queue
command python3 $DIR/radarr.py --missing_avl --queue
command python3 $DIR/ombi.py --total --counts
command python3 $DIR/tautulli.py