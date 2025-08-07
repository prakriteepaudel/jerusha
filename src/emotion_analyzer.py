import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import numpy as np
import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """
    Comprehensive emotion and sentiment analysis using multiple models:
    - BERT-based emotion classification
    - VADER sentiment analysis
    - TextBlob sentiment analysis
    """
    
    def __init__(self):
        self.emotion_classifier = None
        self.vader_analyzer = None
        self.emotion_labels = [
            'sadness', 'joy', 'love', 'anger', 'fear', 'surprise', 'anxiety', 
            'depression', 'loneliness', 'overwhelmed', 'hopeful', 'grateful',
            'frustrated', 'confused', 'excited', 'calm', 'worried', 'content'
        ]
        
        # Emotion mapping for better therapeutic understanding
        self.emotion_categories = {
            'negative_intense': ['anger', 'rage', 'fury', 'depression', 'despair', 'anxiety', 'panic', 'overwhelmed'],
            'negative_moderate': ['sadness', 'fear', 'worry', 'loneliness', 'frustrated', 'confused'],
            'neutral': ['calm', 'content', 'peaceful', 'relaxed'],
            'positive_moderate': ['hopeful', 'grateful', 'pleased', 'satisfied'],
            'positive_intense': ['joy', 'love', 'excitement', 'elation', 'euphoria']
        }
        
    def initialize(self):
        """Initialize all the models and analyzers"""
        try:
            logger.info("Loading emotion classification model...")
            
            # Load emotion classification model (using a pre-trained emotion model)
            model_name = "j-hartmann/emotion-english-distilroberta-base"
            self.emotion_classifier = pipeline(
                "text-classification",
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize VADER sentiment analyzer
            logger.info("Initializing VADER sentiment analyzer...")
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            logger.info("Emotion analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing emotion analyzer: {str(e)}")
            # Fallback to basic sentiment analysis only
            self.vader_analyzer = SentimentIntensityAnalyzer()
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '...', text)
        
        # Handle common internet slang and abbreviations
        text = re.sub(r'\bu\b', 'you', text, flags=re.IGNORECASE)
        text = re.sub(r'\bur\b', 'your', text, flags=re.IGNORECASE)
        text = re.sub(r'\bidk\b', "I don't know", text, flags=re.IGNORECASE)
        text = re.sub(r'\btbh\b', 'to be honest', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def analyze_with_bert(self, text: str) -> Dict:
        """Analyze emotion using BERT-based model"""
        try:
            if self.emotion_classifier is None:
                return None
            
            result = self.emotion_classifier(text)
            
            # Get top emotions with confidence scores
            emotions = []
            for item in result:
                emotions.append({
                    'emotion': item['label'].lower(),
                    'confidence': item['score']
                })
            
            return {
                'primary_emotion': emotions[0]['emotion'] if emotions else 'neutral',
                'confidence': emotions[0]['confidence'] if emotions else 0.5,
                'all_emotions': emotions
            }
            
        except Exception as e:
            logger.error(f"Error in BERT emotion analysis: {str(e)}")
            return None
    
    def analyze_with_vader(self, text: str) -> Dict:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            # Determine primary sentiment
            if scores['compound'] >= 0.05:
                sentiment = 'positive'
            elif scores['compound'] <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'compound': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
            
        except Exception as e:
            logger.error(f"Error in VADER analysis: {str(e)}")
            return {'sentiment': 'neutral', 'compound': 0.0}
    
    def analyze_with_textblob(self, text: str) -> Dict:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            
            return {
                'polarity': blob.sentiment.polarity,  # -1 to 1
                'subjectivity': blob.sentiment.subjectivity  # 0 to 1
            }
            
        except Exception as e:
            logger.error(f"Error in TextBlob analysis: {str(e)}")
            return {'polarity': 0.0, 'subjectivity': 0.5}
    
    def detect_crisis_emotions(self, text: str) -> Dict:
        """Detect emotions that might indicate crisis or high distress"""
        crisis_keywords = [
            # Suicidal ideation
            'suicide', 'kill myself', 'end it all', 'not worth living', 'better off dead',
            'want to die', 'end my life', 'take my life', 'hurt myself',
            
            # Self-harm
            'cut myself', 'self harm', 'self-harm', 'hurt myself', 'punish myself',
            
            # Extreme hopelessness
            'no point', 'nothing matters', 'give up', 'hopeless', 'helpless',
            'can\'t go on', 'too much', 'overwhelmed', 'breaking point',
            
            # Panic/severe anxiety
            'panic attack', 'can\'t breathe', 'heart racing', 'going crazy',
            'losing control', 'falling apart'
        ]
        
        text_lower = text.lower()
        detected_keywords = [keyword for keyword in crisis_keywords if keyword in text_lower]
        
        return {
            'crisis_indicators': detected_keywords,
            'crisis_level': 'high' if len(detected_keywords) > 2 else 'moderate' if detected_keywords else 'low'
        }
    
    def get_emotion_category(self, emotion: str) -> str:
        """Categorize emotion for therapeutic response"""
        for category, emotions in self.emotion_categories.items():
            if emotion.lower() in emotions:
                return category
        return 'neutral'
    
    def analyze(self, text: str) -> Dict:
        """
        Comprehensive analysis combining all methods
        
        Returns:
            Dict containing emotion analysis results
        """
        if not text or not text.strip():
            return {
                'primary_emotion': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'emotion_category': 'neutral',
                'analysis_methods': []
            }
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Perform different analyses
        bert_result = self.analyze_with_bert(processed_text)
        vader_result = self.analyze_with_vader(processed_text)
        textblob_result = self.analyze_with_textblob(processed_text)
        crisis_result = self.detect_crisis_emotions(processed_text)
        
        # Combine results
        primary_emotion = 'neutral'
        confidence = 0.5
        sentiment_score = 0.0
        
        if bert_result:
            primary_emotion = bert_result['primary_emotion']
            confidence = bert_result['confidence']
        
        # Use VADER compound score as primary sentiment
        if vader_result:
            sentiment_score = vader_result['compound']
        
        # Override with crisis emotions if detected
        if crisis_result['crisis_level'] in ['moderate', 'high']:
            if crisis_result['crisis_level'] == 'high':
                primary_emotion = 'crisis'
                confidence = 0.9
            else:
                primary_emotion = 'distressed'
                confidence = 0.8
        
        emotion_category = self.get_emotion_category(primary_emotion)
        
        return {
            'primary_emotion': primary_emotion,
            'sentiment_score': sentiment_score,
            'confidence': confidence,
            'emotion_category': emotion_category,
            'vader_analysis': vader_result,
            'textblob_analysis': textblob_result,
            'bert_analysis': bert_result,
            'crisis_analysis': crisis_result,
            'analysis_methods': ['vader', 'textblob'] + (['bert'] if bert_result else [])
        }