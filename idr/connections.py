"""
Helper functions for accessing the IDR from within IPython notebooks.
"""
import requests
import omero
from omero.gateway import BlitzGateway


def connection(host=None, user=None, password=None, port=4064):
    """
    Connect to the IDR analysis OMERO server
    :return: A BlitzGateway object
    """

    # WARNING: The following block is automatically updated by the IDR
    # deployment scripts. Do not edit this file without testing.
    # BEGIN ANSIBLE MANAGED BLOCK
    default_host = "localhost"
    default_user = "omero"
    default_password = "omero"
    # END ANSIBLE MANAGED BLOCK

    if host is None:
        host = default_host
    if user is None:
        user = default_user
    if password is None:
        password = default_password

    c = omero.client(host)
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
