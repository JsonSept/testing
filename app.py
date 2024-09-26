from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# MySQL database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML file

@app.route('/store_qr_data', methods=['POST'])
def store_qr_data():
    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (first_name, last_name, department) VALUES (%s, %s, %s)",
            (data['first_name'], data['last_name'], data['department'])
        )
        connection.commit()
        return jsonify({"message": "QR data stored successfully", "id": cursor.lastrowid}), 200
    except Exception as error:
        print("Error storing QR data:", error)
        return jsonify({"message": f"Error storing QR data: {str(error)}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/kill', methods=['DELETE'])
def delete_user():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')

    if not first_name or not last_name:
        return jsonify({"message": "Both first name and last name are required"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM users WHERE first_name = %s AND last_name = %s', (first_name, last_name))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as error:
        print("Error deleting user:", error)
        return jsonify({"message": f"Error deleting user: {str(error)}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/qrcode', methods=['GET'])
def check_user_existence():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')

    if not first_name or not last_name:
        return jsonify({"message": "Both first name and last name are required"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE first_name = %s AND last_name = %s', (first_name, last_name))
        count = cursor.fetchone()[0]
        return jsonify({"exists": count > 0}), 200
    except Exception as error:
        print("Error checking user existence:", error)
        return jsonify({"message": f"Error checking user existence: {str(error)}"}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 9900)))
