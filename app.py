import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

from therapist.emotion_analyzer import EmotionAnalyzer
from therapist.response_generator import ResponseGenerator
from therapist.voice_handler import VoiceHandler
from therapist.safety_checker import SafetyChecker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
emotion_analyzer = EmotionAnalyzer()
response_generator = ResponseGenerator()
voice_handler = VoiceHandler()
safety_checker = SafetyChecker()

# Store conversation context (in production, use a proper database)
conversation_contexts = {}

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle text-based chat interactions."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Safety check
        safety_result = safety_checker.check_message(user_message)
        if safety_result['is_crisis']:
            return jsonify({
                'response': safety_result['response'],
                'is_crisis': True,
                'emergency_contacts': safety_result['emergency_contacts']
            })
        
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze(user_message)
        
        # Get conversation context
        context = conversation_contexts.get(session_id, [])
        
        # Generate therapeutic response
        response = response_generator.generate_response(
            user_message, 
            emotion_result, 
            context
        )
        
        # Update context
        context.append({
            'user_message': user_message,
            'emotion': emotion_result['emotion'],
            'sentiment': emotion_result['sentiment_score'],
            'therapist_response': response['response'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 exchanges for context
        conversation_contexts[session_id] = context[-10:]
        
        return jsonify({
            'response': response['response'],
            'emotion_detected': emotion_result['emotion'],
            'sentiment_score': emotion_result['sentiment_score'],
            'confidence': emotion_result['confidence'],
            'suggestions': response.get('suggestions', []),
            'is_crisis': False
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/voice/transcribe', methods=['POST'])
def transcribe_voice():
    """Handle voice input transcription."""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        transcribed_text = voice_handler.transcribe_audio(audio_file)
        
        return jsonify({
            'transcribed_text': transcribed_text,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error in voice transcription: {str(e)}")
        return jsonify({'error': 'Voice transcription failed'}), 500

@app.route('/api/voice/synthesize', methods=['POST'])
def synthesize_voice():
    """Generate speech from text response."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        audio_data = voice_handler.synthesize_speech(text)
        
        return jsonify({
            'audio_data': audio_data,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error in voice synthesis: {str(e)}")
        return jsonify({'error': 'Voice synthesis failed'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info('Client connected')
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info('Client disconnected')

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle real-time chat messages via WebSocket."""
    try:
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            emit('error', {'error': 'No message provided'})
            return
        
        # Safety check
        safety_result = safety_checker.check_message(user_message)
        if safety_result['is_crisis']:
            emit('chat_response', {
                'response': safety_result['response'],
                'is_crisis': True,
                'emergency_contacts': safety_result['emergency_contacts']
            })
            return
        
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze(user_message)
        
        # Get conversation context
        context = conversation_contexts.get(session_id, [])
        
        # Generate therapeutic response
        response = response_generator.generate_response(
            user_message, 
            emotion_result, 
            context
        )
        
        # Update context
        context.append({
            'user_message': user_message,
            'emotion': emotion_result['emotion'],
            'sentiment': emotion_result['sentiment_score'],
            'therapist_response': response['response'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 exchanges for context
        conversation_contexts[session_id] = context[-10:]
        
        emit('chat_response', {
            'response': response['response'],
            'emotion_detected': emotion_result['emotion'],
            'sentiment_score': emotion_result['sentiment_score'],
            'confidence': emotion_result['confidence'],
            'suggestions': response.get('suggestions', []),
            'is_crisis': False
        })
        
    except Exception as e:
        logger.error(f"Error in WebSocket chat: {str(e)}")
        emit('error', {'error': 'Internal server error'})

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'emotion_analyzer': 'active',
            'response_generator': 'active',
            'voice_handler': 'active',
            'safety_checker': 'active'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Virtual Mental Health Therapist on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)