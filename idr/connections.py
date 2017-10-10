"""
Helper functions for accessing the IDR from within IPython notebooks.
"""
import random
import requests
import os
import sys

import omero
from omero.gateway import BlitzGateway


def _configuration_from_url(config_url):
    """
    OMERO binary protocol doesn't support load balancing nor session pinning
    so it has to be done client-side by connecting to a random server/port
    """
    r = requests.get(config_url)
    r.raise_for_status()
    cfgs = r.json()
    cfg = random.choice(cfgs)
    return cfg


def _lookup_parameter(initial, paramname, autocfg, default):
    if initial is not None:
        return initial
    v = autocfg.get(paramname)
    if v is not None:
        return v
    v = os.getenv('IDR_' + paramname.upper())
    if v is not None:
        return v
    return default


def connection(host=None, user=None, password=None, port=None):
    """
    Connect to the IDR analysis OMERO server
    Lookup of connection parameters is done in this order:
    1. Parameters passed as arguments to this method
    2. Parameters obtained from IDR_OMERO_CONFIGURATION_URL
    3. Parameters obtained from IDR_{HOST,PORT,USER,PASSWORD}
    4. Built-in defaults

    :return: A BlitzGateway object
    """
    autocfg = {}
    config_url = os.getenv('IDR_OMERO_CONFIGURATION_URL')
    if config_url:
        try:
            autocfg = _configuration_from_url(config_url)
        except Exception as e:
            print >> sys.stderr, 'Failed to fetch configuration: %r' % e

    host = _lookup_parameter(host, 'host', autocfg, 'localhost')
    port = _lookup_parameter(port, 'port', autocfg, 4064)
    user = _lookup_parameter(user, 'user', autocfg, 'omero')
    password = _lookup_parameter(password, 'password', autocfg, 'omero')

    c = omero.client(host, int(port))
    c.enableKeepAlive(300)
    c.createSession(user, password)
    conn = BlitzGateway(client_obj=c)

    print "Connected to IDR..."
    return conn


def create_http_session(idr_base_url='https://idr.openmicroscopy.org'):

    """
    Create and return http session
    """
    index_page = "%s/webclient/?experimenter=-1" % idr_base_url

    # create http session
    with requests.Session() as session:
        request = requests.Request('GET', index_page)
        prepped = session.prepare_request(request)
        response = session.send(prepped)
        if response.status_code != 200:
            response.raise_for_status()

    return session
