"""
Non-public view for use by admins to see a list of repositories served by crane.
"""
from flask import Blueprint, current_app, json, render_template, request

from .. import app_util


section = Blueprint('crane', __name__, url_prefix='/crane', static_url_path='/' )


@section.route('/repositories/v2')
def repositories_v2():
    """
    Returns a json document containing a dictionary of repositories served by crane
    and keyed by the repo-registry-id which is unique for each repository.

    :return:    json string containing a list of docker repositories
    :rtype:     basestring
    """
    repos_json = app_util.get_v2_repositories()
    if 'Accept' in request.headers and request.headers['Accept'] == 'application/json':
        response = current_app.make_response(json.dumps(repos_json, sort_keys=True))
        response.headers['Content-Type'] = 'application/json'
        return response
    return render_template("repositories.html", repos_json=repos_json, repo_type='v2')


@section.route('/repositories')
def repositories_v1():
    """
    Returns a json document containing a dictionary of repositories served by crane
    and keyed by the repo-registry-id which is unique for each repository.

    :return:    json string containing a list of docker repositories
    :rtype:     basestring
    """
    repos_json = app_util.get_repositories()
    if 'Accept' in request.headers and request.headers['Accept'] == 'application/json':
        response = current_app.make_response(json.dumps(repos_json, sort_keys=True))
        response.headers['Content-Type'] = 'application/json'
        return response
    return render_template("repositories.html", repos_json=repos_json, repo_type='v1')


