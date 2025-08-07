import random
import logging
from typing import Dict, List, Optional
import json
import re

logger = logging.getLogger(__name__)

class TherapeuticResponder:
    """
    Generate therapeutic responses based on CBT principles and active listening.
    Provides empathetic, non-judgmental, and supportive responses.
    """
    
    def __init__(self):
        self.cbt_techniques = {
            'thought_challenging': [
                "I hear that you're having some difficult thoughts. Sometimes our minds can be quite harsh with us. What evidence do you have for and against this thought?",
                "That sounds like a really challenging thought to be having. Let's explore this together - is this thought helping you or making things harder?",
                "It sounds like you're going through a tough time with these thoughts. What would you tell a good friend who was having the same thought?"
            ],
            'emotional_validation': [
                "Your feelings are completely valid and understandable given what you're going through.",
                "It makes complete sense that you would feel this way. Thank you for sharing something so personal with me.",
                "What you're experiencing sounds really difficult, and it's okay to feel overwhelmed by it.",
                "I can hear how much pain you're in right now, and I want you to know that your feelings matter."
            ],
            'behavioral_activation': [
                "When we're feeling this way, sometimes small actions can help. Is there one tiny thing you could do today that might bring you a moment of comfort?",
                "It sounds like you're in a difficult place right now. Sometimes gentle movement or activity can help. What's one small thing you used to enjoy?",
                "Depression and anxiety can make everything feel impossible. What's the smallest step you could take today toward caring for yourself?"
            ],
            'mindfulness': [
                "Right now, in this moment, you're here and you're safe. Can you take a deep breath with me?",
                "Let's try to ground ourselves in the present moment. Can you notice three things you can see around you right now?",
                "When our minds are racing, sometimes it helps to come back to our breath. Would you like to try a brief breathing exercise together?"
            ],
            'hope_instillation': [
                "I hear how difficult things are for you right now. Feelings, even the most painful ones, are temporary and can change.",
                "You've made it through difficult times before, and while this feels overwhelming, you have strength within you.",
                "It takes courage to reach out and share how you're feeling. That's already a step toward healing."
            ]
        }
        
        self.emotion_specific_responses = {
            'anxiety': {
                'acknowledgment': [
                    "I can hear how anxious you're feeling right now. Anxiety can be so overwhelming.",
                    "That sounds like a really anxious experience. Your feelings are completely valid.",
                    "Anxiety can make everything feel so much more intense and scary than it really is."
                ],
                'techniques': [
                    "anxiety_grounding", "breathing_exercise", "thought_challenging"
                ],
                'suggestions': [
                    "grounding exercises", "deep breathing", "progressive muscle relaxation", "mindful observation"
                ]
            },
            'depression': {
                'acknowledgment': [
                    "I hear how heavy and difficult everything feels for you right now.",
                    "Depression can make even the simplest things feel impossible. Thank you for sharing with me.",
                    "It sounds like you're going through a really dark time. I'm here to listen and support you."
                ],
                'techniques': [
                    "behavioral_activation", "thought_challenging", "emotional_validation"
                ],
                'suggestions': [
                    "gentle movement", "sunlight exposure", "connecting with one person", "one small self-care act"
                ]
            },
            'anger': {
                'acknowledgment': [
                    "I can hear how frustrated and angry you're feeling. Those are really intense emotions to carry.",
                    "It sounds like something has really upset you. Your anger is telling us something important.",
                    "Anger can be so overwhelming. It sounds like you're dealing with something really challenging."
                ],
                'techniques': [
                    "emotional_validation", "mindfulness", "thought_challenging"
                ],
                'suggestions': [
                    "physical release like walking", "journaling your feelings", "cooling down techniques", "talking it through"
                ]
            },
            'sadness': {
                'acknowledgment': [
                    "I can hear the sadness in what you're sharing. It sounds really painful.",
                    "Sadness can feel so heavy and consuming. Thank you for trusting me with this.",
                    "It sounds like you're going through something that's causing you a lot of pain."
                ],
                'techniques': [
                    "emotional_validation", "hope_instillation", "behavioral_activation"
                ],
                'suggestions': [
                    "gentle self-compassion", "reaching out to someone you trust", "creative expression", "comforting activities"
                ]
            },
            'loneliness': {
                'acknowledgment': [
                    "Loneliness can be one of the most painful feelings to experience. I hear you.",
                    "Feeling disconnected and alone is so difficult. Thank you for reaching out here.",
                    "The feeling of loneliness can be overwhelming. You're not alone in feeling this way."
                ],
                'techniques': [
                    "emotional_validation", "behavioral_activation", "hope_instillation"
                ],
                'suggestions': [
                    "reaching out to one person", "joining an online community", "volunteering", "self-compassion practices"
                ]
            },
            'overwhelmed': {
                'acknowledgment': [
                    "It sounds like you have so much on your plate right now. Feeling overwhelmed makes complete sense.",
                    "When everything feels like too much, it's natural to feel overwhelmed and stressed.",
                    "I can hear how much you're juggling right now. That feeling of being overwhelmed is so valid."
                ],
                'techniques': [
                    "mindfulness", "thought_challenging", "behavioral_activation"
                ],
                'suggestions': [
                    "breaking tasks into tiny steps", "prioritizing just one thing", "asking for help", "taking breaks"
                ]
            }
        }
        
        self.breathing_exercises = [
            {
                'name': '4-7-8 Breathing',
                'description': 'A calming breath technique to reduce anxiety',
                'instructions': [
                    'Sit comfortably and exhale completely',
                    'Breathe in through your nose for 4 counts',
                    'Hold your breath for 7 counts',
                    'Exhale through your mouth for 8 counts',
                    'Repeat this cycle 3-4 times'
                ],
                'duration': '2-3 minutes'
            },
            {
                'name': 'Box Breathing',
                'description': 'A structured breathing pattern to promote calm',
                'instructions': [
                    'Sit with your back straight and feet on the floor',
                    'Breathe in through your nose for 4 counts',
                    'Hold your breath for 4 counts',
                    'Exhale through your mouth for 4 counts',
                    'Hold empty for 4 counts',
                    'Repeat for several cycles'
                ],
                'duration': '3-5 minutes'
            },
            {
                'name': 'Belly Breathing',
                'description': 'Deep diaphragmatic breathing for relaxation',
                'instructions': [
                    'Place one hand on your chest, one on your belly',
                    'Breathe slowly through your nose',
                    'Feel your belly rise more than your chest',
                    'Exhale slowly through your mouth',
                    'Focus on the gentle rise and fall',
                    'Continue for several minutes'
                ],
                'duration': '5-10 minutes'
            }
        ]
        
        self.coping_strategies = {
            'grounding_techniques': [
                "Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste",
                "Hold an ice cube or splash cold water on your face",
                "Focus on your feet on the ground and take slow, deep breaths",
                "Describe your surroundings in detail to yourself"
            ],
            'self_soothing': [
                "Take a warm bath or shower",
                "Listen to calming music or nature sounds",
                "Wrap yourself in a soft blanket",
                "Practice gentle self-massage",
                "Make yourself a warm, comforting drink"
            ],
            'cognitive_techniques': [
                "Write down your thoughts and examine the evidence for and against them",
                "Ask yourself: 'What would I tell a friend in this situation?'",
                "Consider: 'Will this matter in 5 years?'",
                "Practice the 'Best Friend' technique - be as kind to yourself as you would to a best friend"
            ],
            'physical_release': [
                "Go for a gentle walk, even if just around your room",
                "Do some stretching or yoga",
                "Dance to your favorite song",
                "Try progressive muscle relaxation"
            ]
        }
    
    def initialize(self):
        """Initialize any models or resources needed"""
        logger.info("Therapeutic responder initialized")
    
    def select_cbt_technique(self, emotion: str, emotion_category: str) -> str:
        """Select appropriate CBT technique based on emotion"""
        if emotion in self.emotion_specific_responses:
            techniques = self.emotion_specific_responses[emotion]['techniques']
            return random.choice(techniques)
        
        # Default technique based on emotion category
        if emotion_category == 'negative_intense':
            return 'emotional_validation'
        elif emotion_category == 'negative_moderate':
            return 'thought_challenging'
        else:
            return 'mindfulness'
    
    def generate_acknowledgment(self, emotion: str, user_message: str) -> str:
        """Generate empathetic acknowledgment of user's emotion"""
        if emotion in self.emotion_specific_responses:
            acknowledgments = self.emotion_specific_responses[emotion]['acknowledgment']
            return random.choice(acknowledgments)
        
        # Generic empathetic responses
        generic_responses = [
            "I hear that you're going through a difficult time right now.",
            "Thank you for sharing something so personal with me. I'm here to listen.",
            "It sounds like you're dealing with some challenging feelings.",
            "What you're experiencing sounds really difficult."
        ]
        return random.choice(generic_responses)
    
    def generate_cbt_intervention(self, technique: str, emotion: str) -> str:
        """Generate CBT-based intervention"""
        if technique in self.cbt_techniques:
            return random.choice(self.cbt_techniques[technique])
        return "Let's work through this together. You don't have to face this alone."
    
    def suggest_coping_strategies(self, emotion: str, context: Dict) -> List[str]:
        """Suggest appropriate coping strategies"""
        if emotion in self.emotion_specific_responses:
            return self.emotion_specific_responses[emotion]['suggestions']
        
        # Default suggestions
        return ["deep breathing", "grounding exercises", "self-compassion", "reaching out for support"]
    
    def generate_response(self, user_message: str, emotion_result: Dict, 
                         context: Dict, crisis_info: Dict) -> Dict:
        """
        Generate comprehensive therapeutic response
        
        Args:
            user_message: The user's input message
            emotion_result: Results from emotion analysis
            context: Conversation context
            crisis_info: Crisis detection results
            
        Returns:
            Dict containing response and suggested activities
        """
        emotion = emotion_result.get('primary_emotion', 'neutral')
        emotion_category = emotion_result.get('emotion_category', 'neutral')
        sentiment_score = emotion_result.get('sentiment_score', 0.0)
        
        # Handle crisis situations first
        if crisis_info.get('is_crisis', False):
            return self._generate_crisis_response(user_message, emotion_result, crisis_info)
        
        # Generate main response components
        acknowledgment = self.generate_acknowledgment(emotion, user_message)
        
        # Select and apply CBT technique
        technique = self.select_cbt_technique(emotion, emotion_category)
        intervention = self.generate_cbt_intervention(technique, emotion)
        
        # Add context-aware elements
        context_element = self._add_contextual_element(context, emotion)
        
        # Suggest activities
        suggested_activities = self.suggest_coping_strategies(emotion, context)
        
        # Choose breathing exercise
        breathing_exercise = random.choice(self.breathing_exercises)
        
        # Construct response
        response_parts = [acknowledgment]
        
        if context_element:
            response_parts.append(context_element)
        
        response_parts.append(intervention)
        
        # Add encouraging closing
        closing = self._generate_encouraging_closing(emotion, sentiment_score)
        response_parts.append(closing)
        
        full_response = " ".join(response_parts)
        
        return {
            'response': full_response,
            'technique_used': technique,
            'suggested_activities': suggested_activities[:3],  # Limit to 3 suggestions
            'breathing_exercise': breathing_exercise,
            'emotion_addressed': emotion
        }
    
    def _generate_crisis_response(self, user_message: str, emotion_result: Dict, crisis_info: Dict) -> Dict:
        """Generate response for crisis situations"""
        crisis_response = (
            "I'm really concerned about you and what you're going through right now. "
            "Your life has value, and there are people who want to help you through this difficult time. "
            "Please consider reaching out to a crisis helpline or emergency services if you're in immediate danger. "
            "You don't have to go through this alone."
        )
        
        return {
            'response': crisis_response,
            'technique_used': 'crisis_intervention',
            'suggested_activities': ['contact_crisis_line', 'reach_out_to_trusted_person', 'seek_immediate_help'],
            'breathing_exercise': self.breathing_exercises[0],  # Simple breathing for crisis
            'emotion_addressed': 'crisis',
            'requires_immediate_attention': True
        }
    
    def _add_contextual_element(self, context: Dict, emotion: str) -> Optional[str]:
        """Add contextual elements based on conversation history"""
        if not context or not context.get('interactions'):
            return None
        
        # Check for patterns in recent interactions
        recent_emotions = [interaction.get('emotion', {}).get('primary_emotion') 
                          for interaction in context.get('interactions', [])[-3:]]
        
        if len(recent_emotions) > 1 and all(e in ['sadness', 'depression', 'hopelessness'] for e in recent_emotions):
            return "I've noticed we've been talking about some heavy feelings. It's okay to take things one moment at a time."
        
        if emotion in recent_emotions:
            return "I see this feeling has been persistent for you. That must be exhausting."
        
        return None
    
    def _generate_encouraging_closing(self, emotion: str, sentiment_score: float) -> str:
        """Generate encouraging closing statement"""
        if sentiment_score < -0.5:  # Very negative
            closings = [
                "Remember, you've gotten through difficult times before, and you can get through this too.",
                "Take things one breath, one moment at a time. I believe in your strength.",
                "You don't have to carry all of this alone. There are people who care about you."
            ]
        elif sentiment_score < 0:  # Somewhat negative
            closings = [
                "Small steps forward are still progress. Be gentle with yourself.",
                "It's okay to not be okay. Healing isn't linear, and that's completely normal.",
                "You're doing the best you can with what you have right now, and that's enough."
            ]
        else:  # Neutral or positive
            closings = [
                "Continue to be kind to yourself as you navigate through this.",
                "You have the inner wisdom to know what you need. Trust yourself.",
                "Thank you for sharing with me. You're not alone in this journey."
            ]
        
        return random.choice(closings)
    
    def get_breathing_exercise(self) -> Dict:
        """Get a random breathing exercise"""
        return random.choice(self.breathing_exercises)
    
    def get_coping_strategy(self, category: str = None) -> List[str]:
        """Get coping strategies by category"""
        if category and category in self.coping_strategies:
            return self.coping_strategies[category]
        
        # Return random category
        category = random.choice(list(self.coping_strategies.keys()))
        return self.coping_strategies[category]