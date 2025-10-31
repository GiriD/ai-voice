"""Provider factory for creating TTS provider instances."""

from typing import Optional

from src.config import settings
from src.providers.base import TTSProvider
from src.providers.azure_openai import AzureOpenAIProvider
from src.providers.azure_speech import AzureSpeechProvider


class ProviderFactory:
    """Factory class for creating TTS provider instances."""
    
    # Registry of available providers
    _providers = {
        "azure-openai": AzureOpenAIProvider,
        "azure-speech": AzureSpeechProvider,
    }
    
    @classmethod
    def create(
        cls,
        provider: Optional[str] = None,
        deployment_name: Optional[str] = None
    ) -> TTSProvider:
        """Create a TTS provider instance.
        
        Args:
            provider: Provider to use (azure-openai, azure-speech). If None, uses default.
            deployment_name: For azure-openai: deployment name. Ignored for azure-speech.
            
        Returns:
            Initialized TTS provider instance
            
        Raises:
            ValueError: If provider name is not found in configuration
        """
        # Use default provider if none specified
        if provider is None:
            provider = settings.default_provider
        
        provider = provider.lower()
        
        # Check if provider exists
        if provider not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider '{provider}'. Available providers: {available}"
            )
        
        # Get provider class
        provider_class = cls._providers[provider]
        
        # Build configuration based on provider
        config = cls._get_provider_config(provider, deployment_name)
        
        # Create and return provider instance
        return provider_class(config)
    
    @classmethod
    def _get_provider_config(cls, provider: str, deployment_name: Optional[str] = None) -> dict:
        """Get configuration for a specific provider.
        
        Args:
            provider: Provider name
            deployment_name: Optional deployment name (for azure-openai)
            
        Returns:
            Configuration dictionary for the provider
        """
        config = {
            "output_dir": settings.output_dir,
            "output_format": settings.output_format,
        }
        
        if provider == "azure-openai":
            # Use default deployment if none specified
            if deployment_name is None:
                deployment_name = settings.default_deployment
            
            # Get deployment configuration
            deployment_config = settings.get_deployment_config(deployment_name)
            
            config.update({
                "api_key": settings.azure_openai_api_key,
                "endpoint": settings.azure_openai_endpoint,
                "api_version": settings.azure_openai_api_version,
                "deployment": deployment_name,
                "model": deployment_config.get("model", deployment_name),
                "voice": deployment_config.get("voice", "alloy"),
            })
        elif provider == "azure-speech":
            config.update({
                "api_key": settings.azure_speech_api_key,
                "region": settings.azure_speech_region,
                "voice": settings.azure_speech_voice,
                "language": settings.azure_speech_language,
            })
        
        return config
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def get_available_deployments(cls) -> list[str]:
        """Get list of available deployment names for Azure OpenAI.
        
        Returns:
            List of configured deployment names
        """
        return list(settings.get_deployments().keys())
    
    @classmethod
    def get_deployment_info(cls) -> dict:
        """Get detailed information about all Azure OpenAI deployments.
        
        Returns:
            Dictionary mapping deployment names to their configuration
        """
        return settings.get_deployments()
