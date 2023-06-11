# -*- encoding: utf-8 -*-
# möp
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <dkratzert@gmx.de> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# Daniel Kratzert
# ----------------------------------------------------------------------------
#
from __future__ import print_function

import sys
from contextlib import suppress

import requests

from structurefinder.misc.version import VERSION

urlprefix = "https://dkratzert.de/files/structurefinder/"


def get_current_strf_version(silent=True) -> str:
    """
    determines the current version on the web server

    Returns
    -------
    version number
    """
    headers = {
        'User-Agent': f'strf_cmd v{VERSION} ({sys.platform})',
    }
    try:
        response = requests.get(url='{}version.txt'.format(urlprefix), headers=headers, timeout=2)
    except Exception:
        if not silent:
            print("*** Unable to connect to update server. No Update possible. ***")
        return '0'
    if response.status_code == 200:
        with suppress(ValueError):
            version = response.content.decode('ascii').strip()
    else:
        version = '0'
    return version


def is_update_needed(VERSION=0) -> bool:
    """
    Decides if an update is needed.
    """
    version = get_current_strf_version(silent=True)
    if int(VERSION) < int(version):
        return True
    else:
        return False
