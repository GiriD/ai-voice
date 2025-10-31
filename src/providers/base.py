"""Base abstract class for text-to-speech providers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class TTSProvider(ABC):
    """Abstract base class for all TTS providers."""
    
    def __init__(self, config: dict):
        """Initialize the TTS provider with configuration.
        
        Args:
            config: Dictionary containing provider-specific configuration
        """
        self.config = config
    
    @abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: Optional[Path] = None,
        voice: Optional[str] = None,
        **kwargs
    ) -> Path:
        """Synthesize speech from text.
        
        Args:
            text: The text to convert to speech
            output_path: Optional custom output path for the audio file
            voice: Optional voice name/ID to use
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Path to the generated audio file
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> list[str]:
        """Get list of available voices for this provider.
        
        Returns:
            List of available voice names/IDs
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of the provider.
        
        Returns:
            Provider name as string
        """
        pass
