# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.urandom(24)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def generate_love_letter(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=30
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating letter: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        unique_id = str(uuid.uuid4())
        image_path = None
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                ext = image.filename.split('.')[-1]
                image_path = f"{unique_id}.{ext}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))

        prompt = f"Write a romantic love letter from {request.form['user_name']} to {request.form['lover_name']}. "
        prompt += f"Include these details: {request.form['special_content']}. Use **bold** for important phrases.and resalt size max 160 words"
        
        love_letter = generate_love_letter(prompt)
        
        return jsonify({
            'success': True,
            'love_letter': love_letter,
            'image_path': image_path
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)