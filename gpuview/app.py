#!/usr/bin/env python

"""
Web API of gpuview.

@author Fitsum Gaim
@url https://github.com/fgaim
"""

import os
import json
from datetime import datetime
import time

from bottle import Bottle, TEMPLATE_PATH, template, response


from . import utils
from . import core


app = Bottle()
abs_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_path, 'views')
TEMPLATE_PATH.insert(0, abs_views_path)

EXCLUDE_SELF = False  # Do not report to `/gpustat` calls.
# last update time
last_time=None
last_web=None

@app.route('/')
def index():
    t = time.time()
    if t-last_time>60:
        update()
    return last_web
        

def update():
    global last_web,last_time
    gpustats = core.all_gpustats()
    now = datetime.now().strftime('更新于 %Y-%m-%d %H:%M:%S')
    last_time=time.time()
    last_web=template('index', gpustats=gpustats, update_time=now)


@app.route('/gpustat', methods=['GET'])
def report_gpustat():
    """
    Returns the gpustat of this host.
        See `exclude-self` option of `gpuview run`.
    """

    def _date_handler(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError(type(obj))

    response.content_type = 'application/json'
    if EXCLUDE_SELF:
        resp = {'error': 'Excluded self!'}
    else:
        resp = core.my_gpustat()
    return json.dumps(resp, default=_date_handler)


def main():
    parser = utils.arg_parser()
    args = parser.parse_args()

    if 'run' == args.action:
        core.safe_zone(args.safe_zone)
        global EXCLUDE_SELF
        EXCLUDE_SELF = args.exclude_self
        update()
        app.run(host=args.host, port=args.port, debug=args.debug)
    elif 'service' == args.action:
        core.install_service(host=args.host,
                             port=args.port,
                             safe_zone=args.safe_zone,
                             exclude_self=args.exclude_self)
    elif 'add' == args.action:
        core.add_host(args.url, args.name)
    elif 'remove' == args.action:
        core.remove_host(args.url)
    elif 'hosts' == args.action:
        core.print_hosts()
    elif 'update' == args.action:
        core.update()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
