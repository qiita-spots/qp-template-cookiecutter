# -----------------------------------------------------------------------------
# Copyright (c) {% now 'local', '%Y' %}, {{cookiecutter.author}}.
#
# Distributed under the terms of the {{cookiecutter.license}} License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import TestCase, main
from tempfile import mkdtemp, mkstemp
from os import remove, environ, close
from os.path import exists, isdir
from shutil import rmtree

from qiita_client import QiitaClient

from {{cookiecutter.module_name}}.plugin import execute_job


CLIENT_ID = '19ndkO3oMKsoChjVVWluF7QkxHRfYhTKSFbAVt8IhK7gZgDaO4'
CLIENT_SECRET = ('J7FfQ7CQdOxuKhQAf1eoGgBAE81Ns8Gu3EKaWFm3IO2JKh'
                 'AmmCWZuabe0O5Mp28s1')


class PluginTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up the Qiita Client
        server_cert = environ.get('QIITA_SERVER_CERT', None)
        cls.qclient = QiitaClient("https://localhost:21174", CLIENT_ID,
                                  CLIENT_SECRET, server_cert=server_cert)

    @classmethod
    def tearDownClass(cls):
        # Reset the test database
        cls.qclient.post("/apitest/reset/")

    def setUp(self):
        fd, fp = mkstemp()
        close(fd)
        with open(fp, 'w') as f:
            f.write(CONFIG_FILE % (self.server_cert, CLIENT_ID, CLIENT_SECRET))
        environ['{{cookiecutter.module_name.upper()}}_CONFIG_FP'] = fp

        self.out_dir = mkdtemp()
        self._clean_up_files = [self.out_dir, fp]

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def test_execute_job(self):
        # TODO: Create a job that will complete successfully so the completion
        # of the job in success can be tested
        data = {'TODO: populate with job data'}
        job_id = self.qclient.post(
            '/apitest/processing_job/', data=data)['job']

        execute_job("https://localhost:21174", job_id, self.out_dir)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs['status'], 'error')

    def test_execute_job_error(self):
        # TODO: Create a job that will fail so the completion of the job in
        # failure can be tested
        data = {'TODO: populate with job data'}
        job_id = self.qclient.post(
            '/apitest/processing_job/', data=data)['job']

        execute_job("https://localhost:21174", job_id, self.out_dir)
        obs = self.qclient.get_job_info(job_id)
        self.assertEqual(obs['status'], 'error')

CONFIG_FILE = """
[main]
SERVER_CERT = %s

# Oauth2 plugin configuration
CLIENT_ID = %s
CLIENT_SECRET = %s
"""

if __name__ == '__main__':
    main()
