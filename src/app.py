# Import libraries
import logging
import os
import re
import uuid
from io import BytesIO

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

# Create Flask App
app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname((__file__)))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir + '\db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
crt_thread = []
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

@app.route('/chat')
def chat():
    threads = get_all_threads()

    thread_chat_history = {thread_id: get_thread_messages(thread_id) for thread_id in threads}

    return render_template('chatting_theme.html', threads=threads, thread_chat_history=thread_chat_history)

@app.route('/interview-bot')
def interview():
    threads = get_all_threads()

    thread_chat_history = {thread_id: get_thread_messages(thread_id) for thread_id in threads}

    return render_template('interview_theme.html', threads=threads, thread_chat_history=thread_chat_history)

@app.route('/image-generator')
def image():
    threads = get_all_threads()

    thread_chat_history = {thread_id: get_thread_messages(thread_id) for thread_id in threads}

    return render_template('image_gen_theme.html', threads=threads, thread_chat_history=thread_chat_history)
@app.route('/speech')
def speech():
    threads = get_all_threads()

    thread_chat_history = {thread_id: get_thread_messages(thread_id) for thread_id in threads}

    return render_template('speech_theme.html', threads=threads, thread_chat_history=thread_chat_history)

@app.route('/audio-to-text')
def audio_transcript():
    threads = get_all_threads()

    thread_chat_history = {thread_id: get_thread_messages(thread_id) for thread_id in threads}

    return render_template('trans_theme.html', threads=threads, thread_chat_history=thread_chat_history)


@app.route('/api/getUuid', methods=['POST'])
def generate_uuid():
    threadId = request.json['uuid']
    return jsonify({'uuid': uuid.uuid5(uuid.NAMESPACE_DNS, threadId)})

@app.route('/api/openAIKeyInput', methods=['POST'])
def get_openai_key():

    key = request.json['key']
    status = check_openai_key(key)
    if status == True:
        new_key = key
        client.api_key = new_key
    else:
        new_key = ""

    app.logger.info(f"OpenAI Key received: {key}")
    return jsonify({'status': status})
# API route to handle POST requests

@app.route('/api/completion', methods=['POST'])
def chat_completion():
    try:
        user_message = request.json['message']
        thread_id = request.json.get('thread_id', 'default')

        save_message(thread_id, 'user', user_message)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=get_thread_messages(thread_id)
        )
        assistant_response = completion.choices[0].message.content

        save_message(thread_id, 'assistant', assistant_response)

        return jsonify({'message': assistant_response, 'thread_id': thread_id, 'chat_history': get_thread_messages(thread_id)})

    except Exception as e:
        return jsonify({'error': str(e)})

def generate_stream():
    with app.app_context():
        try:
            crt_thread = get_thread()
            n = len(crt_thread) - 1
            print(crt_thread)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=get_thread_messages(crt_thread[n]),
                stream=True
            )
            assistant_response =""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    assistant_response += chunk.choices[0].delta.content
                    yield f'data: {chunk.choices[0].delta.content}\n\n'
                else:
                    yield f'data: finisheddd\n\n'
            save_message(crt_thread[n], 'assistant', assistant_response)

        except Exception as e:
            return jsonify({'error': str(e)})

# Route for handling GET requests
@app.route('/api/stream', methods=['GET'])
def chat_stream():
    print("stream open")
    return Response(generate_stream(), mimetype='text/event-stream')


@app.route('/api/stream', methods=['POST'])
def stream():
    try:
        user_message = request.json['message']
        thread_id = request.json.get('thread_id', 'default')
        save_message(thread_id, 'user', user_message)
        # crt_thread = get_thread()
        # crt_thread = save_thread(crt_thread,thread_id)
        save_thread(thread_id)
        return jsonify({'status':'Ok'})

    except Exception as e:
        return jsonify({'error': str(e)})

def save_thread(thread_id):
    # Save a message to the database
    global crt_thread
    crt_thread.append(thread_id)
    #return crt_thread
def get_thread():
    return crt_thread
def get_data_file_path(folder,file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'static',folder)
    return os.path.join(data_dir,file_name)

def train_interview_bot():
    try:
        file = get_data_file_path('file','swe-dataset.jsonl')
        status = client.files.create(
            file=open(file,'rb'),
            purpose='fine-tune'
        )
        print(status.id)  #"file-TkYEPtR7KfEhxQb72JkOfwGu"
        training = client.fine_tuning.jobs.create(
            training_file=status.id,
            model="gpt-3.5-turbo-1106"
        )
        print(training.id) #'ftjob-UXWe9MPTVJWwOxjSjYWFq1fL'
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/interview-bot', methods=['POST'])
def interview_bot():
    # try:
        # train_interview_bot()
    try:
        user_message = request.json['message']
        thread_id = request.json.get('thread_id', 'default')

        save_message(thread_id, 'user', user_message)

        completion = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:personal::8wToPHdf",
            messages=get_thread_messages(thread_id)
        )
        assistant_response = completion.choices[0].message.content
        save_message(thread_id, 'assistant', assistant_response)

        return jsonify({'message': assistant_response, 'thread_id': thread_id, 'chat_history': get_thread_messages(thread_id)})
    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/api/image-generator', methods=['POST'])
def image_generator():
    try:
        user_prompt = request.json['message']
        thread_id = request.json.get('thread_id', 'default')

        save_message(thread_id, 'user', user_prompt)

        gen_image = client.images.generate(
            model="dall-e-3",
            prompt=user_prompt,
            n=1,
            size="1792x1024"
        )
        app.logger.info(f"OpenAI Key id: {client.api_key}")
        assistant_response = gen_image.data[0].url
        print(assistant_response)
        save_message(thread_id,'assistant',assistant_response)

        return jsonify({'message': assistant_response, 'thread_id': thread_id, 'chat_history': get_thread_messages(thread_id)})
    except Exception as e:
        return jsonify({'error': str(e)})
@app.route('/api/speech', methods=['POST'])
def text_to_speech():
    try:
        user_message = request.json['message']
        thread_id = request.json.get('thread_id', 'default')
        save_message(thread_id,'user',user_message)
        tts = client.audio.speech.create(
            model='tts-1',
            voice='nova',
            input=user_message
        )
        output_file = get_data_file_path('audio', 'output.mp3')
        tts.stream_to_file(output_file)
        return jsonify({'message': 'audio/output.mp3', 'thread_id': thread_id, 'chat_history': get_thread_messages(thread_id)})
    except Exception as e:
        jsonify({'error': str(e)})

@app.route('/api/audio-to-text', methods = ['POST'])
def audio_to_text():
    print(request)
    input_file = request.files.get('fileInput')
    thread_id = request.form.get('thread_id','default')

    input_file_path = get_data_file_path('audio', 'input_file.mp3')
    input_file.save(input_file_path)

    transcript_to_text = client.audio.transcriptions.create(
        model="whisper-1",
        file=open(input_file_path, 'rb')
    )
    save_message(thread_id,'assistant',transcript_to_text.text)
    return jsonify({'message': transcript_to_text.text, 'thread_id': thread_id, 'chat_history': get_thread_messages(thread_id)})

if __name__ == '__main__':
    #with app.app_context():
    crt_thread = get_thread()
    app.run(debug=True)
