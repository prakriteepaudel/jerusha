import re
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class CrisisDetector:
    """
    Detect crisis situations and provide appropriate emergency resources.
    Focus on suicide prevention, self-harm detection, and emergency intervention.
    """
    
    def __init__(self):
        # High-risk keywords that indicate immediate crisis
        self.high_risk_keywords = [
            # Suicidal ideation - direct
            'kill myself', 'suicide', 'end my life', 'take my life', 'want to die',
            'better off dead', 'not worth living', 'end it all', 'rather be dead',
            
            # Suicidal ideation - indirect
            'no point in living', 'why go on', 'can\'t take anymore', 'final goodbye',
            'saying goodbye', 'won\'t be here much longer',
            
            # Self-harm
            'hurt myself', 'cut myself', 'self harm', 'self-harm', 'punish myself',
            'harm myself', 'injure myself', 'make myself bleed',
            
            # Immediate danger
            'going to hurt', 'going to kill', 'tonight\'s the night', 'this is it',
            'final decision', 'made up my mind', 'no turning back'
        ]
        
        # Moderate risk keywords that indicate distress
        self.moderate_risk_keywords = [
            # Hopelessness
            'hopeless', 'helpless', 'no hope', 'give up', 'giving up',
            'nothing matters', 'pointless', 'no reason', 'empty inside',
            
            # Overwhelming distress
            'can\'t go on', 'too much', 'breaking point', 'falling apart',
            'losing control', 'can\'t cope', 'can\'t handle', 'overwhelmed',
            
            # Isolation and despair
            'alone forever', 'nobody cares', 'burden to everyone', 'useless',
            'worthless', 'failure', 'disappointed everyone', 'let everyone down',
            
            # Severe anxiety/panic
            'panic attack', 'can\'t breathe', 'heart racing', 'going crazy',
            'losing my mind', 'having a breakdown'
        ]
        
        # Crisis resources with different levels of urgency
        self.crisis_resources = {
            'immediate_emergency': {
                'title': 'Emergency Services',
                'resources': [
                    {
                        'name': 'Emergency Services',
                        'number': '911',
                        'description': 'For immediate life-threatening emergencies',
                        'available': '24/7'
                    },
                    {
                        'name': 'Crisis Text Line',
                        'number': 'Text HOME to 741741',
                        'description': 'Free, 24/7 crisis support via text',
                        'available': '24/7'
                    }
                ]
            },
            'suicide_prevention': {
                'title': 'Suicide Prevention',
                'resources': [
                    {
                        'name': '988 Suicide & Crisis Lifeline',
                        'number': '988',
                        'description': 'Free and confidential emotional support',
                        'available': '24/7',
                        'website': 'https://988lifeline.org'
                    },
                    {
                        'name': 'Crisis Text Line',
                        'number': 'Text HOME to 741741',
                        'description': 'Crisis counseling via text message',
                        'available': '24/7'
                    },
                    {
                        'name': 'International Association for Suicide Prevention',
                        'description': 'Global crisis center directory',
                        'website': 'https://www.iasp.info/resources/Crisis_Centres'
                    }
                ]
            },
            'mental_health_support': {
                'title': 'Mental Health Support',
                'resources': [
                    {
                        'name': 'NAMI (National Alliance on Mental Illness)',
                        'number': '1-800-950-NAMI',
                        'description': 'Mental health support and information',
                        'available': 'Monday-Friday 10am-10pm ET'
                    },
                    {
                        'name': 'SAMHSA National Helpline',
                        'number': '1-800-662-4357',
                        'description': 'Treatment referrals and information',
                        'available': '24/7'
                    },
                    {
                        'name': 'BetterHelp',
                        'description': 'Online professional counseling',
                        'website': 'https://www.betterhelp.com'
                    }
                ]
            },
            'specialized_support': {
                'title': 'Specialized Support',
                'resources': [
                    {
                        'name': 'Trans Lifeline',
                        'number': '877-565-8860',
                        'description': 'Crisis support for transgender community',
                        'available': '24/7'
                    },
                    {
                        'name': 'LGBT National Hotline',
                        'number': '1-888-843-4564',
                        'description': 'Support for LGBTQ+ individuals',
                        'available': 'Daily 4pm-12am ET'
                    },
                    {
                        'name': 'Veterans Crisis Line',
                        'number': '1-800-273-8255',
                        'description': 'Crisis support for veterans',
                        'available': '24/7'
                    },
                    {
                        'name': 'RAINN National Sexual Assault Hotline',
                        'number': '1-800-656-4673',
                        'description': 'Support for sexual assault survivors',
                        'available': '24/7'
                    }
                ]
            }
        }
        
        # Safety planning elements
        self.safety_planning_steps = [
            "Identify personal warning signs of a crisis",
            "List internal coping strategies you can use on your own",
            "Identify people and social settings that provide distraction",
            "List people you can ask for help",
            "List professionals or agencies to contact during a crisis",
            "Describe ways to make your environment safer"
        ]
    
    def check_for_crisis(self, text: str) -> Dict:
        """
        Analyze text for crisis indicators
        
        Args:
            text: User input text to analyze
            
        Returns:
            Dictionary with crisis assessment results
        """
        text_lower = text.lower()
        
        # Check for high-risk indicators
        high_risk_found = []
        for keyword in self.high_risk_keywords:
            if keyword in text_lower:
                high_risk_found.append(keyword)
        
        # Check for moderate-risk indicators
        moderate_risk_found = []
        for keyword in self.moderate_risk_keywords:
            if keyword in text_lower:
                moderate_risk_found.append(keyword)
        
        # Determine crisis level
        is_crisis = len(high_risk_found) > 0
        risk_level = 'low'
        
        if high_risk_found:
            risk_level = 'high'
        elif len(moderate_risk_found) >= 2:
            risk_level = 'moderate'
        elif moderate_risk_found:
            risk_level = 'mild'
        
        # Additional context analysis
        urgency_indicators = self._check_urgency_indicators(text_lower)
        method_specificity = self._check_method_specificity(text_lower)
        plan_indicators = self._check_plan_indicators(text_lower)
        
        # Determine appropriate resources
        recommended_resources = self._get_recommended_resources(risk_level, is_crisis)
        
        crisis_result = {
            'is_crisis': is_crisis,
            'risk_level': risk_level,
            'high_risk_keywords': high_risk_found,
            'moderate_risk_keywords': moderate_risk_found,
            'urgency_indicators': urgency_indicators,
            'method_specificity': method_specificity,
            'plan_indicators': plan_indicators,
            'recommended_resources': recommended_resources,
            'requires_immediate_intervention': risk_level == 'high' or urgency_indicators,
            'assessment_timestamp': datetime.now().isoformat()
        }
        
        # Log crisis detection (anonymized)
        if is_crisis or risk_level in ['moderate', 'mild']:
            logger.warning(f"Crisis/distress detected - Risk level: {risk_level}, Keywords: {len(high_risk_found + moderate_risk_found)}")
        
        return crisis_result
    
    def _check_urgency_indicators(self, text: str) -> bool:
        """Check for time-based urgency indicators"""
        urgency_phrases = [
            'tonight', 'today', 'right now', 'this minute', 'immediately',
            'can\'t wait', 'about to', 'going to do it', 'final time',
            'last chance', 'now or never', 'this is it'
        ]
        
        return any(phrase in text for phrase in urgency_phrases)
    
    def _check_method_specificity(self, text: str) -> bool:
        """Check for specific method mentions (higher risk)"""
        method_keywords = [
            'pills', 'rope', 'knife', 'gun', 'bridge', 'building',
            'overdose', 'hanging', 'cutting', 'jumping', 'drowning',
            'poison', 'medication', 'sharp', 'blade'
        ]
        
        return any(keyword in text for keyword in method_keywords)
    
    def _check_plan_indicators(self, text: str) -> bool:
        """Check for planning indicators"""
        plan_phrases = [
            'figured out how', 'know how', 'planned', 'ready to',
            'prepared', 'set up', 'arranged', 'decided when',
            'made plans', 'thought it through', 'have a way'
        ]
        
        return any(phrase in text for phrase in plan_phrases)
    
    def _get_recommended_resources(self, risk_level: str, is_crisis: bool) -> List[Dict]:
        """Get appropriate resources based on risk assessment"""
        resources = []
        
        if is_crisis or risk_level == 'high':
            resources.extend(self.crisis_resources['immediate_emergency']['resources'])
            resources.extend(self.crisis_resources['suicide_prevention']['resources'])
        elif risk_level == 'moderate':
            resources.extend(self.crisis_resources['suicide_prevention']['resources'])
            resources.extend(self.crisis_resources['mental_health_support']['resources'][:2])
        elif risk_level == 'mild':
            resources.extend(self.crisis_resources['mental_health_support']['resources'])
        
        return resources
    
    def get_crisis_resources(self, category: str = None) -> Dict:
        """
        Get crisis resources by category
        
        Args:
            category: Specific category of resources or None for all
            
        Returns:
            Dictionary of crisis resources
        """
        if category and category in self.crisis_resources:
            return {category: self.crisis_resources[category]}
        
        return self.crisis_resources
    
    def generate_safety_plan_template(self) -> Dict:
        """Generate a safety planning template"""
        return {
            'title': 'Personal Safety Plan',
            'description': 'A safety plan is a personalized, practical plan that can help you lower risk, feel safe, and know how to find help.',
            'steps': [
                {
                    'step_number': i + 1,
                    'title': step,
                    'user_input': '',
                    'examples': self._get_safety_plan_examples(i)
                }
                for i, step in enumerate(self.safety_planning_steps)
            ],
            'emergency_contacts': {
                '988 Suicide & Crisis Lifeline': '988',
                'Crisis Text Line': 'Text HOME to 741741',
                'Emergency Services': '911'
            }
        }
    
    def _get_safety_plan_examples(self, step_index: int) -> List[str]:
        """Get examples for each safety planning step"""
        examples = [
            # Warning signs
            ['Feeling hopeless', 'Isolating from others', 'Increased anxiety', 'Sleep problems'],
            
            # Internal coping strategies
            ['Deep breathing exercises', 'Listening to music', 'Taking a shower', 'Going for a walk'],
            
            # People and places for distraction
            ['Coffee with a friend', 'Visit a library', 'Go to a park', 'Call a family member'],
            
            # People to ask for help
            ['Best friend', 'Family member', 'Trusted colleague', 'Neighbor'],
            
            # Professional contacts
            ['Therapist', 'Doctor', 'Crisis hotline', 'Hospital emergency room'],
            
            # Environmental safety
            ['Remove means of self-harm', 'Stay with someone', 'Avoid substances', 'Create calming space']
        ]
        
        return examples[step_index] if step_index < len(examples) else []
    
    def assess_conversation_pattern(self, interactions: List[Dict]) -> Dict:
        """
        Assess crisis risk based on conversation patterns
        
        Args:
            interactions: List of recent conversation interactions
            
        Returns:
            Pattern-based risk assessment
        """
        if not interactions:
            return {'pattern_risk': 'low', 'indicators': []}
        
        indicators = []
        
        # Check for escalating crisis language
        crisis_counts = []
        for interaction in interactions:
            text = interaction.get('user_message', '')
            crisis_check = self.check_for_crisis(text)
            crisis_counts.append(len(crisis_check['high_risk_keywords'] + crisis_check['moderate_risk_keywords']))
        
        if len(crisis_counts) >= 2 and crisis_counts[-1] > crisis_counts[0]:
            indicators.append('escalating_crisis_language')
        
        # Check for persistent hopelessness
        hopelessness_count = 0
        for interaction in interactions:
            text = interaction.get('user_message', '').lower()
            if any(word in text for word in ['hopeless', 'no hope', 'give up', 'pointless']):
                hopelessness_count += 1
        
        if hopelessness_count >= len(interactions) * 0.5:  # 50% or more interactions
            indicators.append('persistent_hopelessness')
        
        # Check for social isolation mentions
        isolation_indicators = ['alone', 'nobody', 'isolated', 'no friends', 'no one cares']
        isolation_count = 0
        for interaction in interactions:
            text = interaction.get('user_message', '').lower()
            if any(indicator in text for indicator in isolation_indicators):
                isolation_count += 1
        
        if isolation_count >= 2:
            indicators.append('social_isolation')
        
        # Determine overall pattern risk
        pattern_risk = 'low'
        if len(indicators) >= 2:
            pattern_risk = 'high'
        elif len(indicators) == 1:
            pattern_risk = 'moderate'
        
        return {
            'pattern_risk': pattern_risk,
            'indicators': indicators,
            'recommendation': self._get_pattern_recommendation(pattern_risk, indicators)
        }
    
    def _get_pattern_recommendation(self, risk_level: str, indicators: List[str]) -> str:
        """Get recommendation based on pattern analysis"""
        if risk_level == 'high':
            return "Strong recommendation for immediate professional intervention and crisis support resources."
        elif risk_level == 'moderate':
            return "Recommend increased support and monitoring, consider professional help."
        else:
            return "Continue supportive conversation and monitor for changes."