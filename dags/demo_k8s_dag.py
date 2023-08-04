import airflow
from airflow import DAG

from airflow.operators.python import PythonOperator



# AIRFLOW_HOST = 'http://airflow-ohio-a.hyperdonut.com:8080'


def demo(dag_run, ti):
    print("dEmo")



def print_execution_date(**context):
    execution_date = context['execution_date']
    timeshift_date = context['ti'].xcom_pull(key=None, task_ids='timeshift_date')
    if timeshift_date:
        print('Got execution date {}'.format(timeshift_date))
    else:
        print('Got execution date {}'.format(execution_date))



default_args = {
    'owner': 'operations',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
}

dag = DAG(
    'demo_dag',
    default_args=default_args,
    schedule_interval='*/15 * * * *',
    tags=['demo'],
    catchup=False
)
with dag:
    demo_task = PythonOperator(
        task_id='demo_task',
        python_callable=demo
    )
