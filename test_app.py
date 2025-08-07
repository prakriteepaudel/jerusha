#!/usr/bin/env python3
"""
Test script for Virtual Mental Health Therapist application.
This script tests the core functionality without requiring a full setup.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.emotion_analyzer import EmotionAnalyzer
from src.therapeutic_responder import TherapeuticResponder
from src.conversation_manager import ConversationManager
from src.crisis_detector import CrisisDetector

def test_emotion_analysis():
    """Test emotion analysis functionality"""
    print("🧠 Testing Emotion Analysis...")
    
    analyzer = EmotionAnalyzer()
    
    test_messages = [
        "I feel overwhelmed and can't cope anymore",
        "I'm really happy today and things are going well",
        "I'm so angry at everything right now",
        "I feel empty and nothing matters",
        "I'm excited about my new job!"
    ]
    
    for message in test_messages:
        result = analyzer.analyze(message)
        print(f"Message: '{message[:30]}...'")
        print(f"  Emotion: {result['primary_emotion']} (confidence: {result['confidence']:.2f})")
        print(f"  Sentiment: {result['sentiment_score']:.2f}")
        print(f"  Category: {result['emotion_category']}")
        print()

def test_therapeutic_responses():
    """Test therapeutic response generation"""
    print("💬 Testing Therapeutic Responses...")
    
    responder = TherapeuticResponder()
    responder.initialize()
    
    test_cases = [
        {
            'message': "I feel anxious about everything",
            'emotion_result': {
                'primary_emotion': 'anxiety',
                'sentiment_score': -0.6,
                'emotion_category': 'negative_moderate',
                'confidence': 0.8
            },
            'context': {'interactions': []},
            'crisis_info': {'is_crisis': False}
        },
        {
            'message': "I'm feeling depressed and hopeless", 
            'emotion_result': {
                'primary_emotion': 'depression',
                'sentiment_score': -0.8,
                'emotion_category': 'negative_intense',
                'confidence': 0.9
            },
            'context': {'interactions': []},
            'crisis_info': {'is_crisis': False}
        }
    ]
    
    for case in test_cases:
        response = responder.generate_response(
            case['message'],
            case['emotion_result'],
            case['context'],
            case['crisis_info']
        )
        
        print(f"User: {case['message']}")
        print(f"Emotion: {case['emotion_result']['primary_emotion']}")
        print(f"Response: {response['response'][:100]}...")
        print(f"Technique: {response['technique_used']}")
        print(f"Activities: {response['suggested_activities']}")
        print()

def test_crisis_detection():
    """Test crisis detection functionality"""
    print("🚨 Testing Crisis Detection...")
    
    detector = CrisisDetector()
    
    test_messages = [
        "I want to hurt myself",
        "I feel hopeless and alone",
        "I'm having trouble sleeping",
        "I want to end it all tonight",
        "I'm struggling but I'll be okay"
    ]
    
    for message in test_messages:
        result = detector.check_for_crisis(message)
        print(f"Message: '{message}'")
        print(f"  Crisis: {result['is_crisis']}")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  High-risk keywords: {len(result['high_risk_keywords'])}")
        print(f"  Moderate-risk keywords: {len(result['moderate_risk_keywords'])}")
        print()

def test_conversation_management():
    """Test conversation management"""
    print("💭 Testing Conversation Management...")
    
    manager = ConversationManager()
    
    # Create a session
    session_id = manager.create_session()
    print(f"Created session: {session_id[:8]}...")
    
    # Add some interactions
    test_interactions = [
        ("I'm feeling stressed about work", {'primary_emotion': 'anxiety', 'sentiment_score': -0.5}),
        ("The anxiety is getting worse", {'primary_emotion': 'anxiety', 'sentiment_score': -0.7}),
        ("I can't sleep because of worry", {'primary_emotion': 'anxiety', 'sentiment_score': -0.6})
    ]
    
    for message, emotion_result in test_interactions:
        manager.add_interaction(session_id, message, emotion_result, "Therapeutic response")
    
    # Get context
    context = manager.get_context(session_id)
    print(f"Session duration: {context['session_duration']:.1f} minutes")
    print(f"Interaction count: {context['interaction_count']}")
    print(f"Recent emotions: {context['recent_emotions']}")
    print(f"Themes: {context['conversation_themes']}")
    print(f"Escalation: {context['escalation_indicators']['escalating']}")
    print()

def test_integration():
    """Test integration of all components"""
    print("🔗 Testing Integration...")
    
    # Initialize all components
    analyzer = EmotionAnalyzer()
    responder = TherapeuticResponder()
    responder.initialize()
    manager = ConversationManager()
    detector = CrisisDetector()
    
    # Create session
    session_id = manager.create_session()
    
    # Test message
    user_message = "I feel like I can't keep up with anything anymore"
    
    # Analyze emotion
    emotion_result = analyzer.analyze(user_message)
    
    # Check for crisis
    crisis_info = detector.check_for_crisis(user_message)
    
    # Get context
    context = manager.get_context(session_id)
    
    # Generate response
    response_data = responder.generate_response(
        user_message, emotion_result, context, crisis_info
    )
    
    # Add to conversation
    manager.add_interaction(
        session_id, user_message, emotion_result, response_data['response']
    )
    
    print(f"User: {user_message}")
    print(f"Detected emotion: {emotion_result['primary_emotion']} ({emotion_result['sentiment_score']:.2f})")
    print(f"Crisis detected: {crisis_info['is_crisis']}")
    print(f"Response: {response_data['response'][:100]}...")
    print(f"Suggested activities: {response_data['suggested_activities']}")
    print()

def main():
    """Run all tests"""
    print("🧪 Virtual Mental Health Therapist - Test Suite")
    print("=" * 50)
    
    try:
        test_emotion_analysis()
        test_therapeutic_responses()
        test_crisis_detection()
        test_conversation_management()
        test_integration()
        
        print("✅ All tests completed successfully!")
        print("\n🚀 Ready to run the application with: python app.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())