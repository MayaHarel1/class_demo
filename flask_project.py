from flask import Flask, request, jsonify, render_template
import sqlite3
from discord_webhook import DiscordWebhook
from datetime import datetime, timedelta

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1356223633130913904/iwPhVR_0D9LI3WoivFYyfBiwUuftFNXlWculrVB38WyMlXEl2JCPTRpOtTj-enWxvg7f"

def get_db_connection():
    conn = sqlite3.connect('messages.db')
    conn.row_factory = sqlite3.Row
    return conn

# Database setup
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def send_to_discord(text):
    webhook = DiscordWebhook(
        url=DISCORD_WEBHOOK_URL,
        content=text)
    webhook.execute()

def save_to_database(text):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now()
    cursor.execute('INSERT INTO messages (content, timestamp) VALUES(?, ?)',
                   (text, timestamp))
    conn.commit()
    conn.close()


# input text
@app.route('/input_text', methods=['POST'])
def input_text():
    try:
        data = request.form
        text = data['text']
        # if text does not exist or not a string
        if not text or not isinstance(text, str):
            return jsonify({"status": "error", "message": "Invalid input"}), 400
        # Send text to Discord server
        send_to_discord(text)
        # Save text to SQLite database
        save_to_database(text)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# get messages
@app.route('/get_messages', methods=['GET'])
def get_messages():
    try:
        cutoff_time = datetime.now() - timedelta(minutes=30)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT content, timestamp FROM messages WHERE timestamp > ?', (cutoff_time,))
        messages = cursor.fetchall()
        conn.close()
        return jsonify({"status": "success", "messages":
        [{"content": row['content'], "timestamp": row['timestamp']}
        for row in messages]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Serve HTML Page
@app.route('/')
def index():
    return render_template('index.html')

# Initialize database and run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=40000)