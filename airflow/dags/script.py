from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 19),
}

dag = DAG(
    'dvc_and_github_integration',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
)

def extract_data():
    logging.info("Extracting data...")
    urls = ['https://www.dawn.com/', 'https://www.bbc.com/']
    extracted_data = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a')]
        titles = [title.text for title in soup.find_all('h1')]
        extracted_data.append({'url': url, 'links': links, 'titles': titles})
    df = pd.DataFrame(extracted_data)
    df.to_csv('extracted_data.csv', index=False)
    logging.info("Data extraction complete.")

def transform_data():
    logging.info("Transforming data...")
    df = pd.read_csv('extracted_data.csv')
    df['cleaned_titles'] = df['titles'].apply(lambda x: x.strip().lower())
    df.to_csv('transformed_data.csv', index=False)
    logging.info("Data transformation complete.")

def add_and_commit_to_dvc():
    logging.info("Adding and committing data to DVC...")
    add_command = 'dvc add transformed_data.csv'
    os.system(add_command)
    commit_command = 'dvc commit'
    os.system(commit_command)
    logging.info("Data added and committed to DVC.")

def push_to_dvc_remote():
    logging.info("Pushing data to DVC remote...")
    os.system('dvc remote add -d MlopsAssignment02 gdrive://1O7Xmsv_6Qaq4eBtRR2SKsZyEIcYQ-7sy')
    os.system('dvc push')
    logging.info("Data pushed to DVC remote.")

def push_to_github():
    logging.info("Pushing changes to GitHub...")
    os.system('git add. ')
    os.system('git commit -m "Update data"')
    os.system('git push origin master')
    logging.info("Changes pushed to GitHub.")

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

add_to_dvc_task = PythonOperator(
    task_id='add_and_commit_to_dvc',
    python_callable=add_and_commit_to_dvc,
    dag=dag,
)

push_to_dvc_remote_task = PythonOperator(
    task_id='push_to_dvc_remote',
    python_callable=push_to_dvc_remote,
    dag=dag,
)

push_to_github_task = PythonOperator(
    task_id='push_to_github',
    python_callable=push_to_github,
    dag=dag,
)
extract_task >> transform_task >> add_to_dvc_task >> push_to_dvc_remote_task >> push_to_github_task