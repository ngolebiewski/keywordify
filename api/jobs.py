from flask import Blueprint, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM job_descriptions")
        
        # Fetch all records
        jobs = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        connection.close()
        
        # Return JSON response
        return jsonify(jobs)
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500