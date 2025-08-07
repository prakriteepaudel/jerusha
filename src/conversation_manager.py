import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manage conversation context and history for therapeutic continuity.
    Handles session management, conversation flow, and context preservation.
    """
    
    def __init__(self, max_session_duration_hours: int = 24, max_interactions_per_session: int = 50):
        self.sessions = {}  # session_id -> session_data
        self.max_session_duration = timedelta(hours=max_session_duration_hours)
        self.max_interactions = max_interactions_per_session
        self.emotion_patterns = defaultdict(list)  # Track emotion patterns across sessions
        
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new conversation session
        
        Args:
            session_id: Optional session ID, will generate one if not provided
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'interactions': [],
            'user_profile': {
                'primary_concerns': [],
                'coping_strategies_tried': [],
                'effective_techniques': [],
                'crisis_history': False
            },
            'session_summary': {
                'dominant_emotions': [],
                'key_themes': [],
                'progress_indicators': [],
                'recommended_follow_ups': []
            }
        }
        
        logger.info(f"Created new session: {session_id[:8]}...")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data by ID"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if self._is_session_expired(session):
            logger.info(f"Session {session_id[:8]}... has expired")
            self._archive_session(session_id)
            return None
        
        return session
    
    def get_context(self, session_id: str) -> Dict:
        """
        Get conversation context for generating responses
        
        Args:
            session_id: Session ID
            
        Returns:
            Context dictionary with relevant conversation history
        """
        session = self.get_session(session_id)
        if not session:
            # Create new session if it doesn't exist
            self.create_session(session_id)
            session = self.sessions[session_id]
        
        # Get recent interactions (last 5 for context)
        recent_interactions = session['interactions'][-5:] if session['interactions'] else []
        
        # Extract emotion patterns from recent interactions
        recent_emotions = [
            interaction.get('emotion_result', {}).get('primary_emotion')
            for interaction in recent_interactions
            if interaction.get('emotion_result')
        ]
        
        # Identify conversation themes
        themes = self._extract_conversation_themes(session['interactions'])
        
        # Check for escalating concerns
        escalation_indicators = self._check_escalation(recent_interactions)
        
        context = {
            'session_duration': (datetime.now() - session['created_at']).total_seconds() / 60,  # minutes
            'interaction_count': len(session['interactions']),
            'recent_emotions': recent_emotions,
            'conversation_themes': themes,
            'escalation_indicators': escalation_indicators,
            'user_profile': session['user_profile'],
            'interactions': recent_interactions,
            'last_activity': session['last_activity'].isoformat()
        }
        
        return context
    
    def add_interaction(self, session_id: str, user_message: str, 
                       emotion_result: Dict, response: str) -> bool:
        """
        Add an interaction to the session
        
        Args:
            session_id: Session ID
            user_message: User's input message
            emotion_result: Emotion analysis results
            response: Therapist's response
            
        Returns:
            Success status
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Create interaction record
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'emotion_result': emotion_result,
            'response': response,
            'message_length': len(user_message),
            'response_length': len(response)
        }
        
        # Add to session
        session['interactions'].append(interaction)
        session['last_activity'] = datetime.now()
        
        # Update user profile based on this interaction
        self._update_user_profile(session, interaction)
        
        # Limit interaction history to prevent memory issues
        if len(session['interactions']) > self.max_interactions:
            # Keep recent interactions and archive older ones
            archived_interactions = session['interactions'][:-self.max_interactions//2]
            session['interactions'] = session['interactions'][-self.max_interactions//2:]
            
            # Update session summary with archived data
            self._update_session_summary(session, archived_interactions)
        
        # Track emotion patterns across sessions
        emotion = emotion_result.get('primary_emotion')
        if emotion:
            self.emotion_patterns[session_id].append({
                'emotion': emotion,
                'timestamp': datetime.now(),
                'sentiment_score': emotion_result.get('sentiment_score', 0)
            })
        
        logger.debug(f"Added interaction to session {session_id[:8]}...")
        return True
    
    def _update_user_profile(self, session: Dict, interaction: Dict):
        """Update user profile based on interaction"""
        emotion_result = interaction.get('emotion_result', {})
        emotion = emotion_result.get('primary_emotion')
        user_message = interaction.get('user_message', '').lower()
        
        # Track primary concerns
        concerns = []
        if emotion in ['anxiety', 'panic', 'overwhelmed']:
            concerns.append('anxiety')
        if emotion in ['depression', 'sadness', 'hopelessness']:
            concerns.append('depression')
        if 'lonely' in user_message or 'alone' in user_message:
            concerns.append('loneliness')
        if 'work' in user_message or 'job' in user_message:
            concerns.append('work_stress')
        if 'relationship' in user_message or 'partner' in user_message:
            concerns.append('relationships')
        
        # Update concerns without duplicates
        for concern in concerns:
            if concern not in session['user_profile']['primary_concerns']:
                session['user_profile']['primary_concerns'].append(concern)
        
        # Track crisis indicators
        crisis_indicators = emotion_result.get('crisis_analysis', {}).get('crisis_indicators', [])
        if crisis_indicators:
            session['user_profile']['crisis_history'] = True
    
    def _extract_conversation_themes(self, interactions: List[Dict]) -> List[str]:
        """Extract key themes from conversation history"""
        if not interactions:
            return []
        
        themes = []
        user_messages = [interaction.get('user_message', '').lower() for interaction in interactions]
        all_text = ' '.join(user_messages)
        
        # Simple keyword-based theme extraction
        theme_keywords = {
            'work_stress': ['work', 'job', 'boss', 'career', 'office', 'deadline'],
            'relationships': ['relationship', 'partner', 'friend', 'family', 'marriage', 'boyfriend', 'girlfriend'],
            'self_esteem': ['worthless', 'failure', 'stupid', 'ugly', 'not good enough'],
            'anxiety': ['worried', 'anxious', 'nervous', 'panic', 'scared', 'afraid'],
            'depression': ['sad', 'depressed', 'hopeless', 'empty', 'numb', 'tired'],
            'trauma': ['trauma', 'abuse', 'assault', 'accident', 'ptsd'],
            'substance_use': ['drinking', 'alcohol', 'drugs', 'substances', 'addiction'],
            'sleep_issues': ['sleep', 'insomnia', 'tired', 'exhausted', 'rest'],
            'financial_stress': ['money', 'debt', 'financial', 'bills', 'broke', 'poor']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _check_escalation(self, recent_interactions: List[Dict]) -> Dict:
        """Check for escalating concerns in recent interactions"""
        if len(recent_interactions) < 2:
            return {'escalating': False}
        
        # Check sentiment trend
        sentiments = [
            interaction.get('emotion_result', {}).get('sentiment_score', 0)
            for interaction in recent_interactions
            if interaction.get('emotion_result', {}).get('sentiment_score') is not None
        ]
        
        escalation_indicators = {
            'escalating': False,
            'sentiment_declining': False,
            'crisis_language_increasing': False,
            'intensity_increasing': False
        }
        
        if len(sentiments) >= 3:
            # Check if sentiment is declining
            recent_trend = sentiments[-3:]
            if all(recent_trend[i] >= recent_trend[i+1] for i in range(len(recent_trend)-1)):
                escalation_indicators['sentiment_declining'] = True
        
        # Check for increasing crisis language
        crisis_counts = []
        for interaction in recent_interactions:
            crisis_indicators = interaction.get('emotion_result', {}).get('crisis_analysis', {}).get('crisis_indicators', [])
            crisis_counts.append(len(crisis_indicators))
        
        if len(crisis_counts) >= 2 and crisis_counts[-1] > crisis_counts[-2]:
            escalation_indicators['crisis_language_increasing'] = True
        
        # Overall escalation check
        escalation_indicators['escalating'] = any([
            escalation_indicators['sentiment_declining'],
            escalation_indicators['crisis_language_increasing']
        ])
        
        return escalation_indicators
    
    def _is_session_expired(self, session: Dict) -> bool:
        """Check if session has expired"""
        last_activity = session['last_activity']
        return datetime.now() - last_activity > self.max_session_duration
    
    def _archive_session(self, session_id: str):
        """Archive an expired session"""
        if session_id in self.sessions:
            # In a real implementation, you might save to a database
            logger.info(f"Archiving session {session_id[:8]}...")
            del self.sessions[session_id]
    
    def _update_session_summary(self, session: Dict, archived_interactions: List[Dict]):
        """Update session summary with archived interaction data"""
        # Extract dominant emotions from archived interactions
        emotions = [
            interaction.get('emotion_result', {}).get('primary_emotion')
            for interaction in archived_interactions
            if interaction.get('emotion_result', {}).get('primary_emotion')
        ]
        
        # Count emotion frequencies
        emotion_counts = defaultdict(int)
        for emotion in emotions:
            emotion_counts[emotion] += 1
        
        # Update dominant emotions
        dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        session['session_summary']['dominant_emotions'] = [emotion for emotion, count in dominant_emotions]
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get summary of session for continuity purposes"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        interactions = session['interactions']
        if not interactions:
            return {'summary': 'No interactions yet'}
        
        # Calculate session metrics
        total_interactions = len(interactions)
        session_duration = (datetime.now() - session['created_at']).total_seconds() / 60
        
        # Emotion analysis
        emotions = [
            interaction.get('emotion_result', {}).get('primary_emotion')
            for interaction in interactions
            if interaction.get('emotion_result', {}).get('primary_emotion')
        ]
        
        emotion_counts = defaultdict(int)
        for emotion in emotions:
            emotion_counts[emotion] += 1
        
        dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Crisis indicators
        crisis_interactions = sum(
            1 for interaction in interactions
            if interaction.get('emotion_result', {}).get('crisis_analysis', {}).get('crisis_level') in ['moderate', 'high']
        )
        
        summary = {
            'session_duration_minutes': round(session_duration, 1),
            'total_interactions': total_interactions,
            'dominant_emotions': [emotion for emotion, count in dominant_emotions],
            'primary_concerns': session['user_profile']['primary_concerns'],
            'conversation_themes': self._extract_conversation_themes(interactions),
            'crisis_interactions': crisis_interactions,
            'escalation_status': self._check_escalation(interactions[-5:]),
            'last_activity': session['last_activity'].isoformat()
        }
        
        return summary
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self._archive_session(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)