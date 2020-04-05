#!/usr/bin/env python3

import argparse
import calendar
import datetime
import glob
import json
import math
import random as rand

import os
import subprocess
import sys

def stop_server(args):
    try:
        subprocess.check_call([os.path.join(args.server_root, 'rustserver'), 'stop'])
    except subprocess.CalledProcessError as cpe:
        if cpe.returncode == 2:
            print('WARNING: Stop server failed. This could be because the server is '
                  'already running! Ignoring, but take caution if this is unexpected')
        else:
            raise cpe


def start_server(args):
    # This shouldn't fail... hopefully
    subprocess.check_call([os.path.join(args.server_root, 'rustserver'), 'start'])


def _dry_run_func(the_thing, would_have="removed"):
    print('[DRY]: Would have {}: {}'.format(would_have, the_thing))


def remove_and_log(the_file):
    os.remove(the_file)
    print('Removed {}'.format(the_file))


def wipe_serverfiles(serverfiles_path):
    '''
    Just a quick note: a lot of this is covered with LGSM's wipe commands
    Probably, in the future, I will use those commands in this script but
    for now, this works for me and I'm not fixing it until I find a reason
    to fix it (other than, maybe LGSM doing a better job than me tracking
    the necessary changes).
    '''

    remove_func = _dry_run_func if args.dry_run else remove_and_log

    db_files = glob.glob(os.path.join(serverfiles_path, '*.db'))
    for db_file in db_files:
        if 'blueprints' in db_file:
            if not args.bps:
                print ('Skipping {} because it is a blueprint file!')
                continue
        remove_func(db_file)

    sav_files = glob.glob(os.path.join(serverfiles_path, '*.sav'))
    for sav_file in sav_files:
        remove_func(sav_file)

    map_files = glob.glob(os.path.join(serverfiles_path, '*.map'))
    for map_file in map_files:
        remove_func(map_file)

    #print(db_files)

def set_server_seed(args, lgsm_data_path):
    if args.seed is None:
        print('Server seed should not be None')
        raise('unexpected None seed')

    seed_file_name = os.path.join(lgsm_data_path, 'rustserver-seed.txt')

    if args.dry_run:
        print('Dry run, seed not actually set')
    else:
        with open(seed_file_name, 'w') as seed_file:
            seed_file.write(f'{args.seed}')


def wipe_oxide_data(oxide_path):
    remove_func = _dry_run_func if args.dry_run else remove_and_log

    # This is a /very/ minimalistic list of data files to wipe.
    # This should probably be moved to a config file in the future...
    oxide_data_files_to_wipe = [
        'Kits_Data.json',
        'LoyaltyData.json',
        'NTeleportationAdmin.json',
        'NTeleportationBandit.json',
        'NTeleportationBandit.json',
        'NTeleportationDisabledCommands.json',
        'NTeleportationHome.json',
        'NTeleportationOutpost.json',
        'NTeleportationTown.json',
        'NTeleportationTPR.json',
        'NTeleportationTPT.json',
        ]

    oxide_data_path_glob = os.path.join(oxide_path, '*')
    oxide_data_files = glob.glob(oxide_data_path_glob)
    print('Inspecting oxide files: {}'.format(', '.join(oxide_data_files)))

    for oxide_data_file in oxide_data_files:
        if os.path.basename(oxide_data_file) in oxide_data_files_to_wipe:
            print('inspecting {}'.format(oxide_data_file))
            remove_func(oxide_data_file)


def set_oxide_config(args, oxide_config_path):
    print('Set oxide config NOT implemented...')

    if args.dry_run:
        print('Dry run, not setting oxide config')
        return


def get_seed_from_args(args):
    if args.seed is None:
        print('seed was None when expected real value')
    return f'server.seed {args.seed}'


def server_cfg_wipe(args, server_cfg_path):
    cfg_file = os.path.join(server_cfg_path, 'server.cfg')

    seed = args.seed
    if args.random_seed or seed is None:
        import random as rand
        seed = rand.randint(1, (2**31 + 1))
        print(f'Using random seed: {seed}') 

    date = datetime.date.today()
    wipe_month = date.month
    wipe_day = date.day

    # Being a clean construction of fields that can be properly formatted later
    server_name_fields = []

    server_name_fields.append(args.server_name)
    if args.flavor not in [None, ""]:
        server_name_fields.append(args.flavor)
    if args.location not in [None, ""]:
        server_name_fields.append(args.location)

    server_name = ' | '.join(server_name_fields)

    server_tags = []
    if args.weekly:
        server_tags.append('weekly')
    if args.bi_weekly:
        server_tags.append('biweekly')
    if args.monthly:
        server_tags.append('monthly')
    if args.vanilla:
        server_tags.append('vanilla')
    if args.pve:
        server_tags.append('pve')
    if args.roleplay:
        server_tags.append('roleplay')
    if args.creative:
        server_tags.append('creative')
    if args.softcore:
        server_tags.append('softcore')
    if args.minigame:
        server_tags.append('minigame')
    if args.training:
        server_tags.append('training')
    if args.battlefield:
        server_tags.append('battlefield')
    if args.broyale:
        server_tags.append('broyale')
    if args.build:
        server_tags.append('build')

    description = ""
    if args.description not in [None, ""]:
        description = args.description
    elif args.description_file not in [None, ""]:
        with open(args.description_file, 'r') as dfile:
            description_lines = [x.strip() for x in dfile.readlines()]
            description = '\\n'.join(description_lines)

    servercfg = f'''
# Rust server settings
server.hostname "{server_name}"
server.maxplayers {args.max_players}
server.headerimage "{args.image_url}"
server.url "{args.server_url}"
server.description "{description}"
server.tags "{",".join(server_tags)}"
server.official {args.official}

# Server map variables
server.level "Procedural Map"
server.worldsize {args.size}
{get_seed_from_args(args)}

# Server intervals
server.saveinterval 300

# Server environment settings
server.radiation True
decay.scale 1

# Probably obsolete settings
server.secure True # VAC
antihack.enabled True # EAC

# Chat settings
server.globalchat True
chat.enabled True
server.stability True

# Server
server.pve False
server.eac 1

# Heli settings
heli.guns 1 # 0 for rockets only
heli.bulletdamagescale 1 # default 1
heli.bulletaccuracy 2 # default 2
'''

    if not args.dry_run:
        with open(cfg_file, 'w') as cfg:
            cfg.write(servercfg)
    else:
        _dry_run_func('\n{}'.format(servercfg), would_have='wrote out config')

    #with open(cfg_file, 'w') as cfg:

    return server_name


def wipe(args):
    print('Wiping server {}'.format(args.server))
    print('Checking directory {}'.format(args.server_root))

    serverfiles_path = os.path.join(args.server_root, 'serverfiles', 'server', args.server)
    print('Serverfiles path: {}'.format(serverfiles_path))

    oxide_path = os.path.join(args.server_root, 'serverfiles', 'oxide')
    oxide_data_path = os.path.join(args.server_root, oxide_path, 'data')
    oxide_config_path = os.path.join(args.server_root, oxide_path, 'config')

    lgsm_data_path = os.path.join(args.server_root, 'lgsm', 'data')

    oxide_path = oxide_path if os.path.exists(oxide_path) else None
    print('Oxide path: {}'.format(oxide_path))

    server_cfg_path = os.path.join(serverfiles_path, 'cfg')
    print('Server cfg path: {}'.format(oxide_path))

    if not args.dry_run:
        stop_server(args)

    # Oxide might not be installed on the server we're wiping
    if oxide_path:
        # Dry run checks are inside each function called
        wipe_oxide_data(oxide_data_path)
        set_oxide_config(args, oxide_config_path)

    # Remove all files belonging to the previous wipe
    wipe_serverfiles(serverfiles_path)

    # Set server configuration from args, return server name
    server_name = server_cfg_wipe(args, server_cfg_path)

    # Write to the seed file
    set_server_seed(args, lgsm_data_path)

    if not args.dry_run:
        start_server(args)

    if args.wipe_alert:
        import redis
        redis_conn = redis.Redis(
                        host=args.redis_host,
                        port=args.redis_port,
                        password=args.redis_password)

        isotime = datetime.datetime.now().isoformat(timespec='seconds')

        redis_conn.lpush(args.redis_list_name, json.dumps({
                                'type': 'wipe_alert',
                                'server_name': server_name,
                                'wipe_datetime': isotime
                            }))


def get_wipe_day(daystring):
    return ['Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'].index(daystring)

def get_default_dir():
    basepath = os.path.dirname(__file__)
    filepath = os.path.abspath(os.path.join(basepath, ".."))
    return filepath


def check_args(args):

    wipe_spec = [
        args.weekly,
        args.bi_weekly,
        args.monthly
        ]

    wipe_spec_names = [
        "--weekly",
        "--bi-weekly",
        "--monthly"
        ]

    if wipe_spec.count(True) != 1:
        raise Exception("Must have only of the following options: {}".format(
            ', '.join(wipe_spec_names)))


    if not args.now:
        days_unabbr = [x for x in calendar.day_name]

        if not args.on_day.lower().capitalize() in days_unabbr:
            raise Exception("--on-day argument must be one of the following:\n{}".format(
                '{}, {}'.format(
                    ', '.join(days_unabbr + days_abbr)
                )))


def is_exceptional_date(args, now):
    """
    Determine, given a newline separated list of YYYY-mm-dd formatted dates,
    if the datetime passed in (now) is an exceptional date
    """
    if args.exceptional_wipe_date_list:
        try:
            with open(args.exceptional_wipe_date_list) as ewdl_file:
                for raw_date_line in ewdl_file.readlines():
                    date_line = raw_date_line.strip()
                    try:
                        exceptional_date = datetime.datetime.strptime(date_line, '%Y-%m-%d')
                        if now.strftime('%Y-%m-%d') == exceptional_date.strftime('%Y-%m-%d'):
                            return True
                    except Exception as e:
                        print(f'Exception while parsing line: "{date_line}"\nError: {e}')
        except Exception as e:
            print(f'Exception while opening exceptional file list at {args.exceptional_wipe_date_list}:\nError: {e}')

    return False


def main(args):

    # Confirm args make sense
    check_args(args)

    now = datetime.datetime.now()
    exceptional_wipe = is_exceptional_date(args, now)

    if exceptional_wipe:
        print(f'Noted that {now.strftime("%Y-%m-%d")} is an exceptional date, refusing to wipe')
        return

    if args.seed is None:
        print('Saw no user-supplied seed, assuming randomized seed was desired')
        args.seed = rand.randint(0, 2**32-1)

    if args.now:
        wipe(args)
        return

    wipe_day = get_wipe_day(args.on_day.lower().capitalize())

    # We wipe if we're called on the same day.
    # If this is a problem, you haven't done your cronjob right.
    if wipe_day == now.weekday():
        if args.weekly:
            wipe(args)
            return
        if args.bi_weekly:
            if math.ceil((now.day / 7)) in [1, 3]:
                wipe(args)
                return
        if args.monthly:
            if now.day <= 7:
                wipe(args)
                return
    else:
        print(f'Today: {now.weekday()} | Wipe day: {wipe_day}')

    print('...not wiping.')


def create_arg_parser():
    parser = argparse.ArgumentParser(description='A Rust server wipe tool')

    parser.add_argument('--now',
                        action='store_true',
                        help='Wipe the server now, without consideration of any other arguments.')
    parser.add_argument('--weekly',
                        action='store_true',
                        help='Wipe server weekly')
    parser.add_argument('--bi-weekly',
                        action='store_true',
                        help='Wipe server bi-weekly. Will only wipe on the first and third '
                             'day of the month')
    parser.add_argument('--monthly',
                        action='store_true',
                        help='Wipe server monthly')
    parser.add_argument('--on-day',
                        default='Thursday',
                        help='The day of the week to wipe')
    parser.add_argument('--bps',
                        action='store_true',
                        help='Wipe player blueprints as well')
    parser.add_argument('--seed',
                        default=None,
                        type=int,
                        help='The new world seed, can be set to any positively signed 32-bit integer.')
    parser.add_argument('--description',
                        type=str,
                        help='Server description, overrides description file')
    parser.add_argument('--description-file',
                        type=str,
                        help='Server description file, inferior to --description')
    parser.add_argument('--size',
                        default=3000,
                        type=int,
                        help='World size in meters')
    parser.add_argument('--server',
                        default='rustserver',
                        type=str)
    parser.add_argument('--location',
                        default=None,
                        type=str)
    parser.add_argument('--official',
                        action='store_true',
                        help='Mark as an official server, '
                             'should enable achievements but SHOULD NOT be '
                             'used on anything other than a true vanilla server')
    #parser.add_argument('--add-wipedate',
    #                    action='store_true',
    #                    help='Add a wipedate to the timestamp')
    parser.add_argument('--server-name',
                        default='Rust Server',
                        help='Server name')
    parser.add_argument('--max-players',
                        default=100,
                        type=int,
                        help='Max players by default in server-level configuration')
    parser.add_argument('--server-root',
                        default=get_default_dir(),
                        help='Root directory for the LGSM install, typically ~/rustserver')
    parser.add_argument('--dry-run',
                        '--dry',
                        action='store_true',
                        help='Does not actually wipe')
    parser.add_argument('--flavor',
                        default=None,
                        help='The flavor of your rust server, "vanilla" or another server flavor',
                        type=str)
    parser.add_argument('--exceptional-wipe-date-list',
                        type=str,
                        help='The path to the exceptional wipe date list')

    parser.add_argument('--image-url',
                        default='https://i.imgur.com/D3kxEmx.png',
                        type=str,
                        help='Image url for banner (512px x 256px)')

    parser.add_argument('--server-url',
                        default='',
                        type=str,
                        help='URL for server webpage')

    parser.add_argument('--wipe-alert',
                        action='store_true',
                        help='Send a wipe alert via redis if enabled')

    parser.add_argument('--redis-host',
                        default='localhost',
                        type=str,
                        help='Redis hostname (for wipe alerts)')

    parser.add_argument('--redis-port',
                        default=6379,
                        type=int,
                        help='Redis port (for wipe alerts)')

    parser.add_argument('--redis-list-name',
                        default='rust_alerts',
                        type=str,
                        help='Redis list (for wipe alerts)')

    parser.add_argument('--redis-password',
                        default=None,
                        type=str,
                        help='Optional password for redis server')

    #
    # Server tags that don't have an effect on server
    # wipe configuration
    #
    parser.add_argument('--vanilla',
                        action='store_true',
                        help='Add the vanilla server tag')
    parser.add_argument('--pve',
                        action='store_true',
                        help='Add the PvE server tag')
    parser.add_argument('--roleplay',
                        action='store_true',
                        help='Add the roleplay tag')
    parser.add_argument('--creative',
                        action='store_true',
                        help='Add the creative tag')
    parser.add_argument('--softcore',
                        action='store_true',
                        help='Add the softcore tag')
    parser.add_argument('--minigame',
                        action='store_true',
                        help='Add the minigame tag')
    parser.add_argument('--training',
                        action='store_true',
                        help='Add the training tag')
    parser.add_argument('--battlefield',
                        action='store_true',
                        help='Add the battlefield tag')
    parser.add_argument('--broyale',
                        action='store_true',
                        help='Add the broyale tag')
    parser.add_argument('--build',
                        action='store_true',
                        help='Add the build tag')

    return parser


if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()
    main(args)
