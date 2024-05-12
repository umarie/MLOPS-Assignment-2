from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Initialize Google Drive authentication
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 19),
}

dag = DAG(
    'my_dag',
    default_args=default_args,
    schedule_interval='@daily',
)

def extract_data():
    # Extract links and titles from dawn.com and BBC.com
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

def transform_data():
    # Preprocess the extracted data (e.g., clean and format text)
    df = pd.read_csv('extracted_data.csv')
    df['cleaned_titles'] = df['titles'].apply(lambda x: x.strip().lower())
    df.to_csv('transformed_data.csv', index=False)

def store_data():
    # Store the processed data on Google Drive
    file_path = 'transformed_data.csv'
    file = drive.CreateFile({'title': os.path.basename(file_path), 'parents': [{'id': 'u/1/folders/1O7Xmsv_6Qaq4eBtRR2SKsZyEIcYQ-7sy'}]})
    file.SetContentFile(file_path)
    file.Upload()

def add_to_dvc():
    # Command to add data to DVC
    add_command = 'dvc add transformed_data.csv'
    return os.system(add_command)

def commit_to_dvc():
    # Command to commit changes to DVC
    commit_command = 'dvc commit'
    return os.system(commit_command)

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

store_task = PythonOperator(
    task_id='store_data',
    python_callable=store_data,
    dag=dag,
)

add_to_dvc_task = PythonOperator(
    task_id='add_to_dvc',
    python_callable=add_to_dvc,
    dag=dag,
)

commit_to_dvc_task = PythonOperator(
    task_id='commit_to_dvc',
    python_callable=commit_to_dvc,
    dag=dag,
)

extract_task >> transform_task >> store_task >> add_to_dvc_task >> commit_to_dvc_task