import pathlib
import os
import json

from kubernetes.client import models as k8s


from datetime import datetime, timedelta
from platform import python_version
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.bash import BashOperator


VERSION: str = "0.58"

CONTAINER_RESOURCES = k8s.V1ResourceRequirements(
    requests={
        "cpu": "500m",
        "memory": "2Gi",
    },
    limits={
        "cpu": "500m",
        "memory": "4Gi",
    },
)

# Sandbox
# secrets_list = [
#     Secret("env", "SHOPIFY_ACCESS_TOKENS_NAME", "shopify-utx-secret", "value"),
#     Secret("env", "SELLERFUSION_SECRET_NAME", "sfdb-utx-secret", "value"),
#     Secret("env", "AWS_DAILY_REPORTS_ACCOUNT_CREDENTIALS", "awscred-utx-secret", "value"),
#     Secret("env", "DB_SECRET_NAME", "dailyreport-secret", "value"),
#     Secret("env", "GOOGLE_SERVICE_ACCOUNT_API_SECRET_NAME", "google-service-account-utx-api-key", "value"),
#     Secret("env", "AWS_ROOT_ACCOUNT_CREDENTIALS", "aws-root-account-credentials", "value"),
#     Secret("env", "EBAY_CLIENT_SECRET_NAME", "ebay-client-secret", "value"),
# ]

# Prod
secrets_list = [
    Secret("env", "SHOPIFY_ACCESS_TOKENS_NAME", "shopify-utx-secret", "value"),
    Secret("env", "EBAY_CLIENT_SECRET_NAME", "ebay-client-secret", "value"),
    Secret("env", "SELLERFUSION_SECRET_NAME", "sfdb-utx-secret", "value"),
    Secret("env", "AWS_DAILY_REPORTS_ACCOUNT_CREDENTIALS", "aws-daily-reports-account-credentials", "value"),
    Secret("env", "DB_SECRET_NAME", "dailyreport-production-secret", "value"),
    Secret("env", "GOOGLE_SERVICE_ACCOUNT_API_SECRET_NAME", "google-service-account-utx-api-key", "value"),
    Secret("env", "AWS_ROOT_ACCOUNT_CREDENTIALS", "aws-root-account-credentials", "value"),
]

with DAG(
    "utx_report",
    default_args={
        "depends_on_past": False,
        "email": ["arshul.mohd@acqu.co"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    description=f"DAG VERSION: {VERSION}",
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["dna"],
) as dag:
    print(os.environ.get("AIRFLOW_STACK_ENV"))
    utx_scheduler = KubernetesPodOperator(
        namespace="airflow",
        image=f"dnateam.azurecr.io/utx_reports:{VERSION}",
        image_pull_secrets=[k8s.V1LocalObjectReference("dnateam-azurecr")],
        cmds=["python", "job_scheduler.py", json.dumps("{{ dag_run.conf }}")],
        name="utx-job",
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id=f"run",
        get_logs=True,
        secrets=secrets_list,
        env_vars={"STACK_ENV_NAME": os.environ.get("AIRFLOW_STACK_ENV"), "INFRASTRUCTURE_NAME": "airflow"},
        # container_resources=CONTAINER_RESOURCES,
        do_xcom_push=True,
    )
    utx_scheduler = BashOperator(
        task_id="run",
        bash_command="",
        # retries=3,
        # on_failure_callback=failure_callback,
        executor_config=get_env_executor_config("mv_promotion_performance", resource_config)
    )


    # api_worker = KubernetesPodOperator.partial(
    #     namespace="airflow",
    #     image=f"dnateam.azurecr.io/utx_reports:{VERSION}",
    #     image_pull_secrets=[k8s.V1LocalObjectReference("dnateam-azurecr")],
    #     name="utx-worker",
    #     is_delete_operator_pod=True,
    #     in_cluster=True,
    #     task_id=f"run2",
    #     get_logs=True,
    #     secrets=secrets_list,
    #     env_vars={"STACK_ENV_NAME": os.environ.get("AIRFLOW_STACK_ENV"), "INFRASTRUCTURE_NAME": "airflow"},
    #     container_resources=CONTAINER_RESOURCES,
    #     do_xcom_push=True,
    # ).expand(
    #     cmds=[
    #         [
    #             "python",
    #             "job_handler.py",
    #             f"{idx}",
    #             "{{ task_instance.xcom_pull(task_ids='run', dag_id='utx_report', key='return_value') }}",
    #         ]
    #         for idx in range(20)
    #     ]
    # )
    #
    # # 2
    # mapping_scheduler = KubernetesPodOperator(
    #     namespace="airflow",
    #     image=f"dnateam.azurecr.io/utx_reports:{VERSION}",
    #     image_pull_secrets=[k8s.V1LocalObjectReference("dnateam-azurecr")],
    #     cmds=["python", "mapping_scheduler.py", json.dumps("{{ dag_run.conf }}")],
    #     name="mapping-scheduler",
    #     is_delete_operator_pod=True,
    #     in_cluster=True,
    #     task_id=f"run3",
    #     get_logs=True,
    #     secrets=secrets_list,
    #     env_vars={"STACK_ENV_NAME": os.environ.get("AIRFLOW_STACK_ENV"), "INFRASTRUCTURE_NAME": "airflow"},
    #     container_resources=CONTAINER_RESOURCES,
    #     do_xcom_push=True,
    # )
    #
    # # 3
    # mapping_handler = KubernetesPodOperator.partial(
    #     namespace="airflow",
    #     image=f"dnateam.azurecr.io/utx_reports:{VERSION}",
    #     image_pull_secrets=[k8s.V1LocalObjectReference("dnateam-azurecr")],
    #     name="mapping-handler",
    #     is_delete_operator_pod=True,
    #     in_cluster=True,
    #     task_id=f"run4",
    #     get_logs=True,
    #     secrets=secrets_list,
    #     env_vars={"STACK_ENV_NAME": os.environ.get("AIRFLOW_STACK_ENV"), "INFRASTRUCTURE_NAME": "airflow"},
    #     container_resources=CONTAINER_RESOURCES,
    #     do_xcom_push=True,
    # ).expand(
    #     cmds=[
    #         [
    #             "python",
    #             "mapping_handler.py",
    #             f"{idx}",
    #             "{{ task_instance.xcom_pull(task_ids='run3', dag_id='utx_report', key='return_value') }}",
    #         ]
    #         for idx in range(20)
    #     ]
    # )
    #
    # # 4
    # tonetsuit_scheduler = KubernetesPodOperator(
    #     namespace="airflow",
    #     image=f"dnateam.azurecr.io/utx_reports:{VERSION}",
    #     image_pull_secrets=[k8s.V1LocalObjectReference("dnateam-azurecr")],
    #     cmds=["python", "tonetsuit_scheduler.py", json.dumps("{{ dag_run.conf }}")],
    #     name="tonetsuit-scheduler",
    #     is_delete_operator_pod=True,
    #     in_cluster=True,
    #     task_id=f"run5",
    #     get_logs=True,
    #     secrets=secrets_list,
    #     env_vars={"STACK_ENV_NAME": os.environ.get("AIRFLOW_STACK_ENV"), "INFRASTRUCTURE_NAME": "airflow"},
    #     container_resources=CONTAINER_RESOURCES,
    #     do_xcom_push=True,
    # )
    #
    # # 5
    # tonetsuit_handler = KubernetesPodOperator.partial(
    #     namespace="airflow",
    #     image=f"dnateam.azurecr.io/utx_reports:{VERSION}",
    #     image_pull_secrets=[k8s.V1LocalObjectReference("dnateam-azurecr")],
    #     name="tonetsuit-handler",
    #     is_delete_operator_pod=True,
    #     in_cluster=True,
    #     task_id=f"run6",
    #     get_logs=True,
    #     secrets=secrets_list,
    #     env_vars={"STACK_ENV_NAME": os.environ.get("AIRFLOW_STACK_ENV"), "INFRASTRUCTURE_NAME": "airflow"},
    #     container_resources=CONTAINER_RESOURCES,
    #     do_xcom_push=True,
    # ).expand(
    #     cmds=[
    #         [
    #             "python",
    #             "tonetsuit_handler.py",
    #             f"{idx}",
    #             "{{ task_instance.xcom_pull(task_ids='run5', dag_id='utx_report', key='return_value') }}",
    #         ]
    #         for idx in range(20)
    #     ]
    # )
    #
    # utx_scheduler >> api_worker >> mapping_scheduler >> mapping_handler >> tonetsuit_scheduler >> tonetsuit_handler
