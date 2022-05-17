import os
from datetime import timedelta

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.operators.emr_create_job_flow import (
    EmrCreateJobFlowOperator,
)
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor
from airflow.utils.dates import days_ago

DAG_ID = os.path.basename(__file__).replace(".py", "")

DEFAULT_ARGS = {
    "owner": "garystafford",
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
}

SPARK_STEPS = [
    {
        "Name": "calculate_pi",
        "ActionOnFailure": "CONTINUE",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": ["/usr/lib/spark/bin/run-example", "SparkPi", "10"],
        },
    }
]

JOB_FLOW_OVERRIDES = {
    "Name": "demo-cluster-airflow",
    "ReleaseLabel": "emr-6.4.0",
    "Applications": [
        {"Name": "Spark"},
    ],
    "Instances": {
        "InstanceGroups": [
            {
                "Name": "Master nodes",
                "Market": "ON_DEMAND",
                "InstanceRole": "MASTER",
                "InstanceType": "m5.xlarge",
                "InstanceCount": 1,
            }
        ],
        "KeepJobFlowAliveWhenNoSteps": False,
        "TerminationProtected": False,
    },
    "VisibleToAllUsers": True,
    "JobFlowRole": "EMR_EC2_DefaultRole",
    "ServiceRole": "EMR_DefaultRole",
    "Tags": [
        {"Key": "Environment", "Value": "Development"},
        {"Key": "Name", "Value": "Airflow EMR Demo Project"},
        {"Key": "Owner", "Value": "Data Analytics Team"},
    ],
    "LogUri": "s3://emr-log-bucket-grape-farmer-project/default_job_flow_location/",
}

with DAG(
    dag_id=DAG_ID,
    description="Run built-in Spark app on Amazon EMR",
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(hours=2),
    start_date=days_ago(1),
    schedule_interval=None,
    tags=["emr demo", "spark"],
) as dag:
    begin = DummyOperator(task_id="begin")

    end = DummyOperator(task_id="end")

    cluster_creator = EmrCreateJobFlowOperator(
        task_id="create_job_flow", job_flow_overrides=JOB_FLOW_OVERRIDES
    )

    step_adder = EmrAddStepsOperator(
        task_id="add_steps",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_job_flow', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=SPARK_STEPS,
    )

    step_checker = EmrStepSensor(
        task_id="watch_step",
        job_flow_id="{{ task_instance.xcom_pull('create_job_flow', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='add_steps', key='return_value')[0] }}",
        aws_conn_id="aws_default",
    )

    begin >> cluster_creator >> step_adder >> step_checker >> end
