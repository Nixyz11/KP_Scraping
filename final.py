# Import functions from your existing scripts
import  final_scrap

# Call the main function from the imported script

import  final_db 




from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
import sqlite3
SCRIPT_PATH = "kp/scraper/dags/final.py"

# Main function to run the workflow
def main():
    # Step 1: Scrape products
    print("Scraping products...")
    final_scrap.main()

    # Step 2: Upsert products into PostgreSQL
    print("Updating database...")
    final_db.main()

    print("Scraping and database update completed successfully!")

if __name__ == '__main__':
    main()
    
    
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 10),  # Change to the desired start date
    'retries': 1,
}

# Define the DAG
dag = DAG(
    'scraping_dag',  # Name of the DAG
    default_args=default_args,
    description='A DAG to schedule and run the final_scrape.py script',
    schedule_interval='0 6 * * *',  # Runs every day at 6:00 AM, change as needed
    catchup=False,  # Don't backfill past runs
)

# Define tasks
scrape_task = PythonOperator(
    task_id="scrape_products",
    python_callable=final_scrap.main(),
    dag=dag,
)

insert_task = PythonOperator(
    task_id="insert_into_db",
    python_callable=final_db.main(),
    dag=dag,
)

# Set task dependencies
scrape_task >> insert_task    