# Do not edit this script. Edit configuration.py
import sys
import requests
from datetime import datetime, timezone, date, timedelta
from influxdb import InfluxDBClient
import argparse
from argparse import RawTextHelpFormatter
import configuration


def now_iso():
    now_iso = datetime.now(timezone.utc).astimezone().isoformat()
    return now_iso


def influx_sender(influx_payload):
    influx = InfluxDBClient(configuration.influxdb_url, configuration.influxdb_port, configuration.influxdb_username,
                            configuration.influxdb_password, configuration.sonarr_influxdb_db_name)
    influx.write_points(influx_payload)


def get_all_missing_shows():
    # Set the time here so we have one timestamp to work with
    now = now_iso()

    missing = []

    influx_payload = []

    for sonarr_url, sonarr_api_key, server_id in configuration.sonarr_server_list:

        headers = {'X-Api-Key': sonarr_api_key}

        get_tv_shows = requests.get('{}/api/wanted/missing/?pageSize=1000'.format(sonarr_url),
                                    headers=headers).json()['records']

        tv_shows = {d['id']: d for d in get_tv_shows}


        for show in tv_shows.keys():
            series_title = '{}'.format(tv_shows[show]['series']['title'])
            sxe = 'S{:0>2}E{:0>2}'.format(tv_shows[show]['seasonNumber'],tv_shows[show]['episodeNumber'])
            missing.append((series_title, sxe, tv_shows[show]['id'], tv_shows[show]['title']))

        for series_title, sxe, id, episode_title in missing:
            influx_payload.append(
                {
                    "measurement": "sonarr_missing",
                    "tags": {
                        "type": "missing",
                        "sonarrId": id,
                        "server": server_id
                    },
                    "time": now,
                    "fields": {
                        "name": series_title,
                        "epname": episode_title,
                        "sxe": sxe
                    }
                }
            )
        # Empty missing or else things get foo bared
        missing = []

    return influx_payload


def get_missing_shows(days_past):
    # Set the time here so we have one timestamp to work with
    now = now_iso()

    last_days = str(date.today()+timedelta(days=-days_past))

    today = str(date.today())

    missing = []

    influx_payload = []

    for sonarr_url, sonarr_api_key, server_id in configuration.sonarr_server_list:

        headers = {'X-Api-Key': sonarr_api_key}

        get_tv_shows = requests.get('{}/api/calendar/?start={}&end={}&pageSize=1000'.format(sonarr_url, last_days, today),
                                    headers=headers).json()

        tv_shows = {d['id']: d for d in get_tv_shows}

        for show in tv_shows.keys():
            if not (tv_shows[show]['hasFile']):
                series_title = '{}'.format(tv_shows[show]['series']['title'])
                sxe = 'S{:0>2}E{:0>2}'.format(tv_shows[show]['seasonNumber'], tv_shows[show]['episodeNumber'])
                air_date = (tv_shows[show]['airDate'])
                missing.append((series_title, sxe, air_date, tv_shows[show]['id']))

        for series_title, sxe, air_date, id in missing:
            influx_payload.append(
                {
                    "measurement": "sonarr_missing_days",
                    "tags": {
                        "type": "missing_days",
                        "sonarrId": id,
                        "server": server_id
                    },
                    "time": now,
                    "fields": {
                        "name": series_title,
                        "sxe": sxe,
                        "airs": air_date
                    }
                }
            )

        # Empty missing or else things get foo bared
        missing = []

    return influx_payload


def get_upcoming_shows():
    # Set the time here so we have one timestamp to work with
    now = now_iso()

    upcoming = []

    influx_payload = []

    for sonarr_url, sonarr_api_key, server_id in configuration.sonarr_server_list:

        headers = {'X-Api-Key': sonarr_api_key}

        get_upcoming_shows = requests.get('{}/api/calendar/'.format(sonarr_url),
                                          headers=headers).json()

        upcoming_shows = {d['id']: d for d in get_upcoming_shows}

        for show in upcoming_shows.keys():
            series_title = '{}'.format(upcoming_shows[show]['series']['title'])
            sxe = 'S{:0>2}E{:0>2}'.format(upcoming_shows[show]['seasonNumber'],upcoming_shows[show]['episodeNumber'])
            upcoming.append((series_title, sxe, upcoming_shows[show]['id'], upcoming_shows[show]['title'], upcoming_shows[show]['airDate']))

        for series_title, sxe, id, episode_title, air_date  in upcoming:
            influx_payload.append(
                {
                    "measurement": "sonarr_soon",
                    "tags": {
                         "type": "soon",
                         "sonarrId": id,
                         "server": server_id
                     },
                     "time": now,
                     "fields": {
                         "name": series_title,
                         "epname": episode_title,
                         "sxe": sxe,
                         "airs": air_date
                     }
                 }
            )
        # Empty upcoming or else things get foo bared
        upcoming = []

    return influx_payload


def get_future_shows(future_days):
    # Set the time here so we have one timestamp to work with
    now = now_iso()

    today = str(date.today())

    future = str(date.today()+timedelta(days=future_days))

    air_days = []

    downloaded = []

    influx_payload = []

    for sonarr_url, sonarr_api_key, server_id in configuration.sonarr_server_list:

        headers = {'X-Api-Key': sonarr_api_key}

        get_tv_shows = requests.get('{}/api/calendar/?start={}&end={}&pageSize=200'.format(sonarr_url, today, future),
                                    headers=headers).json()

        tv_shows = {d['id']: d for d in get_tv_shows}

        for show in tv_shows.keys():
            series_title = '{}'.format(tv_shows[show]['series']['title'])
            dl_status = int(tv_shows[show]['hasFile'])
            sxe = 'S{:0>2}E{:0>2}'.format(tv_shows[show]['seasonNumber'], tv_shows[show]['episodeNumber'])
            air_days.append((series_title, dl_status, sxe, tv_shows[show]['title'], tv_shows[show]['airDate'], tv_shows[show]['id']))

        for series_title, dl_status, sxe, episode_title, air_date, id in air_days:
            influx_payload.append(
                {
                    "measurement": "sonarr_future",
                    "tags": {
                        "type": "future",
                        "sonarrId": id,
                        "server": server_id
                    },
                    "time": now,
                    "fields": {
                        "name": series_title,
                        "epname": episode_title,
                        "sxe": sxe,
                        "airs": air_date,
                        "downloaded": dl_status
                    }
                }
            )
        # Empty air_days or else things get foo bared
        air_days = []

    return influx_payload


def get_queue_shows():
    # Set the time here so we have one timestamp to work with
    now = now_iso()

    queue = []

    downloaded = []

    influx_payload = []

    for sonarr_url, sonarr_api_key, server_id in configuration.sonarr_server_list:

        headers = {'X-Api-Key': sonarr_api_key}

        get_tv_shows = requests.get('{}/api/queue'.format(sonarr_url),
                                    headers=headers).json()

        tv_shows = {d['id']: d for d in get_tv_shows}

        for show in tv_shows.keys():
            series_title = '{}'.format(tv_shows[show]['series']['title'])
            episode_title = '{}'.format(tv_shows[show]['episode']['title'])
            protocol =  (tv_shows[show]['protocol'].upper())
            sxe = 'S{:0>2}E{:0>2}'.format(tv_shows[show]['episode']['seasonNumber'], tv_shows[show]['episode']['episodeNumber'])
            if protocol == 'USENET':
                protocol_id = 1
            else:
                protocol_id = 0

            queue.append((series_title, episode_title, protocol, protocol_id, sxe, tv_shows[show]['id']))

        for series_title, episode_title, protocol, protocol_id, sxe, id in queue:
            influx_payload.append(
                {
                    "measurement": "sonarr_queue",
                    "tags": {
                        "type": "queue",
                        "sonarrId": id,
                        "server": server_id

                    },
                    "time": now,
                    "fields": {
                        "name": series_title,
                        "epname": episode_title,
                        "sxe": sxe,
                        "protocol": protocol,
                        "protocol_id": protocol_id
                    }
                }
            )

        # Empty queue or else things get foo bared
        queue = []

    return influx_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Sonarr stats operations',
        description='Script to aid in data gathering from Sonarr', formatter_class=RawTextHelpFormatter)

    parser.add_argument("--missing",  action='store_true',
        help='Get all missing TV shows')

    parser.add_argument("--missing_days", type=int,
        help='Get missing TV shows in past X days')

    parser.add_argument("--upcoming", action='store_true',
        help='Get upcoming TV shows')

    parser.add_argument("--future", type=int,
        help='Get TV shows on X days into the future. Includes today.'
            '\ni.e. --future 2 is Today and Tomorrow')

    parser.add_argument("--queue", action='store_true',
        help='Get TV shows in queue')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    opts = parser.parse_args()

    if opts.missing:
        influx_sender(get_all_missing_shows())

    if opts.missing_days:
        influx_sender(get_missing_shows(opts.missing_days))

    if opts.upcoming:
        influx_sender(get_upcoming_shows())

    if opts.future:
        influx_sender(get_future_shows(opts.future))

    if opts.queue:
        influx_sender(get_queue_shows())
