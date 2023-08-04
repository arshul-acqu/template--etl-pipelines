from copy import deepcopy
from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG
from airflow.configuration import conf

import os
import sys

sys.path.append('/opt/airflow/custom_log')

BASE_LOG_FOLDER: str = conf.get('logging', 'BASE_LOG_FOLDER')
FILENAME_TEMPLATE: str = conf.get('logging', 'LOG_FILENAME_TEMPLATE')

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)
LOGGING_CONFIG['handlers']['k8stask'] = {
    'class': 'k8s_task_handler.KubernetesTaskHandler',
    'formatter': 'airflow',
    'base_log_folder': os.path.expanduser(BASE_LOG_FOLDER),
    'filename_template': FILENAME_TEMPLATE
}

LOGGING_CONFIG['loggers']['airflow.task']['handlers'].append('k8stask')