import os
from dotenv import load_dotenv
import psycopg2
from flask import Flask, request, jsonify
import logging

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'mydatabase'),
    'user': os.getenv('POSTGRES_USER', 'myuser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'mypassword'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': 5432
}


@app.route('/numbers', methods=['POST'])
def number_request():
    """Обрабатывает POST-запрос с числом при соблюдении всех условий:
    - добавляет в базу, если число ранее не было добавлено
    - если в базе нет числа меньше на единицу
    - число натуральное
    """
    try:
        data = request.get_json()

        if not data or 'number' not in data:
            return jsonify({'error': 'You have not entered a number. Enter a number'}), 400

        number = int(data['number'])
        if number <= 0:
            return jsonify({'error': 'The number is not natural'}), 400

        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM numbers WHERE number = %s", (number,))
                if cursor.fetchone():
                    logger.error(f"Error: Number {number} already exists in database.")
                    return jsonify({'error': f"Number {number} already exists in database."}), 400

                cursor.execute("SELECT 1 FROM numbers WHERE number = %s", (number - 1,))
                if cursor.fetchone():
                    logger.error(f"Error: Number {number - 1} already exists in database.")
                    return jsonify({'error': f"Number {number - 1} already exists."}), 400

                cursor.execute("INSERT INTO numbers (number) VALUES (%s)", (number,))
            conn.commit()

        return jsonify({'result': number + 1}), 200

    except ValueError:
        logger.error("Invalid input: Number must be an integer.")
        return jsonify({'error': 'Invalid input: Number must be an integer.'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
