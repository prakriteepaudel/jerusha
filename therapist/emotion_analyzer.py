import re
import logging
from typing import Dict, Any
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """Analyzes emotions and sentiment in user messages using multiple NLP models."""
    
    def __init__(self):
        """Initialize the emotion analyzer with multiple models."""
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Emotion classification model
        try:
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
        except Exception as e:
            logger.warning(f"Could not load emotion classifier: {e}")
            self.emotion_classifier = None
        
        # Sentiment analysis model
        try:
            self.sentiment_classifier = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        except Exception as e:
            logger.warning(f"Could not load sentiment classifier: {e}")
            self.sentiment_classifier = None
        
        # Emotion categories and their descriptions
        self.emotion_categories = {
            'joy': 'positive emotions, happiness, excitement',
            'sadness': 'negative emotions, grief, melancholy',
            'anger': 'frustration, irritation, rage',
            'fear': 'anxiety, worry, nervousness',
            'surprise': 'shock, amazement, unexpected events',
            'disgust': 'aversion, repulsion, dislike',
            'neutral': 'balanced, calm, indifferent'
        }
        
        # Crisis keywords for safety detection
        self.crisis_keywords = {
            'suicide': ['kill myself', 'end it all', 'want to die', 'suicide', 'take my life'],
            'self_harm': ['cut myself', 'hurt myself', 'self harm', 'self-injury'],
            'hopelessness': ['no hope', 'nothing matters', 'give up', 'hopeless'],
            'isolation': ['alone', 'nobody cares', 'no friends', 'isolated'],
            'despair': ['can\'t take it', 'overwhelmed', 'desperate', 'helpless']
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze the emotion and sentiment of the input text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            Dictionary containing emotion analysis results
        """
        if not text or not text.strip():
            return self._get_default_result()
        
        text = text.strip().lower()
        
        # Analyze emotion
        emotion_result = self._analyze_emotion(text)
        
        # Analyze sentiment
        sentiment_result = self._analyze_sentiment(text)
        
        # Check for crisis indicators
        crisis_indicators = self._check_crisis_indicators(text)
        
        return {
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'sentiment_score': sentiment_result['score'],
            'sentiment_label': sentiment_result['label'],
            'crisis_indicators': crisis_indicators,
            'raw_text': text
        }
    
    def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        """Analyze the primary emotion in the text."""
        try:
            if self.emotion_classifier:
                results = self.emotion_classifier(text)
                if results and len(results) > 0:
                    # Get the emotion with highest confidence
                    emotions = results[0]
                    best_emotion = max(emotions, key=lambda x: x['score'])
                    
                    return {
                        'emotion': best_emotion['label'],
                        'confidence': best_emotion['score'],
                        'all_emotions': emotions
                    }
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
        
        # Fallback to keyword-based emotion detection
        return self._fallback_emotion_analysis(text)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment of the text using multiple methods."""
        results = {}
        
        # VADER sentiment analysis
        try:
            vader_scores = self.vader_analyzer.polarity_scores(text)
            results['vader'] = vader_scores
        except Exception as e:
            logger.error(f"VADER analysis error: {e}")
        
        # TextBlob sentiment analysis
        try:
            blob = TextBlob(text)
            results['textblob'] = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"TextBlob analysis error: {e}")
        
        # Transformer-based sentiment analysis
        try:
            if self.sentiment_classifier:
                sentiment_result = self.sentiment_classifier(text)
                if sentiment_result:
                    results['transformer'] = sentiment_result[0]
        except Exception as e:
            logger.error(f"Transformer sentiment analysis error: {e}")
        
        # Combine results
        return self._combine_sentiment_results(results)
    
    def _fallback_emotion_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback emotion analysis using keyword matching."""
        emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'enjoy'],
            'sadness': ['sad', 'depressed', 'lonely', 'empty', 'hopeless', 'miserable'],
            'anger': ['angry', 'frustrated', 'mad', 'irritated', 'annoyed', 'hate'],
            'fear': ['anxious', 'worried', 'scared', 'nervous', 'afraid', 'terrified'],
            'surprise': ['shocked', 'surprised', 'amazed', 'unexpected'],
            'disgust': ['disgusted', 'repulsed', 'sick', 'gross'],
            'neutral': ['okay', 'fine', 'alright', 'normal', 'neutral']
        }
        
        text_words = set(re.findall(r'\b\w+\b', text.lower()))
        
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = len(text_words.intersection(set(keywords)))
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            return {
                'emotion': best_emotion[0],
                'confidence': min(best_emotion[1] / 3.0, 0.9),  # Normalize confidence
                'method': 'keyword_fallback'
            }
        
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'method': 'default'
        }
    
    def _combine_sentiment_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from multiple sentiment analysis methods."""
        combined_score = 0.0
        method_count = 0
        
        # VADER
        if 'vader' in results:
            vader_score = results['vader']['compound']
            combined_score += vader_score
            method_count += 1
        
        # TextBlob
        if 'textblob' in results:
            textblob_score = results['textblob']['polarity']
            combined_score += textblob_score
            method_count += 1
        
        # Transformer
        if 'transformer' in results:
            transformer_result = results['transformer']
            if transformer_result['label'] == 'POSITIVE':
                transformer_score = transformer_result['score']
            elif transformer_result['label'] == 'NEGATIVE':
                transformer_score = -transformer_result['score']
            else:
                transformer_score = 0
            combined_score += transformer_score
            method_count += 1
        
        if method_count > 0:
            final_score = combined_score / method_count
        else:
            final_score = 0.0
        
        # Determine sentiment label
        if final_score > 0.1:
            label = 'Positive'
        elif final_score < -0.1:
            label = 'Negative'
        else:
            label = 'Neutral'
        
        return {
            'score': round(final_score, 3),
            'label': label,
            'methods_used': method_count
        }
    
    def _check_crisis_indicators(self, text: str) -> Dict[str, Any]:
        """Check for crisis indicators in the text."""
        indicators = {}
        text_lower = text.lower()
        
        for crisis_type, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    indicators[crisis_type] = True
                    break
        
        return {
            'has_crisis_indicators': len(indicators) > 0,
            'crisis_types': list(indicators.keys()),
            'severity': len(indicators)
        }
    
    def _get_default_result(self) -> Dict[str, Any]:
        """Return default result when no text is provided."""
        return {
            'emotion': 'neutral',
            'confidence': 0.0,
            'sentiment_score': 0.0,
            'sentiment_label': 'Neutral',
            'crisis_indicators': {'has_crisis_indicators': False, 'crisis_types': [], 'severity': 0},
            'raw_text': ''
        }