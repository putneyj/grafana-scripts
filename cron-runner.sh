#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"

command python3 $DIR/sonarr.py --missing --upcoming --queue
command python3 $DIR/radarr.py --missing_avl --queue
command python3 $DIR/ombi.py --total --counts
command python3 $DIR/tautulli.py

sleep 30

command python3 $DIR/sonarr.py --missing --upcoming --queue
command python3 $DIR/radarr.py --missing_avl --queue
command python3 $DIR/ombi.py --total --counts
command python3 $DIR/tautulli.py