# Import libraries
import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

# Create Flask App
app = Flask(__name__)

# OpenAI API Key configuration
config = load_dotenv()
client = OpenAI(
    api_key=os.environ.get("API_KEY")
)

# Default route to serve the index.html file
@app.route('/')
def index():
    return render_template('index.html')

# API route to handle POST requests
@app.route('/api', methods=['POST'])
def api():
    try:
        # Get the message from the request's JSON data
        user_message = request.json['message']

        # Send the user's message to OpenAI API
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content":user_message}
            ]
        )

        # Get the generated response from OpenAI
        assistant = completion.choices[0].message.content

        # Return the AI response as JSON
        return jsonify({'message': assistant})

    except Exception as e:
        # Handle any errors and return an error message
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
