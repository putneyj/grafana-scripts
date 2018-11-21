#!/bin/bash

command python3 $PWD/sonarr.py --missing --upcoming --queue
command python3 $PWD/radarr.py --missing_avl --queue
command python3 $PWD/ombi.py --total --counts
command python3 $PWD/tautulli.py
