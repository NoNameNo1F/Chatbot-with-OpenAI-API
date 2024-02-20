# Import libraries
import logging
import os
import re
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

from utils.helpers import *

# Create Flask App
app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname((__file__)))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir + 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)

def save_message(thread_id, role, content):
    # Save a message to the database
    message = ChatMessage(thread_id=thread_id, role=role, content=content)
    db.session.add(message)
    db.session.commit()

def get_thread_messages(thread_id):
    # Get all messages for a specific thread from the database
    messages = ChatMessage.query.filter_by(thread_id=thread_id).all()
    return [{'role': message.role, 'content': message.content} for message in messages]

def get_all_threads():
    # Get all unique thread IDs from the database and sort them in a natural order
    threads = sorted(set(message.thread_id for message in ChatMessage.query.all()), key=lambda x: [int(s) if s.isdigit() else s for s in re.split('([0-9]+)', x)])
    threads.pop(0)
    return threads
def check_openai_key(key):
    test = OpenAI(api_key=key)
    try:
        test.models.list()
    except Exception as e:
        app.logger.error(f"{e}")
        return False
    else:
        return True

with app.app_context():
    db.create_all()

config = load_dotenv()
API_KEY = None
client = OpenAI(
    api_key=os.environ.get("API_KEY")
)


@app.route('/')
def index():

    threads = get_all_threads()

    thread_chat_history = {thread_id: get_thread_messages(thread_id) for thread_id in threads}

    return render_template('index.html', threads=threads, thread_chat_history=thread_chat_history)

@app.route('/api/openAIKeyInput', methods=['POST'])
def get_openai_key():

    key = request.json['key']
    status = check_openai_key(key)
    if status == True:
        API_KEY = key
        client.api_key = API_KEY
    else:
        API_KEY = ""

    app.logger.info(f"OpenAI Key received: {key}")
    return jsonify({'status': status})
# API route to handle POST requests
@app.route('/api', methods=['POST'])
def chat_completion():
    try:
        user_message = request.json['message']
        thread_id = request.json.get('thread_id', 'default')

        save_message(thread_id, 'user', user_message)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=get_thread_messages(thread_id)
        )
        assistant_response = completion.choices[-1].message.content

        save_message(thread_id, 'assistant', assistant_response)

        return jsonify({'message': assistant_response, 'thread_id': thread_id, 'chat_history': get_thread_messages(thread_id)})

    except Exception as e:
        return jsonify({'error': str(e)})

# @app.route('/api/history', methods=['POST'])
# def get_history():
#     try:
#         thread_id = request.json.get('thread_id', 'default')

#         chat_history = get_thread_messages(thread_id)
#         return jsonify({'chat_history': chat_history, 'thread_id': thread_id})

#     except Exception as e:
#         return jsonify({'error': str(e)})

# @app.route('/api/history/<thread_id>', methods=['GET'])
# def get_thread_chat_history(thread_id):
#     try:
#         # Fetch and return chat history for the thread
#         chat_history = get_thread_messages(thread_id)
#         return jsonify({'chat_history': chat_history, 'thread_id': thread_id})

#     except Exception as e:
#         # Handle any errors and return an error message
#         return jsonify({'error': str(e)})

@app.route('/api/getUuid', methods=['POST'])
def generateUuid():
    threadId = request.json['uuid']
    return jsonify({'uuid': uuid.uuid5(uuid.NAMESPACE_DNS, threadId)})

if __name__ == '__main__':
    app.run(debug=True)
