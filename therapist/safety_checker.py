import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SafetyChecker:
    """Monitors user messages for crisis indicators and provides safety resources."""
    
    def __init__(self):
        """Initialize the safety checker with crisis detection patterns."""
        
        # Crisis keywords and phrases organized by severity
        self.crisis_patterns = {
            'immediate_crisis': {
                'suicide': [
                    r'\b(kill\s+myself|end\s+my\s+life|take\s+my\s+life|commit\s+suicide)\b',
                    r'\b(want\s+to\s+die|wish\s+i\s+was\s+dead|better\s+off\s+dead)\b',
                    r'\b(no\s+reason\s+to\s+live|life\s+is\s+not\s+worth\s+living)\b',
                    r'\b(planning\s+to\s+end\s+it|going\s+to\s+end\s+it)\b'
                ],
                'self_harm': [
                    r'\b(cut\s+myself|hurt\s+myself|self\s+harm|self\s+injury)\b',
                    r'\b(burn\s+myself|starve\s+myself|overdose)\b',
                    r'\b(want\s+to\s+hurt\s+myself|need\s+to\s+feel\s+pain)\b'
                ],
                'homicide': [
                    r'\b(kill\s+someone|hurt\s+someone|want\s+to\s+hurt\s+others)\b',
                    r'\b(planning\s+to\s+hurt|going\s+to\s+hurt)\b'
                ]
            },
            'high_risk': {
                'hopelessness': [
                    r'\b(no\s+hope|hopeless|nothing\s+matters|pointless)\b',
                    r'\b(can\'t\s+go\s+on|give\s+up|tired\s+of\s+living)\b',
                    r'\b(everything\s+is\s+meaningless|life\s+has\s+no\s+purpose)\b'
                ],
                'isolation': [
                    r'\b(completely\s+alone|nobody\s+cares|no\s+friends)\b',
                    r'\b(no\s+one\s+would\s+miss\s+me|no\s+one\s+understands)\b',
                    r'\b(isolated|cut\s+off|disconnected)\b'
                ],
                'despair': [
                    r'\b(can\'t\s+take\s+it\s+anymore|overwhelmed|desperate)\b',
                    r'\b(helpless|powerless|trapped)\b',
                    r'\b(no\s+way\s+out|stuck|no\s+options)\b'
                ]
            },
            'moderate_risk': {
                'depression': [
                    r'\b(depressed|sad\s+all\s+the\s+time|empty\s+inside)\b',
                    r'\b(can\'t\s+get\s+out\s+of\s+bed|no\s+energy|exhausted)\b',
                    r'\b(don\'t\s+want\s+to\s+live|life\s+is\s+too\s+hard)\b'
                ],
                'anxiety': [
                    r'\b(panic\s+attack|anxiety\s+attack|can\'t\s+breathe)\b',
                    r'\b(overwhelming\s+anxiety|constant\s+worry|paralyzed)\b'
                ],
                'substance_abuse': [
                    r'\b(drinking\s+too\s+much|using\s+drugs|substance\s+abuse)\b',
                    r'\b(need\s+to\s+escape|numb\s+myself)\b'
                ]
            }
        }
        
        # Emergency contact information
        self.emergency_contacts = {
            'US': {
                'National Suicide Prevention Lifeline': '988',
                'Crisis Text Line': 'Text HOME to 741741',
                'Emergency Services': '911',
                'SAMHSA National Helpline': '1-800-662-HELP (4357)',
                'Veterans Crisis Line': '1-800-273-8255, Press 1'
            },
            'Canada': {
                'Crisis Services Canada': '1-833-456-4566',
                'Text Crisis Services': 'Text HOME to 686868',
                'Emergency Services': '911'
            },
            'UK': {
                'Samaritans': '116 123',
                'Shout Crisis Text Line': 'Text SHOUT to 85258',
                'Emergency Services': '999'
            },
            'Australia': {
                'Lifeline': '13 11 14',
                'Beyond Blue': '1300 22 4636',
                'Emergency Services': '000'
            }
        }
        
        # Safety response templates
        self.safety_responses = {
            'immediate_crisis': {
                'response': (
                    "I'm very concerned about what you're sharing. Your life has value and you deserve help. "
                    "Please reach out to a crisis helpline immediately - they have trained professionals who can help you right now. "
                    "You don't have to go through this alone."
                ),
                'urgency': 'immediate',
                'requires_emergency_contacts': True
            },
            'high_risk': {
                'response': (
                    "I hear how much pain you're in, and I'm worried about you. "
                    "These feelings are serious and you deserve professional support. "
                    "Please consider reaching out to a mental health professional or crisis helpline. "
                    "You're not alone in this."
                ),
                'urgency': 'high',
                'requires_emergency_contacts': True
            },
            'moderate_risk': {
                'response': (
                    "I can see you're going through a really difficult time. "
                    "These feelings are valid and it's okay to ask for help. "
                    "Consider talking to a mental health professional - they can provide the support you deserve. "
                    "You don't have to face this alone."
                ),
                'urgency': 'moderate',
                'requires_emergency_contacts': False
            }
        }
    
    def check_message(self, message: str) -> Dict[str, Any]:
        """
        Check a message for crisis indicators and return appropriate safety response.
        
        Args:
            message: The user's message to check
            
        Returns:
            Dictionary containing safety assessment and response
        """
        if not message or not message.strip():
            return self._get_safe_response()
        
        message_lower = message.lower().strip()
        
        # Check for crisis indicators
        crisis_results = self._detect_crisis_indicators(message_lower)
        
        # Determine the highest risk level
        risk_level = self._determine_risk_level(crisis_results)
        
        # Generate appropriate response
        response_data = self._generate_safety_response(risk_level, crisis_results)
        
        return response_data
    
    def _detect_crisis_indicators(self, message: str) -> Dict[str, Any]:
        """Detect crisis indicators in the message."""
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
    
    def _determine_risk_level(self, crisis_results: Dict[str, Any]) -> str:
        """Determine the highest risk level from detected crises."""
        if crisis_results.get('immediate_crisis'):
            for category, matches in crisis_results['immediate_crisis'].items():
                if matches:
                    return 'immediate_crisis'
        
        if crisis_results.get('high_risk'):
            for category, matches in crisis_results['high_risk'].items():
                if matches:
                    return 'high_risk'
        
        if crisis_results.get('moderate_risk'):
            for category, matches in crisis_results['moderate_risk'].items():
                if matches:
                    return 'moderate_risk'
        
        return 'safe'
    
    def _generate_safety_response(self, risk_level: str, crisis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate safety response based on risk level."""
        if risk_level == 'safe':
            return self._get_safe_response()
        
        # Get response template for the risk level
        response_template = self.safety_responses.get(risk_level, self.safety_responses['moderate_risk'])
        
        # Determine which country's emergency contacts to provide
        emergency_contacts = self._get_relevant_emergency_contacts()
        
        return {
            'is_crisis': True,
            'risk_level': risk_level,
            'response': response_template['response'],
            'urgency': response_template['urgency'],
            'emergency_contacts': emergency_contacts if response_template['requires_emergency_contacts'] else {},
            'detected_crises': crisis_results,
            'recommendation': self._get_crisis_recommendation(risk_level)
        }
    
    def _get_safe_response(self) -> Dict[str, Any]:
        """Return response for safe messages."""
        return {
            'is_crisis': False,
            'risk_level': 'safe',
            'response': '',
            'urgency': 'none',
            'emergency_contacts': {},
            'detected_crises': {},
            'recommendation': 'continue_therapy'
        }
    
    def _get_relevant_emergency_contacts(self) -> Dict[str, str]:
        """Get emergency contacts for the user's location (default to US)."""
        # In a real implementation, you might detect user location
        # For now, default to US contacts
        return self.emergency_contacts.get('US', {})
    
    def _get_crisis_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level."""
        recommendations = {
            'immediate_crisis': 'immediate_professional_help',
            'high_risk': 'professional_help_soon',
            'moderate_risk': 'consider_professional_help',
            'safe': 'continue_therapy'
        }
        return recommendations.get(risk_level, 'continue_therapy')
    
    def get_all_emergency_contacts(self) -> Dict[str, Dict[str, str]]:
        """Get all emergency contacts for all supported countries."""
        return self.emergency_contacts.copy()
    
    def add_custom_emergency_contact(self, country: str, service: str, contact: str):
        """Add a custom emergency contact."""
        if country not in self.emergency_contacts:
            self.emergency_contacts[country] = {}
        
        self.emergency_contacts[country][service] = contact
    
    def validate_message_safety(self, message: str) -> bool:
        """
        Quick validation to check if a message contains any crisis indicators.
        
        Args:
            message: Message to validate
            
        Returns:
            True if message appears safe, False if crisis indicators detected
        """
        if not message:
            return True
        
        result = self.check_message(message)
        return not result['is_crisis']
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """Get statistics about safety monitoring."""
        return {
            'crisis_patterns_count': sum(len(patterns) for categories in self.crisis_patterns.values() 
                                        for patterns in categories.values()),
            'supported_countries': len(self.emergency_contacts),
            'risk_levels': list(self.safety_responses.keys()),
            'monitoring_active': True
        }