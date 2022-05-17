import argparse

from pyspark.sql import SparkSession

def setup_spark():
    return SparkSession \
        .builder \
        .appName("ExampleTransformations") \
        .config("spark.sql.caseSensitive", True) \
        .enableHiveSupport() \
        .getOrCreate()


def transformation(data_frame):
    return



def function_a (**kwargs):
    spark = setup_spark()

    input_df = spark.read.csv()

    transformation(input_df)

    name = kwargs['name']
    return f'hello {name} !!'
