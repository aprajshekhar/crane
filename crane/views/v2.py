from flask import Blueprint, json, current_app, redirect
from ..api import repository


section = Blueprint('v2', __name__, url_prefix='/v2')


@section.after_request
def add_common_headers(response):
    """
    Add headers to a response.

    All 200 responses get a content type of 'application/json', and all others
    retain their default.

    Headers are added to make this app look like the actual docker-registry.

    :param response:    flask response object for a request
    :type  response:    flask.Response

    :return:    a response object that has the correct headers
    :rtype:     flask.Response
    """
    # if response code is 200, assume it is JSON
    if response.status_code == 200:
        response.headers['Content-Type'] = 'application/json'
    # current stable release of docker-registry
    response.headers['X-Docker-Registry-Version'] = '0.6.6'
    response.headers['Docker-Distribution-API-Version'] = 'registry/2.0'
    # "common" is documented by docker-registry as a valid config, but I am
    # just guessing that it will work in our case.
    response.headers['X-Docker-Registry-Config'] = 'common'

    return response


@section.route('/')
def v2():
    # "True" is what the real docker-registry puts in the response body
    response = current_app.make_response(json.dumps({}))
    response.headers['X-Docker-Registry-Standalone'] = True
    return response


@section.route('/<path:username>/<path:repo>/<path:file_path>')
def name_redirect(username, repo, file_path):
    """


    :param username:    username of the repo
    :type  username:    basestring
    :param repo:    name of the repository
    :type  repo:    basestring
    :param file_path: the relative path
    :type file_path:  basestring
    :return:    302 redirect response
    :rtype:     flask.Response
    """

    repo_id = '/'.join([username, repo])
    print(repo_id)
    base_url = repository.get_path_for_repo(repo_id)
    if not base_url.endswith('/'):
        base_url += '/'
    url = base_url + file_path
    return redirect(url)
