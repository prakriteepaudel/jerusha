#!/usr/bin/env python3
"""
Simplified Demo for Virtual Mental Health Therapist
This version works with basic Python packages to demonstrate core functionality.
"""

import re
import random
from datetime import datetime

class SimpleEmotionAnalyzer:
    """Simplified emotion analyzer using keyword matching."""
    
    def __init__(self):
        self.emotion_keywords = {
            'sadness': ['sad', 'depressed', 'lonely', 'empty', 'hopeless', 'miserable', 'tired', 'exhausted'],
            'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'terrified', 'overwhelmed'],
            'anger': ['angry', 'frustrated', 'mad', 'irritated', 'annoyed', 'hate', 'furious'],
            'joy': ['happy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'enjoy', 'thrilled'],
            'fear': ['fear', 'scared', 'terrified', 'panic', 'dread', 'horrified'],
            'neutral': ['okay', 'fine', 'alright', 'normal', 'neutral', 'stable']
        }
        
        self.crisis_keywords = {
            'suicide': ['kill myself', 'end my life', 'want to die', 'suicide', 'take my life'],
            'self_harm': ['cut myself', 'hurt myself', 'self harm', 'self-injury'],
            'hopelessness': ['no hope', 'nothing matters', 'give up', 'hopeless'],
            'isolation': ['alone', 'nobody cares', 'no friends', 'isolated'],
            'despair': ['can\'t take it', 'overwhelmed', 'desperate', 'helpless']
        }
    
    def analyze(self, text):
        """Analyze emotion and sentiment of text."""
        if not text or not text.strip():
            return self._get_default_result()
        
        text_lower = text.lower().strip()
        
        # Analyze emotion
        emotion_result = self._analyze_emotion(text_lower)
        
        # Analyze sentiment
        sentiment_result = self._analyze_sentiment(text_lower)
        
        # Check for crisis indicators
        crisis_indicators = self._check_crisis_indicators(text_lower)
        
        return {
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'sentiment_score': sentiment_result['score'],
            'sentiment_label': sentiment_result['label'],
            'crisis_indicators': crisis_indicators,
            'raw_text': text_lower
        }
    
    def _analyze_emotion(self, text):
        """Analyze emotion using keyword matching."""
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            return {
                'emotion': best_emotion[0],
                'confidence': min(best_emotion[1] / 3.0, 0.9)
            }
        
        return {
            'emotion': 'neutral',
            'confidence': 0.5
        }
    
    def _analyze_sentiment(self, text):
        """Simple sentiment analysis."""
        positive_words = ['good', 'great', 'wonderful', 'amazing', 'happy', 'love', 'enjoy', 'excited']
        negative_words = ['bad', 'terrible', 'awful', 'sad', 'hate', 'angry', 'frustrated', 'worried']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            score = 0.5
            label = 'Positive'
        elif negative_count > positive_count:
            score = -0.5
            label = 'Negative'
        else:
            score = 0.0
            label = 'Neutral'
        
        return {
            'score': score,
            'label': label
        }
    
    def _check_crisis_indicators(self, text):
        """Check for crisis indicators."""
        indicators = {}
        
        for crisis_type, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    indicators[crisis_type] = True
                    break
        
        return {
            'has_crisis_indicators': len(indicators) > 0,
            'crisis_types': list(indicators.keys()),
            'severity': len(indicators)
        }
    
    def _get_default_result(self):
        """Return default result."""
        return {
            'emotion': 'neutral',
            'confidence': 0.0,
            'sentiment_score': 0.0,
            'sentiment_label': 'Neutral',
            'crisis_indicators': {'has_crisis_indicators': False, 'crisis_types': [], 'severity': 0},
            'raw_text': ''
        }

class SimpleResponseGenerator:
    """Simplified response generator."""
    
    def __init__(self):
        self.response_templates = {
            'sadness': [
                "I hear how difficult this is for you. It's completely normal to feel this way.",
                "Your feelings are valid, and it's okay to not be okay right now.",
                "I can sense the weight of what you're carrying. You don't have to carry it alone.",
                "It sounds like you're going through a really tough time. I'm here to listen."
            ],
            'anxiety': [
                "Anxiety can feel really overwhelming. It's understandable that you're feeling this way.",
                "Your anxiety is real, and it's okay to feel scared or worried.",
                "I can see how much this is affecting you. You're not alone in this."
            ],
            'anger': [
                "It sounds like you have every right to be frustrated. Your feelings make sense.",
                "Anger is often a sign that something important to you has been violated.",
                "I can hear how upset you are. It's okay to feel angry about this."
            ],
            'joy': [
                "It's wonderful to hear you're feeling good! What's bringing you this joy?",
                "I'm so glad you're experiencing this positive moment. Tell me more about it.",
                "Your happiness is contagious! What's making you feel this way?"
            ],
            'neutral': [
                "It sounds like you're in a stable place right now. How does that feel?",
                "Sometimes neutral can be a good place to be. What's on your mind?",
                "I'm here to listen, whatever you'd like to share."
            ]
        }
        
        self.coping_suggestions = {
            'breathing': "Let's try the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8.",
            'grounding': "Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, 1 thing you can taste.",
            'movement': "Gentle movement can help release tension. Try some light stretching.",
            'connection': "Reach out to someone you trust. You don't have to go through this alone."
        }
    
    def generate_response(self, user_message, emotion_result, context=None):
        """Generate therapeutic response."""
        emotion = emotion_result.get('emotion', 'neutral')
        sentiment_score = emotion_result.get('sentiment_score', 0)
        
        # Get response template
        templates = self.response_templates.get(emotion, self.response_templates['neutral'])
        response = random.choice(templates)
        
        # Generate suggestions
        suggestions = []
        if sentiment_score < -0.3:
            suggestions.append(self.coping_suggestions['breathing'])
        if emotion in ['anxiety', 'fear']:
            suggestions.append(self.coping_suggestions['grounding'])
        if sentiment_score < -0.2:
            suggestions.append(random.choice([self.coping_suggestions['movement'], self.coping_suggestions['connection']]))
        
        return {
            'response': response,
            'suggestions': suggestions[:2],
            'approach_used': 'validation',
            'emotion_targeted': emotion,
            'confidence': emotion_result.get('confidence', 0.5)
        }

class SimpleSafetyChecker:
    """Simplified safety checker."""
    
    def __init__(self):
        self.crisis_patterns = {
            'immediate_crisis': {
                'suicide': [r'\b(kill\s+myself|end\s+my\s+life|want\s+to\s+die)\b'],
                'self_harm': [r'\b(cut\s+myself|hurt\s+myself|self\s+harm)\b']
            },
            'high_risk': {
                'hopelessness': [r'\b(no\s+hope|hopeless|nothing\s+matters)\b'],
                'isolation': [r'\b(completely\s+alone|nobody\s+cares)\b']
            }
        }
        
        self.emergency_contacts = {
            'National Suicide Prevention Lifeline (US)': '988',
            'Crisis Text Line': 'Text HOME to 741741',
            'Emergency Services': '911'
        }
    
    def check_message(self, message):
        """Check message for crisis indicators."""
        if not message or not message.strip():
            return self._get_safe_response()
        
        message_lower = message.lower().strip()
        
        # Check for crisis indicators
        crisis_results = self._detect_crisis_indicators(message_lower)
        risk_level = self._determine_risk_level(crisis_results)
        
        return self._generate_safety_response(risk_level, crisis_results)
    
    def _detect_crisis_indicators(self, message):
        """Detect crisis indicators."""
        detected_crises = {}
        
        for risk_level, categories in self.crisis_patterns.items():
            detected_crises[risk_level] = {}
            
            for category, patterns in categories.items():
                detected_crises[risk_level][category] = []
                
                for pattern in patterns:
                    matches = re.findall(pattern, message, re.IGNORECASE)
                    if matches:
                        detected_crises[risk_level][category].extend(matches)
        
        return detected_crises
    
    def _determine_risk_level(self, crisis_results):
        """Determine risk level."""
        if crisis_results.get('immediate_crisis'):
            for category, matches in crisis_results['immediate_crisis'].items():
                if matches:
                    return 'immediate_crisis'
        
        if crisis_results.get('high_risk'):
            for category, matches in crisis_results['high_risk'].items():
                if matches:
                    return 'high_risk'
        
        return 'safe'
    
    def _generate_safety_response(self, risk_level, crisis_results):
        """Generate safety response."""
        if risk_level == 'safe':
            return self._get_safe_response()
        
        if risk_level == 'immediate_crisis':
            response = (
                "I'm very concerned about what you're sharing. Your life has value and you deserve help. "
                "Please reach out to a crisis helpline immediately - they have trained professionals who can help you right now. "
                "You don't have to go through this alone."
            )
        else:
            response = (
                "I hear how much pain you're in, and I'm worried about you. "
                "These feelings are serious and you deserve professional support. "
                "Please consider reaching out to a mental health professional or crisis helpline. "
                "You're not alone in this."
            )
        
        return {
            'is_crisis': True,
            'risk_level': risk_level,
            'response': response,
            'emergency_contacts': self.emergency_contacts,
            'detected_crises': crisis_results
        }
    
    def _get_safe_response(self):
        """Return safe response."""
        return {
            'is_crisis': False,
            'risk_level': 'safe',
            'response': '',
            'emergency_contacts': {},
            'detected_crises': {}
        }

def demo_emotion_analysis():
    """Demonstrate emotion analysis functionality."""
    print("🔍 Testing Emotion Analysis...")
    print("=" * 50)
    
    analyzer = SimpleEmotionAnalyzer()
    
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
    
    generator = SimpleResponseGenerator()
    
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
    
    checker = SimpleSafetyChecker()
    
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

def demo_conversation():
    """Demonstrate a full conversation flow."""
    print("\n\n💭 Testing Full Conversation Flow...")
    print("=" * 50)
    
    analyzer = SimpleEmotionAnalyzer()
    generator = SimpleResponseGenerator()
    checker = SimpleSafetyChecker()
    
    conversation = [
        "I feel like I can't keep up with anything anymore.",
        "I'm just really tired of everything.",
        "Is it normal to feel this empty every day?",
        "I want to kill myself and end it all."
    ]
    
    for i, user_message in enumerate(conversation, 1):
        print(f"\n--- Turn {i} ---")
        print(f"👤 User: {user_message}")
        
        # Safety check
        safety_result = checker.check_message(user_message)
        if safety_result['is_crisis']:
            print(f"🚨 CRISIS DETECTED: {safety_result['response']}")
            if safety_result['emergency_contacts']:
                print("📞 Emergency Contacts:")
                for service, contact in safety_result['emergency_contacts'].items():
                    print(f"   {service}: {contact}")
            break
        
        # Emotion analysis
        emotion_result = analyzer.analyze(user_message)
        print(f"🔍 Analysis: {emotion_result['emotion']} ({emotion_result['sentiment_label']})")
        
        # Generate response
        response = generator.generate_response(user_message, emotion_result, [])
        print(f"🤖 Therapist: {response['response']}")
        
        if response['suggestions']:
            print(f"💡 Suggestions: {', '.join(response['suggestions'])}")

def main():
    """Run all demos."""
    print("🧠 Virtual Mental Health Therapist - Simple Demo")
    print("=" * 60)
    print("This demo showcases the core functionality using simplified components.")
    print("Note: This is for demonstration purposes only.")
    print("=" * 60)
    
    try:
        demo_emotion_analysis()
        demo_response_generation()
        demo_safety_checking()
        demo_conversation()
        
        print("\n\n✅ Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("   ✅ Emotion Analysis")
        print("   ✅ Sentiment Analysis")
        print("   ✅ Crisis Detection")
        print("   ✅ Therapeutic Response Generation")
        print("   ✅ Safety Monitoring")
        print("   ✅ Emergency Contact Provision")
        
        print("\nTo run the full web application with advanced features:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run the app: python app.py")
        print("   3. Open http://localhost:5000 in your browser")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main()