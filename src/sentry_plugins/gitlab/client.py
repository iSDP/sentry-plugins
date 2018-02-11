from __future__ import absolute_import

from requests.exceptions import HTTPError
from six.moves.urllib.parse import quote
from sentry.http import build_session

from sentry_plugins.exceptions import ApiError


class GitLabClient(object):
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def request(self, method, path, data=None, params=None):
        headers = {
            'Private-Token': self.token,
        }
        session = build_session()
        try:
            resp = getattr(session, method.lower())(
                url='{}/api/v3/{}'.format(self.url, path.lstrip('/')),
                headers=headers,
                json=data,
                params=params,
                allow_redirects=False,
            )
            resp.raise_for_status()
        except HTTPError as e:
            raise ApiError.from_response(e.response)
        return resp.json()

    def auth(self):
        return self.request('GET', '/user')

    def get_project(self, repo):
        return self.request('GET', '/projects/{}'.format(quote(repo, safe='')))

    def get_issue(self, repo, issue_id):
        try:
            return self.request(
                'GET',
                '/projects/{}/issues/{}'.format(
                    quote(repo, safe=''),
                    issue_id
                )
            )
        except IndexError:
            raise ApiError('Issue not found with ID', 404)

    def create_issue(self, repo, data):
        return self.request(
            'POST',
            '/projects/{}/issues'.format(quote(repo, safe='')),
            data=data,
        )

    def create_note(self, repo, global_issue_id, data):
        return self.request(
            'POST',
            '/projects/{}/issues/{}/notes'.format(
                quote(repo, safe=''),
                global_issue_id,
            ),
            data=data,
        )

    def list_project_members(self, repo):
        return self.request(
            'GET',
            '/projects/{}/members'.format(quote(repo, safe='')),
        )

    def get_commits(self, repo):
        return self.request(
            'GET',
            '/projects/{}/repository/commits'.format(quote(repo, safe=''))
        )

    def get_commit(self, repo, commit_sha):
        return self.request(
            'GET',
            '/projects/{}/repository/commits/{}'.format(quote(repo, safe=''), commit_sha)
        )

    def get_merge_request_commits(self, repo, merge_request_iid):
        return self.request(
            'GET',
            '/projects/{}/merge_requests/{}/commits'.format(quote(repo, safe=''), merge_request_iid)
        )

