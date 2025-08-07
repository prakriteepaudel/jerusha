import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import io
import base64
import logging
import tempfile
import os
from typing import Optional, Union

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """
    Handle voice input/output processing:
    - Speech-to-text using Google Speech Recognition
    - Text-to-speech using pyttsx3 and gTTS
    """
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.use_offline_tts = True  # Prefer offline TTS for privacy
        
    def initialize(self):
        """Initialize voice processing components"""
        try:
            # Initialize speech recognition
            logger.info("Initializing speech recognition...")
            self.recognizer = sr.Recognizer()
            
            # Try to initialize microphone (may fail in headless environments)
            try:
                self.microphone = sr.Microphone()
                logger.info("Microphone initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize microphone: {str(e)}")
            
            # Initialize text-to-speech engine
            logger.info("Initializing text-to-speech engine...")
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_tts_engine()
                logger.info("Offline TTS engine initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize offline TTS: {str(e)}")
                self.use_offline_tts = False
            
            logger.info("Voice processor initialized")
            
        except Exception as e:
            logger.error(f"Error initializing voice processor: {str(e)}")
    
    def _configure_tts_engine(self):
        """Configure the TTS engine with appropriate settings"""
        if not self.tts_engine:
            return
        
        try:
            # Set voice properties for more natural, calming speech
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice if available (often perceived as more calming)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate (slower for therapeutic context)
            self.tts_engine.setProperty('rate', 150)  # Default is usually 200
            
            # Set volume
            self.tts_engine.setProperty('volume', 0.8)
            
        except Exception as e:
            logger.warning(f"Could not configure TTS engine: {str(e)}")
    
    def speech_to_text(self, audio_source: Union[str, io.BytesIO]) -> Optional[str]:
        """
        Convert speech to text
        
        Args:
            audio_source: Audio file path or BytesIO object
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.recognizer:
            logger.error("Speech recognizer not initialized")
            return None
        
        try:
            # Handle different audio source types
            if isinstance(audio_source, str):
                # File path
                with sr.AudioFile(audio_source) as source:
                    audio = self.recognizer.record(source)
            elif hasattr(audio_source, 'read'):
                # File-like object (e.g., from Flask request)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(audio_source.read())
                    tmp_file_path = tmp_file.name
                
                try:
                    with sr.AudioFile(tmp_file_path) as source:
                        audio = self.recognizer.record(source)
                finally:
                    os.unlink(tmp_file_path)
            else:
                logger.error("Invalid audio source type")
                return None
            
            # Perform speech recognition
            try:
                # Try Google Web Speech API first
                text = self.recognizer.recognize_google(audio)
                logger.info("Successfully transcribed speech using Google API")
                return text
            except sr.RequestError:
                # Fallback to offline recognition if available
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    logger.info("Successfully transcribed speech using offline Sphinx")
                    return text
                except sr.RequestError:
                    logger.error("Could not perform speech recognition - no internet and Sphinx not available")
                    return None
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None
                
        except Exception as e:
            logger.error(f"Error in speech-to-text conversion: {str(e)}")
            return None
    
    def text_to_speech(self, text: str, use_online: bool = False) -> Optional[str]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            use_online: Whether to use online TTS (gTTS) instead of offline
            
        Returns:
            Base64 encoded audio data or None if failed
        """
        if not text or not text.strip():
            return None
        
        try:
            if self.use_offline_tts and self.tts_engine and not use_online:
                return self._text_to_speech_offline(text)
            else:
                return self._text_to_speech_online(text)
                
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {str(e)}")
            return None
    
    def _text_to_speech_offline(self, text: str) -> Optional[str]:
        """Convert text to speech using offline pyttsx3"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file_path = tmp_file.name
            
            # Save to temporary file
            self.tts_engine.save_to_file(text, tmp_file_path)
            self.tts_engine.runAndWait()
            
            # Read the file and encode as base64
            try:
                with open(tmp_file_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                return encoded_audio
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error in offline TTS: {str(e)}")
            return None
    
    def _text_to_speech_online(self, text: str) -> Optional[str]:
        """Convert text to speech using online gTTS"""
        try:
            # Create gTTS object with calming, slow speech
            tts = gTTS(text=text, lang='en', slow=True)
            
            # Save to BytesIO buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Encode as base64
            audio_data = audio_buffer.read()
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            
            return encoded_audio
            
        except Exception as e:
            logger.error(f"Error in online TTS: {str(e)}")
            return None
    
    def record_from_microphone(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Record audio from microphone and convert to text
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for phrase
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.microphone or not self.recognizer:
            logger.error("Microphone or recognizer not available")
            return None
        
        try:
            # Adjust for ambient noise
            with self.microphone as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Listen for speech
            logger.info("Listening for speech...")
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Convert to text
            logger.info("Converting speech to text...")
            try:
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Could not understand speech")
                return None
            except sr.RequestError as e:
                logger.error(f"Error with speech recognition service: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error recording from microphone: {str(e)}")
            return None
    
    def is_microphone_available(self) -> bool:
        """Check if microphone is available"""
        return self.microphone is not None
    
    def is_tts_available(self) -> bool:
        """Check if text-to-speech is available"""
        return self.tts_engine is not None or True  # gTTS is always available with internet
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        if not self.tts_engine:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return [{'id': voice.id, 'name': voice.name} for voice in voices] if voices else []
        except Exception as e:
            logger.error(f"Error getting available voices: {str(e)}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set TTS voice by ID"""
        if not self.tts_engine:
            return False
        
        try:
            self.tts_engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            logger.error(f"Error setting voice: {str(e)}")
            return False