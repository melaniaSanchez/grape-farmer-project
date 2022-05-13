"""
Importing necessary modules
"""
from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from src.example_transformation import function_a


"""
Initializing DAGs
"""
dag = DAG(
          dag_id="grepy_sample_dag",
          start_date=days_ago(2),
          description="DAG which orchestrates a simple ML workflow",
          schedule_interval='@daily')

"""
Creating Tasks
"""

first_task = PythonOperator(
        task_id="first_task",
        python_callable= function_a,
        op_kwargs= {'name': 'Fayaz'},
        dag= dag)

second_task = DummyOperator(task_id="second_task", dag=dag)

"""
Dependencies
"""
first_task >> second_task
