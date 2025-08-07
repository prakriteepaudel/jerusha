import os
import io
import base64
import logging
from typing import Optional
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import tempfile

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handles speech-to-text and text-to-speech functionality."""
    
    def __init__(self):
        """Initialize the voice handler with speech recognition and synthesis."""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            # Configure TTS settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to set a female voice for a more empathetic tone
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Fallback to first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 150)  # Words per minute
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            
        except Exception as e:
            logger.warning(f"Could not initialize pyttsx3: {e}")
            self.tts_engine = None
        
        # Google Cloud Speech-to-Text API key (optional)
        self.google_api_key = os.getenv('GOOGLE_SPEECH_API_KEY')
        
        # Supported audio formats
        self.supported_formats = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    
    def transcribe_audio(self, audio_file) -> str:
        """
        Transcribe audio file to text using speech recognition.
        
        Args:
            audio_file: File object containing audio data
            
        Returns:
            Transcribed text string
        """
        try:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            # Load the audio file
            with sr.AudioFile(temp_file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Try multiple speech recognition services
            transcribed_text = self._try_speech_recognition(audio)
            
            if transcribed_text:
                logger.info(f"Successfully transcribed: {transcribed_text}")
                return transcribed_text
            else:
                logger.warning("Speech recognition failed for all services")
                return "I'm sorry, I couldn't understand what you said. Could you please try again?"
                
        except Exception as e:
            logger.error(f"Error in speech transcription: {e}")
            return "I'm sorry, there was an error processing your voice input. Please try again."
    
    def _try_speech_recognition(self, audio) -> Optional[str]:
        """Try multiple speech recognition services in order of preference."""
        
        # Try Google Speech Recognition (requires internet)
        try:
            text = self.recognizer.recognize_google(audio)
            if text:
                return text
        except sr.UnknownValueError:
            logger.debug("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.debug(f"Google Speech Recognition error: {e}")
        except Exception as e:
            logger.debug(f"Google Speech Recognition failed: {e}")
        
        # Try Google Cloud Speech-to-Text API if API key is available
        if self.google_api_key:
            try:
                text = self.recognizer.recognize_google_cloud(audio, credentials_json=self.google_api_key)
                if text:
                    return text
            except Exception as e:
                logger.debug(f"Google Cloud Speech Recognition failed: {e}")
        
        # Try Sphinx (offline, but less accurate)
        try:
            text = self.recognizer.recognize_sphinx(audio)
            if text:
                return text
        except sr.UnknownValueError:
            logger.debug("Sphinx could not understand audio")
        except Exception as e:
            logger.debug(f"Sphinx recognition failed: {e}")
        
        return None
    
    def synthesize_speech(self, text: str) -> str:
        """
        Convert text to speech and return as base64 encoded audio data.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Base64 encoded audio data
        """
        try:
            # Use gTTS (Google Text-to-Speech) for better quality
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                temp_file_path = temp_file.name
            
            # Read the audio file and encode as base64
            with open(temp_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Encode as base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            logger.info(f"Successfully synthesized speech for text: {text[:50]}...")
            return audio_base64
            
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")
            
            # Fallback to pyttsx3 if gTTS fails
            if self.tts_engine:
                try:
                    return self._synthesize_with_pyttsx3(text)
                except Exception as e2:
                    logger.error(f"Pyttsx3 fallback also failed: {e2}")
            
            return ""
    
    def _synthesize_with_pyttsx3(self, text: str) -> str:
        """Fallback speech synthesis using pyttsx3."""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file_path = temp_file.name
            
            # Synthesize speech
            self.tts_engine.save_to_file(text, temp_file_path)
            self.tts_engine.runAndWait()
            
            # Read the audio file and encode as base64
            with open(temp_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Encode as base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"Pyttsx3 synthesis failed: {e}")
            return ""
    
    def get_audio_duration(self, audio_base64: str) -> float:
        """
        Estimate the duration of audio from base64 data.
        
        Args:
            audio_base64: Base64 encoded audio data
            
        Returns:
            Estimated duration in seconds
        """
        try:
            # Decode base64 data
            audio_data = base64.b64decode(audio_base64)
            
            # Rough estimation: 1 second of audio ≈ 16KB for MP3
            # This is a very rough estimate
            estimated_duration = len(audio_data) / 16000  # bytes per second estimate
            
            return max(estimated_duration, 0.5)  # Minimum 0.5 seconds
            
        except Exception as e:
            logger.error(f"Error estimating audio duration: {e}")
            return 2.0  # Default fallback duration
    
    def is_audio_file_supported(self, filename: str) -> bool:
        """
        Check if the audio file format is supported.
        
        Args:
            filename: Name of the audio file
            
        Returns:
            True if format is supported, False otherwise
        """
        if not filename:
            return False
        
        file_extension = os.path.splitext(filename.lower())[1]
        return file_extension in self.supported_formats
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats."""
        return self.supported_formats.copy()
    
    def adjust_for_noise(self, audio_file) -> bool:
        """
        Adjust speech recognition for ambient noise.
        
        Args:
            audio_file: Audio file to adjust for
            
        Returns:
            True if adjustment was successful, False otherwise
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            with sr.AudioFile(temp_file_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
            os.unlink(temp_file_path)
            return True
            
        except Exception as e:
            logger.error(f"Error adjusting for noise: {e}")
            return False