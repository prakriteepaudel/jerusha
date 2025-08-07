#!/usr/bin/env python3
"""
Demo script for the Virtual Mental Health Therapist
This script demonstrates the core functionality without running the web server.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from therapist.emotion_analyzer import EmotionAnalyzer
from therapist.response_generator import ResponseGenerator
from therapist.safety_checker import SafetyChecker
from therapist.voice_handler import VoiceHandler

def demo_emotion_analysis():
    """Demonstrate emotion analysis functionality."""
    print("🔍 Testing Emotion Analysis...")
    print("=" * 50)
    
    analyzer = EmotionAnalyzer()
    
    test_messages = [
        "I feel like I can't keep up with anything anymore.",
        "I'm just really tired of everything.",
        "Is it normal to feel this empty every day?",
        "I'm so happy today! Everything is going great!",
        "I'm feeling anxious about my upcoming presentation.",
        "I want to kill myself and end it all."
    ]
    
    for message in test_messages:
        print(f"\n📝 Message: {message}")
        result = analyzer.analyze(message)
        print(f"   Emotion: {result['emotion']}")
        print(f"   Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.3f})")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Crisis Indicators: {result['crisis_indicators']['has_crisis_indicators']}")
        if result['crisis_indicators']['has_crisis_indicators']:
            print(f"   Crisis Types: {result['crisis_indicators']['crisis_types']}")

def demo_response_generation():
    """Demonstrate response generation functionality."""
    print("\n\n💬 Testing Response Generation...")
    print("=" * 50)
    
    generator = ResponseGenerator()
    
    test_scenarios = [
        {
            'message': "I feel so sad and hopeless today",
            'emotion': 'sadness',
            'sentiment_score': -0.8
        },
        {
            'message': "I'm feeling anxious about everything",
            'emotion': 'anxiety',
            'sentiment_score': -0.6
        },
        {
            'message': "I'm so angry at everyone",
            'emotion': 'anger',
            'sentiment_score': -0.7
        },
        {
            'message': "I'm feeling great today!",
            'emotion': 'joy',
            'sentiment_score': 0.8
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📝 User: {scenario['message']}")
        
        emotion_result = {
            'emotion': scenario['emotion'],
            'sentiment_score': scenario['sentiment_score'],
            'confidence': 0.8
        }
        
        response = generator.generate_response(
            scenario['message'], 
            emotion_result, 
            []
        )
        
        print(f"🤖 Therapist: {response['response']}")
        print(f"   Approach: {response['approach_used']}")
        if response['suggestions']:
            print(f"   Suggestions: {', '.join(response['suggestions'])}")

def demo_safety_checking():
    """Demonstrate safety checking functionality."""
    print("\n\n🛡️ Testing Safety Checking...")
    print("=" * 50)
    
    checker = SafetyChecker()
    
    test_messages = [
        "I want to kill myself",
        "I feel like cutting myself",
        "Nobody cares about me",
        "I'm feeling a bit sad today",
        "I had a great day!"
    ]
    
    for message in test_messages:
        print(f"\n📝 Message: {message}")
        result = checker.check_message(message)
        print(f"   Is Crisis: {result['is_crisis']}")
        print(f"   Risk Level: {result['risk_level']}")
        if result['is_crisis']:
            print(f"   Response: {result['response']}")
            if result['emergency_contacts']:
                print(f"   Emergency Contacts: {len(result['emergency_contacts'])} available")

def demo_voice_handler():
    """Demonstrate voice handler functionality."""
    print("\n\n🎤 Testing Voice Handler...")
    print("=" * 50)
    
    handler = VoiceHandler()
    
    print("Voice Handler initialized with:")
    print(f"   Supported formats: {handler.get_supported_formats()}")
    print(f"   TTS Engine available: {handler.tts_engine is not None}")
    print(f"   Google API available: {handler.google_api_key is not None}")
    
    # Test text-to-speech synthesis
    test_text = "Hello, I'm here to support you."
    print(f"\nTesting TTS synthesis for: '{test_text}'")
    
    try:
        audio_data = handler.synthesize_speech(test_text)
        if audio_data:
            print("   ✅ TTS synthesis successful")
            duration = handler.get_audio_duration(audio_data)
            print(f"   Estimated duration: {duration:.2f} seconds")
        else:
            print("   ❌ TTS synthesis failed")
    except Exception as e:
        print(f"   ❌ TTS synthesis error: {e}")

def demo_emergency_contacts():
    """Demonstrate emergency contact functionality."""
    print("\n\n📞 Testing Emergency Contacts...")
    print("=" * 50)
    
    checker = SafetyChecker()
    contacts = checker.get_all_emergency_contacts()
    
    print("Available emergency contacts by country:")
    for country, services in contacts.items():
        print(f"\n🇺🇸 {country}:")
        for service, contact in services.items():
            print(f"   {service}: {contact}")

def main():
    """Run all demos."""
    print("🧠 Virtual Mental Health Therapist - Demo")
    print("=" * 60)
    print("This demo showcases the core functionality of the system.")
    print("Note: This is for demonstration purposes only.")
    print("=" * 60)
    
    try:
        demo_emotion_analysis()
        demo_response_generation()
        demo_safety_checking()
        demo_voice_handler()
        demo_emergency_contacts()
        
        print("\n\n✅ Demo completed successfully!")
        print("\nTo run the full web application:")
        print("   python app.py")
        print("   Then open http://localhost:5000 in your browser")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check that all dependencies are installed:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()