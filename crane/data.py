from collections import namedtuple
import glob
import logging
import os
import threading
import time
import urlparse

from flask import json

from . import config


logger = logging.getLogger(__name__)

response_data = {
    'repos': {},
    'images': {},
}

Repo = namedtuple('Repo', ['url', 'images_json', 'tags_json', 'url_path', 'protected'])


def load_from_file(path):
    """
    Load one specific repository's metadata from a json file

    :param path:    full path to the json file
    :type  path:    basestring

    :return:    tuple of repo_id (str), repo_tuple (Repo), image_ids (list)
    :rtype:     tuple

    :raises ValueError: if the "version" value in the metadata is not a supported
                        metadata schema version
    """
    with open(path) as json_file:
        repo_data = json.load(json_file)

    # for now, we only support version 1 of the metadata schema
    if repo_data['version'] != 1:
        raise ValueError('metadata version %d not supported' % repo_data['version'])

    repo_id = repo_data['repo-registry-id']
    image_ids = [image['id'] for image in repo_data['images']]
    url_path = urlparse.urlparse(repo_data['url']).path
    repo_tuple = Repo(repo_data['url'],
                      json.dumps(repo_data['images']),
                      json.dumps(repo_data['tags']),
                      url_path, repo_data.get('protected', False))

    return repo_id, repo_tuple, image_ids


def monitor_data_dir(app, last_modified=0):
    """
    Loop forever monitoring the data directory for changes and reload the data if any changes occur
    This checks for updates at the interval defined in the config file (Defaults to 60 seconds)

    :param app: the flask application
    :type  app: flask.Flask
    :param last_modified:   seconds since the epoch; if the data on disk is modified
                            after this time, it must be re-loaded.
    :type  last_modified:   int or float
    """
    data_dir = app.config[config.KEY_DATA_DIR]
    polling_interval = app.config[config.KEY_DATA_POLLING_INTERVAL]
    if not os.path.exists(data_dir):
        logging.error('The data directory specified does not exist: %s' % data_dir)
    while True:
        # Check if the modified time has changed on the directory and if so reload the data
        # This has been verified using a directory mounted via NFS 4 as well as locally
        try:
            logging.debug('Checking for new metadata files')
            current_modified = os.stat(data_dir).st_mtime
            if current_modified > last_modified:
                last_modified = current_modified
                load_all(app)
        except OSError:
            # The directory does not exist
            pass
        time.sleep(polling_interval)


def start_monitoring_data_dir(app):
    """
    Spin off a daemon thread that monitors the data dir for changes and updates the app config
    if any changes occur.  This will guarantee a refresh of the app data the first time it is run

    :param app: the flask application
    :type  app: flask.Flask
    """
    now = time.time()
    # load the data once in a blocking fashion
    load_all(app)
    thread = threading.Thread(target=monitor_data_dir, args=(app, now))
    thread.setDaemon(True)
    thread.start()


def load_all(app):
    """
    Load all metadata files and replace the "response_data" value in this
    module.

    :param app: the flask application
    :type  app: flask.Flask
    """
    global response_data
    repos = {}
    images = {}

    try:
        data_dir = app.config[config.KEY_DATA_DIR]
        logging.info('loading metadata from %s' % data_dir)
        paths = glob.glob(os.path.join(data_dir, '*.json'))

        # load data from each file
        for metadata_file_path in paths:
            repo_id, repo_tuple, image_ids = load_from_file(metadata_file_path)
            repos[repo_id] = repo_tuple
            for image_id in image_ids:
                images.setdefault(image_id, set()).add(repo_id)

        # make each set immutable
        for image_id in images.keys():
            images[image_id] = frozenset(images[image_id])

        # replace old data structure with new
        response_data = {
            'repos': repos,
            'images': images,
        }

    except Exception, e:
        logger.error('aborting metadata load: %s' % str(e))
