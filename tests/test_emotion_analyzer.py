import unittest
from unittest.mock import patch, MagicMock
from therapist.emotion_analyzer import EmotionAnalyzer

class TestEmotionAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = EmotionAnalyzer()
    
    def test_analyze_empty_message(self):
        """Test analysis of empty message."""
        result = self.analyzer.analyze("")
        self.assertEqual(result['emotion'], 'neutral')
        self.assertEqual(result['sentiment_score'], 0.0)
        self.assertFalse(result['crisis_indicators']['has_crisis_indicators'])
    
    def test_analyze_sad_message(self):
        """Test analysis of sad message."""
        result = self.analyzer.analyze("I feel so sad and hopeless today")
        self.assertIn(result['emotion'], ['sadness', 'neutral'])
        self.assertLessEqual(result['sentiment_score'], 0)
        self.assertTrue(result['crisis_indicators']['has_crisis_indicators'])
    
    def test_analyze_happy_message(self):
        """Test analysis of happy message."""
        result = self.analyzer.analyze("I'm feeling great and excited today!")
        self.assertIn(result['emotion'], ['joy', 'neutral'])
        self.assertGreaterEqual(result['sentiment_score'], 0)
        self.assertFalse(result['crisis_indicators']['has_crisis_indicators'])
    
    def test_crisis_detection_suicide(self):
        """Test crisis detection for suicide keywords."""
        result = self.analyzer.analyze("I want to kill myself")
        self.assertTrue(result['crisis_indicators']['has_crisis_indicators'])
        self.assertIn('suicide', result['crisis_indicators']['crisis_types'])
    
    def test_crisis_detection_self_harm(self):
        """Test crisis detection for self-harm keywords."""
        result = self.analyzer.analyze("I want to cut myself")
        self.assertTrue(result['crisis_indicators']['has_crisis_indicators'])
        self.assertIn('self_harm', result['crisis_indicators']['crisis_types'])
    
    def test_crisis_detection_hopelessness(self):
        """Test crisis detection for hopelessness keywords."""
        result = self.analyzer.analyze("I have no hope left")
        self.assertTrue(result['crisis_indicators']['has_crisis_indicators'])
        self.assertIn('hopelessness', result['crisis_indicators']['crisis_types'])
    
    def test_fallback_emotion_analysis(self):
        """Test fallback emotion analysis when models fail."""
        with patch.object(self.analyzer, 'emotion_classifier', None):
            result = self.analyzer.analyze("I am very happy")
            self.assertIsNotNone(result['emotion'])
            self.assertIsNotNone(result['confidence'])
    
    def test_sentiment_analysis_negative(self):
        """Test sentiment analysis for negative text."""
        result = self.analyzer.analyze("This is terrible and awful")
        self.assertLessEqual(result['sentiment_score'], 0)
        self.assertEqual(result['sentiment_label'], 'Negative')
    
    def test_sentiment_analysis_positive(self):
        """Test sentiment analysis for positive text."""
        result = self.analyzer.analyze("This is wonderful and amazing")
        self.assertGreaterEqual(result['sentiment_score'], 0)
        self.assertEqual(result['sentiment_label'], 'Positive')
    
    def test_confidence_scoring(self):
        """Test that confidence scores are within valid range."""
        result = self.analyzer.analyze("I am feeling sad")
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)
    
    def test_crisis_keywords_comprehensive(self):
        """Test comprehensive crisis keyword detection."""
        crisis_phrases = [
            "I want to die",
            "Nobody cares about me",
            "I can't take it anymore",
            "Life is not worth living"
        ]
        
        for phrase in crisis_phrases:
            result = self.analyzer.analyze(phrase)
            self.assertTrue(result['crisis_indicators']['has_crisis_indicators'])
    
    def test_normal_message_no_crisis(self):
        """Test that normal messages don't trigger crisis detection."""
        normal_phrases = [
            "I had a good day",
            "The weather is nice",
            "I like pizza",
            "How are you doing?"
        ]
        
        for phrase in normal_phrases:
            result = self.analyzer.analyze(phrase)
            self.assertFalse(result['crisis_indicators']['has_crisis_indicators'])

if __name__ == '__main__':
    unittest.main()