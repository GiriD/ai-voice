"""Azure OpenAI text-to-speech provider implementation."""

from pathlib import Path
from typing import Optional
import time

from openai import AzureOpenAI
from src.providers.base import TTSProvider


class AzureOpenAIProvider(TTSProvider):
    """Azure OpenAI TTS provider implementation."""
    
    def __init__(self, config: dict):
        """Initialize Azure OpenAI provider.
        
        Args:
            config: Configuration dictionary with Azure OpenAI settings
        """
        super().__init__(config)
        
        self.client = AzureOpenAI(
            api_key=config.get("api_key"),
            api_version=config.get("api_version", "2024-02-15-preview"),
            azure_endpoint=config.get("endpoint")
        )
        
        self.deployment = config.get("deployment")
        self.model = config.get("model", self.deployment)
        self.default_voice = config.get("voice", "alloy")
        self.output_dir = Path(config.get("output_dir", "output"))
        self.output_format = config.get("output_format", "mp3")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def synthesize(
        self,
        text: str,
        output_path: Optional[Path] = None,
        voice: Optional[str] = None,
        **kwargs
    ) -> Path:
        """Synthesize speech using Azure OpenAI TTS.
        
        Args:
            text: Text to convert to speech
            output_path: Optional custom output path
            voice: Voice to use (defaults to configured voice)
            **kwargs: Additional parameters (speed, response_format, etc.)
            
        Returns:
            Path to generated audio file
        """
        # Use provided voice or default
        selected_voice = voice or self.default_voice
        
        # Determine output path
        if output_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create unique filename with deployment, voice, and timestamp
            filename = f"{self.deployment}_{selected_voice}_{timestamp}.{self.output_format}"
            output_path = self.output_dir / filename
        else:
            # Ensure custom output path is within output directory
            if not output_path.is_absolute():
                output_path = self.output_dir / output_path
        
        # Get optional parameters
        speed = kwargs.get("speed", 1.0)
        response_format = kwargs.get("response_format", self.output_format)
        
        # Generate speech
        response = self.client.audio.speech.create(
            model=self.deployment,
            voice=selected_voice,
            input=text,
            speed=speed,
            response_format=response_format
        )
        
        # Save to file
        response.stream_to_file(output_path)
        
        return output_path
    
    def get_available_voices(self) -> list[str]:
        """Get available voices for Azure OpenAI TTS.
        
        Returns:
            List of available voice names
        """
        # Azure OpenAI TTS supports these voices
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    @property
    def provider_name(self) -> str:
        """Get provider name.
        
        Returns:
            Provider name string
        """
        return f"Azure OpenAI ({self.deployment})"
