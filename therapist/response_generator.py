import random
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates therapeutic responses based on emotion analysis and psychological principles."""
    
    def __init__(self):
        """Initialize the response generator with therapeutic frameworks."""
        self.therapeutic_approaches = {
            'cbt': 'Cognitive Behavioral Therapy',
            'act': 'Acceptance and Commitment Therapy',
            'dbt': 'Dialectical Behavior Therapy',
            'mindfulness': 'Mindfulness-based approaches',
            'validation': 'Emotional validation and support'
        }
        
        # Response templates organized by emotion and approach
        self.response_templates = {
            'sadness': {
                'validation': [
                    "I hear how difficult this is for you. It's completely normal to feel this way.",
                    "Your feelings are valid, and it's okay to not be okay right now.",
                    "I can sense the weight of what you're carrying. You don't have to carry it alone.",
                    "It sounds like you're going through a really tough time. I'm here to listen."
                ],
                'cbt': [
                    "When you're feeling this way, what thoughts are going through your mind?",
                    "Sometimes our thoughts can make difficult situations feel even harder. What's the most challenging thought you're having right now?",
                    "I wonder if there might be another way to look at this situation. What would be the most helpful perspective for you?"
                ],
                'mindfulness': [
                    "Let's take a moment together. Can you notice where you feel this sadness in your body?",
                    "Sometimes just acknowledging our feelings can help. Can you describe what this sadness feels like?",
                    "It's okay to sit with these feelings. You don't have to fix them right now."
                ]
            },
            'anxiety': {
                'validation': [
                    "Anxiety can feel really overwhelming. It's understandable that you're feeling this way.",
                    "Your anxiety is real, and it's okay to feel scared or worried.",
                    "I can see how much this is affecting you. You're not alone in this."
                ],
                'cbt': [
                    "What's the worst thing you're worried might happen? And what's the most likely thing?",
                    "When anxiety hits, it can feel like our thoughts are racing. Can you slow down and tell me what's most concerning you right now?",
                    "Sometimes our anxious thoughts can feel like facts. Let's look at what evidence you have for and against your worries."
                ],
                'mindfulness': [
                    "Let's try a quick grounding exercise. Can you name 5 things you can see right now?",
                    "Take a deep breath with me. Inhale for 4 counts, hold for 4, exhale for 4.",
                    "Your anxiety is like a wave - it will pass. Can you notice it without getting swept away?"
                ]
            },
            'anger': {
                'validation': [
                    "It sounds like you have every right to be frustrated. Your feelings make sense.",
                    "Anger is often a sign that something important to you has been violated. What feels most important to you right now?",
                    "I can hear how upset you are. It's okay to feel angry about this."
                ],
                'cbt': [
                    "When you're feeling this angry, what's the story you're telling yourself about what happened?",
                    "Anger often covers other feelings. Underneath the anger, what else might you be feeling?",
                    "What would be the most helpful way to express this anger constructively?"
                ],
                'mindfulness': [
                    "Anger can feel like fire in the body. Can you notice where you feel it?",
                    "Let's take a moment to breathe. Anger doesn't have to control your actions.",
                    "It's okay to feel angry. The question is, what do you want to do with this energy?"
                ]
            },
            'fear': {
                'validation': [
                    "Fear can be really scary. It's natural to feel this way when things feel uncertain.",
                    "Your fear is real, and it's okay to be afraid. You're not weak for feeling this way.",
                    "I can hear how frightened you are. You don't have to face this alone."
                ],
                'cbt': [
                    "What's the scariest thing you're imagining might happen?",
                    "When you're feeling this afraid, what do you tell yourself about your ability to cope?",
                    "Let's look at what you've survived before. What strengths have helped you through difficult times?"
                ],
                'mindfulness': [
                    "Fear can feel like it's taking over. Can you notice it without getting lost in it?",
                    "Let's ground ourselves. Can you feel your feet on the ground? Your breath in your body?",
                    "Fear is like a storm - intense but temporary. You can weather this."
                ]
            },
            'joy': {
                'validation': [
                    "It's wonderful to hear you're feeling good! What's bringing you this joy?",
                    "I'm so glad you're experiencing this positive moment. Tell me more about it.",
                    "Your happiness is contagious! What's making you feel this way?"
                ],
                'mindfulness': [
                    "Can you really savor this moment? What does this joy feel like in your body?",
                    "This is a beautiful feeling. Can you notice all the details of what's making you happy?",
                    "Joy is precious. How can you hold onto this feeling a little longer?"
                ]
            },
            'neutral': {
                'validation': [
                    "It sounds like you're in a stable place right now. How does that feel?",
                    "Sometimes neutral can be a good place to be. What's on your mind?",
                    "I'm here to listen, whatever you'd like to share."
                ],
                'exploration': [
                    "What would be most helpful for you to talk about right now?",
                    "Is there anything on your mind that you'd like to explore?",
                    "How are you feeling about where you are right now?"
                ]
            }
        }
        
        # Coping strategies and exercises
        self.coping_strategies = {
            'breathing': [
                "Let's try the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8.",
                "Box breathing can help: inhale for 4, hold for 4, exhale for 4, hold for 4.",
                "Take 5 deep breaths with me. Focus on the sensation of breathing."
            ],
            'grounding': [
                "Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, 1 thing you can taste.",
                "Feel your feet on the ground. Notice the weight of your body in your chair.",
                "Look around and name the colors you see. What's the most vibrant color in your environment?"
            ],
            'progressive_relaxation': [
                "Let's relax your body: tense your shoulders for 5 seconds, then release. Notice the difference.",
                "Starting from your toes, tense each muscle group for 5 seconds, then release.",
                "Imagine a wave of relaxation flowing from your head down to your toes."
            ],
            'mindfulness': [
                "Take a moment to just be. Notice your thoughts without judging them.",
                "Focus on your breath. When your mind wanders, gently bring it back.",
                "Can you observe your feelings like clouds passing in the sky?"
            ]
        }
        
        # Self-help suggestions
        self.self_help_suggestions = {
            'journaling': [
                "Writing down your thoughts can help process them. Try free-writing for 10 minutes.",
                "Keep a mood journal to track patterns in your emotions.",
                "Write a letter to yourself from a compassionate friend's perspective."
            ],
            'movement': [
                "Gentle movement can help release tension. Try some light stretching.",
                "A short walk can help clear your mind and shift your mood.",
                "Dance to your favorite song - movement can be medicine."
            ],
            'connection': [
                "Reach out to someone you trust. You don't have to go through this alone.",
                "Consider joining a support group or community where you feel understood.",
                "Sometimes helping others can help us feel better too."
            ],
            'self_care': [
                "What would feel nourishing to you right now? A warm drink, a favorite song, or a cozy blanket?",
                "Small acts of self-care can make a big difference. What feels good to you?",
                "Remember to be kind to yourself. You're doing the best you can."
            ]
        }
    
    def generate_response(self, user_message: str, emotion_result: Dict[str, Any], context: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate a therapeutic response based on the user's message and emotion analysis.
        
        Args:
            user_message: The user's input message
            emotion_result: Results from emotion analysis
            context: Previous conversation context
            
        Returns:
            Dictionary containing the therapeutic response and suggestions
        """
        emotion = emotion_result.get('emotion', 'neutral')
        sentiment_score = emotion_result.get('sentiment_score', 0)
        confidence = emotion_result.get('confidence', 0.5)
        
        # Determine the therapeutic approach based on emotion and context
        approach = self._select_approach(emotion, sentiment_score, context)
        
        # Generate the main response
        response = self._generate_main_response(emotion, approach, user_message, context)
        
        # Generate coping suggestions
        suggestions = self._generate_suggestions(emotion, sentiment_score, context)
        
        # Add crisis awareness if needed
        if emotion_result.get('crisis_indicators', {}).get('has_crisis_indicators', False):
            response += " " + self._add_crisis_support()
        
        return {
            'response': response,
            'suggestions': suggestions,
            'approach_used': approach,
            'emotion_targeted': emotion,
            'confidence': confidence
        }
    
    def _select_approach(self, emotion: str, sentiment_score: float, context: List[Dict] = None) -> str:
        """Select the most appropriate therapeutic approach."""
        if sentiment_score < -0.5:
            # High negative sentiment - focus on validation and support
            return 'validation'
        elif emotion in ['anxiety', 'fear']:
            return 'cbt' if random.random() > 0.5 else 'mindfulness'
        elif emotion == 'anger':
            return 'validation' if random.random() > 0.5 else 'cbt'
        elif emotion == 'sadness':
            return 'validation' if random.random() > 0.6 else 'mindfulness'
        elif emotion == 'joy':
            return 'mindfulness'
        else:
            return 'validation'
    
    def _generate_main_response(self, emotion: str, approach: str, user_message: str, context: List[Dict] = None) -> str:
        """Generate the main therapeutic response."""
        templates = self.response_templates.get(emotion, self.response_templates['neutral'])
        
        if approach in templates:
            responses = templates[approach]
        else:
            responses = templates.get('validation', templates.get('exploration', ["I'm here to listen."]))
        
        # Select a response, avoiding repetition if possible
        if context and len(context) > 0:
            recent_responses = [ctx.get('therapist_response', '') for ctx in context[-3:]]
            available_responses = [r for r in responses if r not in recent_responses]
            if available_responses:
                responses = available_responses
        
        response = random.choice(responses)
        
        # Add personalization based on the user's message
        response = self._personalize_response(response, user_message, emotion)
        
        return response
    
    def _personalize_response(self, response: str, user_message: str, emotion: str) -> str:
        """Personalize the response based on the user's specific message."""
        # Add specific references to what the user said
        if "I feel like" in user_message.lower():
            response = response.replace("this", "what you're experiencing")
        elif "I can't" in user_message.lower():
            response = response.replace("this", "feeling stuck")
        elif "always" in user_message.lower() or "never" in user_message.lower():
            response = response.replace("this", "feeling like this is permanent")
        
        return response
    
    def _generate_suggestions(self, emotion: str, sentiment_score: float, context: List[Dict] = None) -> List[str]:
        """Generate coping strategies and self-help suggestions."""
        suggestions = []
        
        # Add breathing exercises for high distress
        if sentiment_score < -0.3:
            suggestions.append(random.choice(self.coping_strategies['breathing']))
        
        # Add grounding for anxiety/fear
        if emotion in ['anxiety', 'fear']:
            suggestions.append(random.choice(self.coping_strategies['grounding']))
        
        # Add mindfulness for various emotions
        if emotion in ['sadness', 'anger', 'anxiety']:
            suggestions.append(random.choice(self.coping_strategies['mindfulness']))
        
        # Add self-help suggestions
        if sentiment_score < -0.2:
            category = random.choice(['journaling', 'movement', 'connection', 'self_care'])
            suggestions.append(random.choice(self.self_help_suggestions[category]))
        
        return suggestions[:2]  # Limit to 2 suggestions
    
    def _add_crisis_support(self) -> str:
        """Add crisis support message."""
        return ("Remember, you're not alone. If you're having thoughts of harming yourself or others, "
                "please reach out to a crisis helpline or mental health professional immediately. "
                "Your life has value, and there are people who want to help you.")
    
    def get_emergency_contacts(self) -> Dict[str, str]:
        """Get emergency contact information."""
        return {
            'National Suicide Prevention Lifeline (US)': '988',
            'Crisis Text Line': 'Text HOME to 741741',
            'Emergency Services': '911',
            'SAMHSA National Helpline': '1-800-662-HELP (4357)'
        }