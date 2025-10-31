"""Configuration management using pydantic-settings."""

from typing import Dict
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # Default provider to use (azure-openai or azure-speech)
    default_provider: str = "azure-openai"
    
    # Azure OpenAI settings
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Default deployment to use (for Azure OpenAI)
    default_deployment: str = "tts-1"
    
    # Deployments configuration (comma-separated: deployment_name:model_name:voice)
    # Example: "tts-1:gpt-4o-realtime-preview:alloy,tts-hd:gpt-4o-realtime-preview:nova"
    azure_deployments: str = ""
    
    # Azure AI Speech settings
    azure_speech_api_key: str = ""
    azure_speech_region: str = ""
    azure_speech_voice: str = "en-US-JennyNeural"
    azure_speech_language: str = "en-US"
    
    # Output settings
    output_dir: str = "output"
    output_format: str = "mp3"
    
    def get_deployments(self) -> Dict[str, Dict[str, str]]:
        """Parse deployments configuration into a dictionary.
        
        Returns:
            Dictionary mapping deployment names to their config (model, voice)
        """
        deployments = {}
        
        if not self.azure_deployments:
            # Return default deployment if none configured
            return {
                self.default_deployment: {
                    "model": self.default_deployment,
                    "voice": "alloy"
                }
            }
        
        for deployment_config in self.azure_deployments.split(","):
            parts = deployment_config.strip().split(":")
            if len(parts) >= 1:
                deployment_name = parts[0]
                model = parts[1] if len(parts) > 1 else deployment_name
                voice = parts[2] if len(parts) > 2 else "alloy"
                
                deployments[deployment_name] = {
                    "model": model,
                    "voice": voice
                }
        
        return deployments
    
    def get_deployment_config(self, deployment_name: str = None) -> Dict[str, str]:
        """Get configuration for a specific deployment.
        
        Args:
            deployment_name: Name of the deployment. If None, uses default.
            
        Returns:
            Dictionary with model and voice configuration
        """
        deployments = self.get_deployments()
        
        if deployment_name is None:
            deployment_name = self.default_deployment
        
        if deployment_name not in deployments:
            raise ValueError(
                f"Deployment '{deployment_name}' not found. "
                f"Available deployments: {', '.join(deployments.keys())}"
            )
        
        return deployments[deployment_name]


# Global settings instance
settings = Settings()
