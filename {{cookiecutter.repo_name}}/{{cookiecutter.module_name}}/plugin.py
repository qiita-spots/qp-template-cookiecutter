# -----------------------------------------------------------------------------
# Copyright (c) {% now 'local', '%Y' %}, {{cookiecutter.author}}.
#
# Distributed under the terms of the {{cookiecutter.license}} License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from os.path import exists, join, dirname, abspath
from os import makedirs, environ
from future import standard_library
import traceback
import sys

from qiita_client import QiitaClient

# TODO: Add relevant imports here

with standard_library.hooks():
    from configparser import ConfigParser

TASK_DICT = {
    # TODO: Add the mappings between Qiita's command name and the actual
    # python function executing the command
    'TODO: command name': "TODO: python function"
}


def execute_job(server_url, job_id, output_dir):
    """Starts the plugin and executes the assigned task

    Parameters
    ----------
    server_url : str
        The url of the server
    job_id : str
        The job id
    output_dir : str
        The output directory

    Raises
    ------
    RuntimeError
        If there is a problem gathering the job information
    """
    # Set up the Qiita Client
    dflt_conf_fp = join(dirname(abspath(__file__)), 'support_files',
                        'config_file.cfg')
    conf_fp = environ.get('{{cookiecutter.module_name.upper()}}_CONFIG_FP',
                          dflt_conf_fp)
    config = ConfigParser()
    with open(conf_fp, 'U') as conf_file:
        config.readfp(conf_file)

    qclient = QiitaClient(server_url, config.get('main', 'CLIENT_ID'),
                          config.get('main', 'CLIENT_SECRET'),
                          server_cert=config.get('main', 'SERVER_CERT'))

    # Request job information. If there is a problem retrieving the job
    # information, the QiitaClient already raises an error
    job_info = qclient.get_job_info(job_id)
    # Starting the job heartbeat, so Qiita knows that this job is runnig
    qclient.start_heartbeat(job_id)
    # Execute the given task
    task_name = job_info['command']
    task = TASK_DICT[task_name]

    if not exists(output_dir):
        makedirs(output_dir)
    try:
        success, artifacts_info, error_msg = task(
            qclient, job_id, job_info['parameters'], output_dir)
    except Exception:
        exc_str = repr(traceback.format_exception(*sys.exc_info()))
        error_msg = ("Error executing %s: \n%s" % (task_name, exc_str))
        success = False
        artifacts_info = None

    # The job completed
    qclient.complete_job(job_id, success, error_msg=error_msg,
                         artifacts_info=artifacts_info)
