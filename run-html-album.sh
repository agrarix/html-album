#!/bin/bash
# ==============================================================================
# run-html-album.sh
# Webhook runner voor html-album op fabrix
# ==============================================================================

set -u

export HOME="/home/maarten"
export USER="maarten"
export PATH="/home/maarten/bin:/home/maarten/scripts:/usr/local/bin:/usr/bin:/bin:$PATH"

SCRIPT="/home/maarten/scripts/html-album.py"
LOGDIR="/home/maarten/log"
LOGFILE="${LOGDIR}/html-album-webhook.log"
LOCKFILE="/tmp/html-album.lock"

mkdir -p "$LOGDIR"

CONFIG="${1:-html-album.rc}"
if [ -z "$CONFIG" ]; then
    CONFIG="html-album.rc"
fi

ALL_FLAG="${2:-0}"
ASYNC_FLAG="${3:-0}"

# Indien directe optie (-V, -h, --help) meegegeven:
if [[ "$CONFIG" == -* ]]; then
    /usr/bin/python3 "$SCRIPT" "$CONFIG"
    exit $?
fi

EXTRA_ARGS=""
if [ "$ALL_FLAG" = "1" ] || [ "$ALL_FLAG" = "true" ] || [ "$ALL_FLAG" = "yes" ]; then
    EXTRA_ARGS="--all"
fi

run_album() {
    exec 200>"$LOCKFILE"
    if ! flock -n 200; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] html-album is al actief! Een andere taak draait momenteel." | tee -a "$LOGFILE"
        return 1
    fi

    echo "==============================================================================" | tee -a "$LOGFILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Start html-album via webhook" | tee -a "$LOGFILE"
    echo "Host       : $(hostname)" | tee -a "$LOGFILE"
    echo "Gebruiker  : $(whoami)" | tee -a "$LOGFILE"
    echo "Config     : ${CONFIG}" | tee -a "$LOGFILE"
    if [ -n "$EXTRA_ARGS" ]; then
        echo "Opties     : ${EXTRA_ARGS}" | tee -a "$LOGFILE"
    fi
    echo "==============================================================================" | tee -a "$LOGFILE"

    cd /home/maarten
    /usr/bin/python3 "$SCRIPT" "$CONFIG" $EXTRA_ARGS 2>&1 | tee -a "$LOGFILE"
    EXIT_CODE=${PIPESTATUS[0]}

    echo "------------------------------------------------------------------------------" | tee -a "$LOGFILE"
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] html-album succesvol afgerond (code 0)" | tee -a "$LOGFILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [FOUT] html-album geëindigd met foutcode ${EXIT_CODE}" | tee -a "$LOGFILE"
    fi
    echo "==============================================================================" | tee -a "$LOGFILE"
    return $EXIT_CODE
}

if [ "$ASYNC_FLAG" = "1" ] || [ "$ASYNC_FLAG" = "true" ] || [ "$ASYNC_FLAG" = "yes" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] html-album gestart in achtergrond met config '${CONFIG}'."
    echo "Uitvoer wordt gelogd naar ${LOGFILE}."
    ( run_album ) >/dev/null 2>&1 &
    exit 0
else
    run_album
    exit $?
fi