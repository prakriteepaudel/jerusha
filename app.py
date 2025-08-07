from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import uuid

# Import our custom modules
from src.emotion_analyzer import EmotionAnalyzer
from src.therapeutic_responder import TherapeuticResponder
from src.voice_processor import VoiceProcessor
from src.conversation_manager import ConversationManager
from src.crisis_detector import CrisisDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
emotion_analyzer = EmotionAnalyzer()
therapeutic_responder = TherapeuticResponder()
voice_processor = VoiceProcessor()
conversation_manager = ConversationManager()
crisis_detector = CrisisDetector()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/analyze', methods=['POST'])
def analyze_message():
    """Main endpoint for analyzing user messages and generating responses"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Log the interaction (anonymized)
        logger.info(f"Processing message for session: {session_id[:8]}...")
        
        # Check for crisis indicators
        crisis_info = crisis_detector.check_for_crisis(user_message)
        
        # Analyze emotion and sentiment
        emotion_result = emotion_analyzer.analyze(user_message)
        
        # Get conversation context
        context = conversation_manager.get_context(session_id)
        
        # Generate therapeutic response
        response_data = therapeutic_responder.generate_response(
            user_message=user_message,
            emotion_result=emotion_result,
            context=context,
            crisis_info=crisis_info
        )
        
        # Update conversation history
        conversation_manager.add_interaction(
            session_id=session_id,
            user_message=user_message,
            emotion_result=emotion_result,
            response=response_data['response']
        )
        
        # Prepare response
        result = {
            "session_id": session_id,
            "emotion_detected": emotion_result['primary_emotion'],
            "sentiment_score": emotion_result['sentiment_score'],
            "confidence": emotion_result['confidence'],
            "empathetic_response": response_data['response'],
            "suggested_activities": response_data.get('suggested_activities', []),
            "breathing_exercise": response_data.get('breathing_exercise'),
            "crisis_detected": crisis_info['is_crisis'],
            "emergency_resources": crisis_info.get('resources', []) if crisis_info['is_crisis'] else None,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": "An error occurred processing your message"}), 500

@app.route('/api/voice/process', methods=['POST'])
def process_voice():
    """Process voice input and return text"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        text = voice_processor.speech_to_text(audio_file)
        
        return jsonify({"text": text})
        
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        return jsonify({"error": "Error processing voice input"}), 500

@app.route('/api/voice/synthesize', methods=['POST'])
def synthesize_speech():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400
        
        audio_data = voice_processor.text_to_speech(text)
        
        return jsonify({"audio_data": audio_data})
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        return jsonify({"error": "Error generating speech"}), 500

@app.route('/api/exercises/breathing')
def get_breathing_exercise():
    """Get a breathing exercise"""
    try:
        exercise = therapeutic_responder.get_breathing_exercise()
        return jsonify(exercise)
    except Exception as e:
        logger.error(f"Error getting breathing exercise: {str(e)}")
        return jsonify({"error": "Error loading breathing exercise"}), 500

@app.route('/api/resources/crisis')
def get_crisis_resources():
    """Get crisis support resources"""
    try:
        resources = crisis_detector.get_crisis_resources()
        return jsonify(resources)
    except Exception as e:
        logger.error(f"Error getting crisis resources: {str(e)}")
        return jsonify({"error": "Error loading crisis resources"}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected")
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected")

@socketio.on('message')
def handle_message(data):
    """Handle real-time message processing"""
    try:
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Process the message (similar to the REST endpoint)
        emotion_result = emotion_analyzer.analyze(user_message)
        context = conversation_manager.get_context(session_id)
        crisis_info = crisis_detector.check_for_crisis(user_message)
        
        response_data = therapeutic_responder.generate_response(
            user_message=user_message,
            emotion_result=emotion_result,
            context=context,
            crisis_info=crisis_info
        )
        
        conversation_manager.add_interaction(
            session_id=session_id,
            user_message=user_message,
            emotion_result=emotion_result,
            response=response_data['response']
        )
        
        result = {
            "emotion_detected": emotion_result['primary_emotion'],
            "sentiment_score": emotion_result['sentiment_score'],
            "empathetic_response": response_data['response'],
            "suggested_activities": response_data.get('suggested_activities', []),
            "crisis_detected": crisis_info['is_crisis']
        }
        
        emit('response', result)
        
    except Exception as e:
        logger.error(f"Error in WebSocket message handling: {str(e)}")
        emit('error', {'message': 'An error occurred processing your message'})

if __name__ == '__main__':
    # Initialize models on startup
    logger.info("Initializing Virtual Mental Health Therapist...")
    
    try:
        emotion_analyzer.initialize()
        therapeutic_responder.initialize()
        logger.info("All components initialized successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)