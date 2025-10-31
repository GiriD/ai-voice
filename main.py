#!/usr/bin/env python3
"""Main entry point for AI Voice text-to-speech application."""

import sys
from pathlib import Path
from typing import Optional

from src.config import settings
from src.factory import ProviderFactory


def read_input_file(file_path: Optional[Path] = None) -> str:
    """Read text from input file.
    
    Args:
        file_path: Path to input file (default: input/text.txt)
        
    Returns:
        Text content from file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    if file_path is None:
        file_path = Path("input/text.txt")
    
    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}\n"
            f"Please create the file with text to synthesize."
        )
    
    text = file_path.read_text(encoding="utf-8").strip()
    
    if not text:
        raise ValueError(f"Input file is empty: {file_path}")
    
    return text


def synthesize_from_file(
    input_file: Optional[str] = None,
    provider: Optional[str] = None,
    deployment: Optional[str] = None,
    voice: Optional[str] = None,
    output: Optional[str] = None,
    speed: float = 1.0,
    **kwargs
) -> Path:
    """Synthesize text to speech from input file.
    
    Args:
        input_file: Path to input text file (default: input/text.txt)
        provider: Provider to use (azure-openai, azure-speech, default: from .env)
        deployment: Azure OpenAI deployment to use (ignored for azure-speech)
        voice: Voice to use (default: from provider config)
        output: Output file path (default: auto-generated)
        speed: Speech speed (0.25 to 4.0 for azure-openai, rate for azure-speech)
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Path to generated audio file
    """
    # Read text from file
    file_path = Path(input_file) if input_file else None
    text = read_input_file(file_path)
    
    print(f"Read {len(text)} characters from input file")
    
    # Create TTS provider
    tts_provider = ProviderFactory.create(provider, deployment)
    
    print(f"Using provider: {tts_provider.provider_name}")
    
    # Convert output string to Path if provided
    output_path = Path(output) if output else None
    
    # Synthesize speech
    print(f"Synthesizing text: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # Prepare synthesis parameters
    synth_kwargs = {"speed": speed} if "azure-openai" in tts_provider.provider_name.lower() else {}
    
    # Add provider-specific kwargs
    synth_kwargs.update(kwargs)
    
    result_path = tts_provider.synthesize(
        text=text,
        output_path=output_path,
        voice=voice,
        **synth_kwargs
    )
    
    print(f"✓ Audio saved to: {result_path}")
    
    return result_path


def list_providers() -> None:
    """List all available TTS providers."""
    providers = ProviderFactory.get_available_providers()
    
    print("Available TTS providers:")
    for provider in providers:
        is_default = " (default)" if provider == settings.default_provider else ""
        print(f"  - {provider}{is_default}")


def list_deployments() -> None:
    """List all available Azure OpenAI deployments."""
    deployments = ProviderFactory.get_deployment_info()
    
    print("Available Azure OpenAI deployments:")
    for deployment_name, config in deployments.items():
        is_default = " (default)" if deployment_name == settings.default_deployment else ""
        print(f"  - {deployment_name}{is_default}")
        print(f"    Model: {config.get('model', 'N/A')}")
        print(f"    Voice: {config.get('voice', 'N/A')}")


def list_voices(provider: Optional[str] = None, deployment: Optional[str] = None) -> None:
    """List available voices for a provider.
    
    Args:
        provider: Provider name (default: from .env)
        deployment: Deployment name for azure-openai (default: from .env)
    """
    tts_provider = ProviderFactory.create(provider, deployment)
    voices = tts_provider.get_available_voices()
    
    print(f"Available voices for {tts_provider.provider_name}:")
    for voice in voices:
        print(f"  - {voice}")


def show_voice_info(voice_name: str, provider: Optional[str] = None, deployment: Optional[str] = None) -> None:
    """Show detailed information about a specific voice.
    
    Args:
        voice_name: Name of the voice to inspect
        provider: Provider name (default: from .env)
        deployment: Deployment name for azure-openai (default: from .env)
    """
    tts_provider = ProviderFactory.create(provider, deployment)
    
    # Check if provider supports voice info
    if not hasattr(tts_provider, 'get_voice_info'):
        print(f"Error: Voice info not supported for provider: {tts_provider.provider_name}")
        print("This feature is only available for Azure AI Speech provider.")
        sys.exit(1)
    
    voice_info = tts_provider.get_voice_info(voice_name)
    
    if voice_info is None:
        print(f"Error: Voice '{voice_name}' not found.")
        print("Use 'python main.py voices azure-speech' to see available voices.")
        sys.exit(1)
    
    # Display voice information
    print(f"\nVoice Information: {voice_info['short_name']}")
    print("=" * 70)
    print(f"Full Name:      {voice_info['name']}")
    print(f"Local Name:     {voice_info['local_name']}")
    print(f"Locale:         {voice_info['locale']}")
    print(f"Gender:         {voice_info['gender']}")
    print(f"Voice Type:     {voice_info['voice_type']}")
    
    # Display secondary locales if available (multilingual voices)
    if 'secondary_locales' in voice_info and voice_info['secondary_locales']:
        print(f"\nMultilingual Support ({len(voice_info['secondary_locales'])} additional locales):")
        for locale in voice_info['secondary_locales']:
            print(f"  - {locale}")
    
    # Filter out empty strings from styles
    styles = [s for s in voice_info['styles'] if s and s.strip()]
    
    # Display styles if available
    if styles:
        print(f"\nAvailable Styles ({len(styles)}):")
        for style in styles:
            print(f"  - {style}")
    else:
        print("\nAvailable Styles: None (use default style)")
    
    # Display roles if available
    if voice_info['roles']:
        print(f"\nAvailable Roles ({len(voice_info['roles'])}):")
        for role in voice_info['roles']:
            print(f"  - {role}")
    else:
        print("\nAvailable Roles: None (use default role)")
    
    # Show usage examples
    print("\nUsage Examples:")
    print(f"  # Basic synthesis:")
    print(f"  python main.py synthesize --provider azure-speech --voice {voice_info['short_name']}")
    
    if styles:
        example_style = styles[0]
        print(f"\n  # With style:")
        print(f"  python main.py synthesize --provider azure-speech --voice {voice_info['short_name']} --style {example_style}")
    
    if voice_info['roles']:
        example_role = voice_info['roles'][0]
        print(f"\n  # With role (requires SSML):")
        print(f"  # Note: Role-play requires custom SSML generation")
    
    print(f"\n  # Adjust rate and pitch:")
    print(f"  python main.py synthesize --provider azure-speech --voice {voice_info['short_name']} --rate 1.2 --pitch +5%")
    
    if 'secondary_locales' in voice_info and voice_info['secondary_locales']:
        print(f"\n  # Multilingual synthesis:")
        print(f"  # This voice can speak in {len(voice_info['secondary_locales']) + 1} languages!")
    
    print()


def print_usage() -> None:
    """Print usage information."""
    print("""
AI Voice - Text-to-Speech Converter

Usage:
    python main.py <command> [options]

Commands:
    synthesize               Convert text from input file to speech
    providers                List available TTS providers
    deployments              List available Azure OpenAI deployments
    voices [provider]        List available voices for a provider
    voice-info <voice-name>  Show detailed info about a specific voice

Options for 'synthesize':
    --input <path>           Input text file (default: input/text.txt)
    --provider <name>        TTS provider (azure-openai, azure-speech, default: from .env)
    --deployment <name>      Azure OpenAI deployment (only for azure-openai provider)
    --voice <name>           Voice to use (default: from provider config)
    --output <path>          Output file path (default: auto-generated)
    --speed <float>          Speech speed, 0.25-4.0 (default: 1.0)
    --style <name>           Speaking style (azure-speech only, e.g., cheerful, sad)
    --rate <value>           Speech rate (azure-speech only, e.g., 1.0, 1.5)
    --pitch <value>          Pitch adjustment (azure-speech only, e.g., 0%, +10%)

Options for 'voice-info':
    --provider <name>        TTS provider (default: azure-speech)

Examples:
    # Create input file with your text
    echo "Hello, world!" > input/text.txt
    
    # Using Azure OpenAI (default)
    python main.py synthesize
    python main.py synthesize --deployment tts-hd --voice nova
    
    # Using Azure AI Speech
    python main.py synthesize --provider azure-speech --voice en-US-JennyNeural
    python main.py synthesize --provider azure-speech --style cheerful --rate 1.2
    
    # Custom input file
    python main.py synthesize --input my-script.txt --provider azure-speech
    
    # List providers and voices
    python main.py providers
    python main.py deployments
    python main.py voices azure-speech
    
    # Inspect voice capabilities
    python main.py voice-info en-US-JennyNeural
    python main.py voice-info zh-CN-YunxiNeural
""")


def main() -> None:
    """Main application entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "synthesize":
            # Parse arguments
            input_file = None
            provider = None
            deployment = None
            voice = None
            output = None
            speed = 1.0
            kwargs = {}
            
            # Parse optional arguments
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == "--input" and i + 1 < len(sys.argv):
                    input_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
                    provider = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--deployment" and i + 1 < len(sys.argv):
                    deployment = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--voice" and i + 1 < len(sys.argv):
                    voice = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--speed" and i + 1 < len(sys.argv):
                    speed = float(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == "--style" and i + 1 < len(sys.argv):
                    kwargs["style"] = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--rate" and i + 1 < len(sys.argv):
                    kwargs["rate"] = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--pitch" and i + 1 < len(sys.argv):
                    kwargs["pitch"] = sys.argv[i + 1]
                    i += 2
                else:
                    print(f"Warning: Unknown argument '{sys.argv[i]}'")
                    i += 1
            
            synthesize_from_file(input_file, provider, deployment, voice, output, speed, **kwargs)
        
        elif command == "providers":
            list_providers()
        
        elif command == "deployments":
            list_deployments()
        
        elif command == "voices":
            provider = sys.argv[2] if len(sys.argv) > 2 else None
            deployment = sys.argv[3] if len(sys.argv) > 3 else None
            list_voices(provider, deployment)
        
        elif command == "voice-info":
            if len(sys.argv) < 3:
                print("Error: Voice name required for 'voice-info' command")
                print("Usage: python main.py voice-info <voice-name> [--provider <name>]")
                sys.exit(1)
            
            voice_name = sys.argv[2]
            provider = None
            
            # Parse optional provider argument
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
                    provider = sys.argv[i + 1]
                    i += 2
                else:
                    print(f"Warning: Unknown argument '{sys.argv[i]}'")
                    i += 1
            
            # Default to azure-speech if no provider specified
            if provider is None:
                provider = "azure-speech"
            
            show_voice_info(voice_name, provider)
        
        else:
            print(f"Error: Unknown command '{command}'")
            print_usage()
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
