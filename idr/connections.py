"""
Helper functions for accessing the IDR from within IPython notebooks.
"""
import re
import requests
import os

import omero
from omero.gateway import BlitzGateway


def _configuration_from_url(config_url):
    """
    OMERO binary protocol doesn't support load balancing nor session pinning
    so it has to be done client-side by connecting to a random server/port
    """
    try:
        host = re.match('\w+://([^:/]+)', config_url).group(1)
    except AttributeError:
        host = config_url
        config_url = 'https://%s/connection/omero-client.json' % host
    r = requests.get(config_url)
    r.raise_for_status()
    cfg = r.json()
    return cfg, host


def _lookup_parameter(initial, paramname, default):
    if initial is not None:
        return initial
    v = os.getenv('IDR_' + paramname.upper())
    if v is not None:
        return v
    return default


def connection(host=None, user=None, password=None, port=None, verbose=1):
    """
    Connect to the IDR analysis OMERO server
    Lookup of connection parameters is done in this order:

    1. If host/IDR_HOST starts with protocol:// treat this as a full
       omero-client.json configuration URL and fetch it
    2. If host/IDR_HOST is defined but port/IDR_PORT empty then attempt
       to fetch configuration from
       https://host/connection/omero-client.json
    3. Remaining parameters are taken first from the method arguments,
       then from IDR_{HOST,PORT,USER,PASSWORD}
    4. If host/IDR_HOST was a configuration URL then automatically set
       host to the host portion of the URL in case it needs to be
       substituted into the fetched configuration

    No defaults are provided

    :return: A BlitzGateway object
    """
    host = _lookup_parameter(host, 'host', '')
    port = int(_lookup_parameter(port, 'port', 0))
    user = _lookup_parameter(user, 'user', None)
    password = _lookup_parameter(password, 'password', None)

    autocfg = []
    if (host and not port) or re.match('\w+://', host):
        autocfg, host = _configuration_from_url(host)

    # https://github.com/openmicroscopy/openmicroscopy/blob/v5.4.3/components/tools/OmeroPy/src/omero/clients.py#L50
    kwargs = {'args': autocfg}
    if host:
        kwargs['host'] = host
    if port:
        kwargs['port'] = port

    c = omero.client(**kwargs)
    c.enableKeepAlive(300)
    c.createSession(user, password)
    conn = BlitzGateway(client_obj=c)

    if verbose > 0:
        server = ''
        if verbose > 1:
            info = conn.c.sf.ice_getConnection().getInfo()
            server = '[{}:{}]'.format(info.remoteAddress, info.remotePort)

        print("Connected to IDR%s ..." % server)
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
