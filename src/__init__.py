# Virtual Mental Health Therapist - Core Modules
"""
Core modules for the Virtual Mental Health Therapist application.

This package contains:
- EmotionAnalyzer: Sentiment and emotion analysis using BERT, VADER, and TextBlob
- TherapeuticResponder: CBT-based response generation system
- VoiceProcessor: Speech-to-text and text-to-speech functionality
- ConversationManager: Session and context management
- CrisisDetector: Crisis detection and emergency resource management
"""

__version__ = "1.0.0"
__author__ = "Virtual Mental Health Therapist Team"

from .emotion_analyzer import EmotionAnalyzer
from .therapeutic_responder import TherapeuticResponder
from .voice_processor import VoiceProcessor
from .conversation_manager import ConversationManager
from .crisis_detector import CrisisDetector

__all__ = [
    'EmotionAnalyzer',
    'TherapeuticResponder', 
    'VoiceProcessor',
    'ConversationManager',
    'CrisisDetector'
]