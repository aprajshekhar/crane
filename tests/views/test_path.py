from . import base


class TestPath(base.BaseCraneAPITest):
    def test_invalid_repo_name(self):
        response = self.test_client.get('/v2/no/name/test')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_valid_repo_name(self):
        response = self.test_client.get('/v2/redhat/foo/test')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))
        self.assertTrue('foo/bar/images/test' in response.headers['Location'])

    def test_valid_repo_name_without_trailing_slash(self):
        response = self.test_client.get('/v2/redhat/foo/test')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))
        self.assertTrue('/bar/images' in response.headers['Location'])

    def test_repo_name_without_username(self):
        response = self.test_client.get('/v2/foo/test')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_repo_name_without_repo(self):
        response = self.test_client.get('/v2/redhat/test')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_repo_name_without_path(self):
        response = self.test_client.get('/v2/redhat/foo')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))
