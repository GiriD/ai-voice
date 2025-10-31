"""Azure AI Speech text-to-speech provider implementation."""

from pathlib import Path
from typing import Optional
from datetime import datetime
import azure.cognitiveservices.speech as speechsdk

from src.providers.base import TTSProvider


class AzureSpeechProvider(TTSProvider):
    """Azure AI Speech TTS provider implementation."""
    
    def __init__(self, config: dict):
        """Initialize Azure AI Speech provider.
        
        Args:
            config: Configuration dictionary with Azure AI Speech settings
        """
        super().__init__(config)
        
        # Initialize speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=config.get("api_key"),
            region=config.get("region")
        )
        
        self.default_voice = config.get("voice", "en-US-JennyNeural")
        self.language = config.get("language", "en-US")
        self.output_dir = Path(config.get("output_dir", "output"))
        self.output_format = config.get("output_format", "mp3")
        
        # Set output format
        if self.output_format == "mp3":
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
            )
        elif self.output_format == "wav":
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
            )
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def synthesize(
        self,
        text: str,
        output_path: Optional[Path] = None,
        voice: Optional[str] = None,
        **kwargs
    ) -> Path:
        """Synthesize speech using Azure AI Speech.
        
        Args:
            text: Text to convert to speech
            output_path: Optional custom output path
            voice: Voice to use (defaults to configured voice)
            **kwargs: Additional parameters (rate, pitch, style, etc.)
            
        Returns:
            Path to generated audio file
        """
        # Use provided voice or default
        selected_voice = voice or self.default_voice
        
        # Determine output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            voice_short = selected_voice.split('-')[-1].replace('Neural', '')
            filename = f"azure-speech_{voice_short}_{timestamp}.{self.output_format}"
            output_path = self.output_dir / filename
        else:
            # Ensure custom output path is within output directory
            if not output_path.is_absolute():
                output_path = self.output_dir / output_path
        
        # Set the voice name
        self.speech_config.speech_synthesis_voice_name = selected_voice
        
        # Check if input is already SSML
        text_stripped = text.strip()
        is_ssml = (text_stripped.startswith('<?xml') or 
                   text_stripped.startswith('<speak'))
        
        if is_ssml:
            # Use provided SSML directly
            ssml_text = text
        else:
            # Get optional parameters
            rate = kwargs.get("rate", "1.0")
            pitch = kwargs.get("pitch", "0%")
            style = kwargs.get("style", None)
            
            # Build SSML if additional parameters provided
            if style or rate != "1.0" or pitch != "0%":
                ssml_text = self._build_ssml(text, selected_voice, rate, pitch, style)
            else:
                ssml_text = None
        
        # Configure audio output
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
        
        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        # Synthesize speech
        if ssml_text:
            result = synthesizer.speak_ssml_async(ssml_text).get()
        else:
            result = synthesizer.speak_text_async(text).get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return output_path
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_msg = f"Speech synthesis canceled: {cancellation_details.reason}"
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                error_msg += f"\nError details: {cancellation_details.error_details}"
            raise RuntimeError(error_msg)
        else:
            raise RuntimeError(f"Speech synthesis failed with reason: {result.reason}")
    
    def _build_ssml(
        self,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        style: Optional[str]
    ) -> str:
        """Build SSML for advanced speech synthesis.
        
        Args:
            text: Text to synthesize
            voice: Voice name
            rate: Speech rate (e.g., "1.0", "1.5")
            pitch: Pitch adjustment (e.g., "0%", "+10%")
            style: Speaking style (e.g., "cheerful", "sad")
            
        Returns:
            SSML string
        """
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        ssml += 'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{}">'
        
        # Voice element
        ssml += f'<voice name="{voice}">'
        
        # Style element (if supported)
        if style:
            ssml += f'<mstts:express-as style="{style}">'
        
        # Prosody element
        ssml += f'<prosody rate="{rate}" pitch="{pitch}">'
        ssml += text
        ssml += '</prosody>'
        
        if style:
            ssml += '</mstts:express-as>'
        
        ssml += '</voice></speak>'
        
        return ssml
    
    def get_available_voices(self) -> list[str]:
        """Get available voices for Azure AI Speech.
        
        Returns:
            List of all available voice names from Azure Speech service
        """
        try:
            # Create synthesizer to get voices list
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
            
            # Get voices asynchronously
            result = synthesizer.get_voices_async().get()
            
            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                # Extract voice names and sort them
                voices = [voice.short_name for voice in result.voices]
                return sorted(voices)
            else:
                # Fallback to popular voices if retrieval fails
                print(f"Warning: Could not retrieve voices list. Reason: {result.reason}")
                return self._get_popular_voices()
        except Exception as e:
            # Fallback to popular voices on error
            print(f"Warning: Error retrieving voices: {e}")
            return self._get_popular_voices()
    
    def get_voice_info(self, voice_name: str) -> Optional[dict]:
        """Get detailed information about a specific voice.
        
        Args:
            voice_name: Voice name to get information for
            
        Returns:
            Dictionary with voice information including name, locale, gender,
            styles, roles, voice_type, and other properties. Returns None if voice not found.
        """
        try:
            # Create synthesizer to get voices list
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
            
            # Get voices asynchronously
            result = synthesizer.get_voices_async().get()
            
            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                # Find the requested voice
                for voice in result.voices:
                    if voice.short_name.lower() == voice_name.lower():
                        # Extract voice information
                        voice_info = {
                            "name": voice.name,
                            "short_name": voice.short_name,
                            "locale": voice.locale,
                            "local_name": voice.local_name,
                            "gender": str(voice.gender),
                            "voice_type": str(voice.voice_type),
                            "styles": list(voice.style_list) if hasattr(voice, 'style_list') and voice.style_list else [],
                        }
                        
                        # Try to get role play list (property name might vary)
                        roles = []
                        if hasattr(voice, 'role_play_list') and voice.role_play_list:
                            roles = list(voice.role_play_list)
                        
                        voice_info["roles"] = roles
                        
                        # Add secondary locales if available
                        if hasattr(voice, 'secondary_locale_list') and voice.secondary_locale_list:
                            voice_info["secondary_locales"] = list(voice.secondary_locale_list)
                        
                        # Add voice properties for debugging
                        try:
                            properties = voice.properties
                            if properties:
                                # Check for additional properties that might contain role info
                                voice_info["properties"] = {}
                                # Properties is a PropertyCollection, iterate through known keys
                                for prop_id in dir(speechsdk.PropertyId):
                                    if not prop_id.startswith('_'):
                                        try:
                                            val = properties.get_property(getattr(speechsdk.PropertyId, prop_id))
                                            if val:
                                                voice_info["properties"][prop_id] = val
                                        except:
                                            pass
                        except Exception as e:
                            pass  # Properties might not be available
                        
                        return voice_info
                
                # Voice not found
                return None
            else:
                print(f"Warning: Could not retrieve voices list. Reason: {result.reason}")
                return None
        except Exception as e:
            print(f"Warning: Error retrieving voice info: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_popular_voices(self) -> list[str]:
        """Get a subset of popular voices as fallback.
        
        Returns:
            List of popular voice names
        """
        return [
            "en-US-JennyNeural",
            "en-US-GuyNeural",
            "en-US-AriaNeural",
            "en-US-DavisNeural",
            "en-US-AmberNeural",
            "en-US-AnaNeural",
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural",
            "en-AU-NatashaNeural",
            "en-AU-WilliamNeural",
            "fr-FR-DeniseNeural",
            "fr-FR-HenriNeural",
            "de-DE-KatjaNeural",
            "de-DE-ConradNeural",
            "es-ES-ElviraNeural",
            "es-ES-AlvaroNeural",
            "it-IT-ElsaNeural",
            "it-IT-DiegoNeural",
            "ja-JP-NanamiNeural",
            "ja-JP-KeitaNeural",
            "zh-CN-XiaoxiaoNeural",
            "zh-CN-YunxiNeural",
        ]
    
    @property
    def provider_name(self) -> str:
        """Get provider name.
        
        Returns:
            Provider name string
        """
        return "Azure AI Speech"
