# AI Voice - Multi-Provider Text-to-Speech Solution

## Project Description

AI Voice is a centralized Python solution for text-to-speech conversion that supports multiple Azure AI providers with file-based input and advanced SSML support. It provides a unified interface for both simple voice synthesis and sophisticated speech control through SSML markup.

## Key Features

### Core Capabilities

- **Multi-Provider Architecture**: Unified interface for Azure OpenAI TTS and Azure AI Speech
- **File-Based Processing**: Read plain text or SSML files for batch processing
- **Flexible Configuration**: Environment-based settings with support for multiple deployments
- **Rich Voice Library**: Access to 6 Azure OpenAI voices or 567+ Azure neural voices
- **SSML Support**: Full control over speaking styles, prosody, emphasis, and multilingual content
- **Command-Line Interface**: Comprehensive CLI for synthesis, voice discovery, and inspection
- **Extensible Design**: Factory pattern enables easy addition of new TTS providers

### Technical Features

- Modern Python packaging with UV
- Provider abstraction layer
- Dynamic voice retrieval and caching
- Automatic SSML detection
- UTF-8 input support for international characters
- Auto-generated output file naming with timestamps

## Overview

### Vision

Create a developer-friendly, production-ready text-to-speech solution that abstracts away provider-specific complexities while exposing advanced features when needed.

### Scope

**In Scope:**
- Azure OpenAI TTS integration
- Azure AI Speech integration with full SSML support
- File-based input/output workflows
- Voice discovery and inspection
- CLI-based operation
- Multiple deployment configurations

**Out of Scope:**
- Real-time streaming synthesis
- Web API or REST endpoints
- Non-Azure TTS providers (currently)
- Audio post-processing or effects
- GUI interface

## High-Level Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                             │
│                         (main.py)                                │
│  Commands: synthesize | providers | voices | voice-info         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Provider Factory                              │
│                     (factory.py)                                 │
│  Instantiates providers based on configuration                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├──────────────────┬──────────────────────────────┐
                 ▼                  ▼                              ▼
        ┌──────────────┐   ┌──────────────┐            ┌──────────────┐
        │   TTSProvider│   │   TTSProvider│            │  Future      │
        │  (Abstract)  │   │  (Abstract)  │            │  Providers   │
        └──────┬───────┘   └──────┬───────┘            └──────────────┘
               │                  │
               ▼                  ▼
    ┌──────────────────┐ ┌──────────────────┐
    │  Azure OpenAI    │ │  Azure Speech    │
    │    Provider      │ │    Provider      │
    │                  │ │                  │
    │ - 6 voices       │ │ - 567+ voices    │
    │ - Speed control  │ │ - SSML support   │
    │ - tts-1/tts-1-hd │ │ - Styles/prosody │
    └────────┬─────────┘ └────────┬─────────┘
             │                    │
             ▼                    ▼
    ┌─────────────────────────────────────┐
    │      Azure AI Services              │
    │  (OpenAI API / Speech SDK)          │
    └─────────────────────────────────────┘
```

### Data Flow

#### Text Synthesis Flow

```
1. Input
   ├─ input/text.txt (default)
   └─ Custom file path (--input)
        │
        ▼
2. Detection
   ├─ Plain text → Direct synthesis
   └─ SSML (<?xml or <speak>) → SSML synthesis
        │
        ▼
3. Provider Selection
   ├─ Environment default (DEFAULT_PROVIDER)
   └─ CLI parameter (--provider)
        │
        ▼
4. Synthesis
   ├─ Azure OpenAI → openai.audio.speech.create()
   └─ Azure Speech → speechsdk.SpeechSynthesizer()
        │
        ▼
5. Output
   └─ output/{provider}_{voice}_{timestamp}.mp3
```

#### SSML Processing Flow

```
SSML File → Parser → Voice Configuration
                    ├─ Voice Name
                    ├─ Speaking Style
                    ├─ Prosody (rate/pitch/volume)
                    ├─ Emphasis & Breaks
                    └─ Language Switching
                         │
                         ▼
                   Azure Speech SDK
                         │
                         ▼
                    Audio Output
```

## Example Workflows

### Workflow 1: Simple Text-to-Speech

**Use Case**: Convert a short text message to speech with default settings

**Input** (`input/text.txt`):
```
Welcome to our service! We're here to help you 24/7.
```

**Command**:
```powershell
uv run python main.py synthesize --provider azure-speech
```

**Output**: `output/azure-speech_Jenny_20251031_142530.mp3`

---

### Workflow 2: Multi-Style Customer Service Message

**Use Case**: Create a customer service greeting with varying emotional tones

**Input** (`input/examples/customer_service.ssml`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
    
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="cheerful">
            <prosody rate="1.05" pitch="+3%">
                Hello! Welcome to our customer service.
            </prosody>
        </mstts:express-as>
        
        <break time="600ms"/>
        
        <mstts:express-as style="customerservice">
            <prosody rate="0.95">
                How may I assist you today?
            </prosody>
        </mstts:express-as>
    </voice>
</speak>
```

**Command**:
```powershell
Copy-Item input\examples\customer_service.ssml input\text.txt
uv run python main.py synthesize --provider azure-speech --output customer_greeting.mp3
```

**Output**: `output/customer_greeting.mp3` with natural voice transitions

---

### Workflow 3: Multilingual Announcement

**Use Case**: Create an announcement in multiple languages using one voice

**Input** (`input/examples/multilingual.ssml`):
```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
    
    <voice name="en-US-AndrewMultilingualNeural">
        <p>Welcome to the international conference.</p>
        <p><lang xml:lang="es-ES">Bienvenidos a la conferencia internacional.</lang></p>
        <p><lang xml:lang="fr-FR">Bienvenue à la conférence internationale.</lang></p>
        <p><lang xml:lang="ja-JP">国際会議へようこそ。</lang></p>
    </voice>
</speak>
```

**Command**:
```powershell
Copy-Item input\examples\multilingual.ssml input\text.txt
uv run python main.py synthesize --provider azure-speech
```

**Output**: Single audio file with seamless language transitions

---

### Workflow 4: Voice Discovery & Inspection

**Use Case**: Find and inspect voices with specific capabilities

**Commands**:
```powershell
# List all available voices
uv run python main.py voices azure-speech

# Inspect specific voice for styles and features
uv run python main.py voice-info en-US-AriaNeural
```

**Output**:
```
Voice Information: en-US-AriaNeural
======================================================================
Full Name:      Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)
Locale:         en-US
Gender:         Female
Voice Type:     Neural

Available Styles (16):
  - chat
  - customerservice
  - cheerful
  - empathetic
  - excited
  - friendly
  ...
```

---

### Workflow 5: Educational Content with Natural Pacing

**Use Case**: Create educational audio with proper pacing and emphasis

**Input** (`input/examples/education_recursion.ssml`):
```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
    
    <voice name="en-US-GuyNeural">
        <prosody rate="0.85" pitch="-2%">
            Today we'll learn about recursion in programming.
            <break time="800ms"/>
            Recursion is when a function calls itself to solve a problem.
        </prosody>
    </voice>
</speak>
```

**Command**:
```powershell
Copy-Item input\examples\education_recursion.ssml input\text.txt
uv run python main.py synthesize --provider azure-speech --output education.mp3
```

**Output**: Natural-sounding educational content with appropriate pacing

---

### Workflow 6: Batch Processing Multiple Scripts

**Use Case**: Convert multiple script files to audio

**Commands**:
```powershell
# Process all text files in input folder
foreach ($file in Get-ChildItem input\*.txt) {
    $outputName = $file.BaseName + ".mp3"
    uv run python main.py synthesize --input $file --output $outputName
}
```

**Output**: Multiple audio files, one for each input file

## Project Structure

```
ai-voice/
├── main.py                      # CLI entry point with command handlers
│
├── input/                       # Input files
│   ├── text.txt                # Default input (user-created)
│   └── examples/               # SSML example templates
│       ├── customer_service.ssml
│       ├── announcement.ssml
│       ├── multilingual.ssml
│       └── education_recursion.ssml
│
├── output/                      # Generated audio files (auto-created)
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── config.py               # Environment configuration with Pydantic
│   ├── factory.py              # Provider factory and registry
│   └── providers/              # TTS provider implementations
│       ├── __init__.py
│       ├── base.py             # Abstract TTSProvider base class
│       ├── azure_openai.py     # Azure OpenAI TTS implementation
│       └── azure_speech.py     # Azure AI Speech implementation
│
├── pyproject.toml              # UV project configuration
├── .env.example                # Environment template
├── .env                        # User configuration (git-ignored)
└── README.md                   # Detailed documentation
```

## Technology Stack

### Core Technologies
- **Python 3.10+**: Primary language
- **UV**: Modern Python package manager
- **Pydantic**: Configuration and data validation

### Azure Services
- **Azure OpenAI**: TTS-1 and TTS-1-HD models
- **Azure AI Speech**: Neural text-to-speech with SSML

### Key Libraries
- `openai` (>=1.0.0): Azure OpenAI SDK
- `azure-cognitiveservices-speech` (>=1.40.0): Azure Speech SDK
- `pydantic-settings` (>=2.0.0): Configuration management

## Design Patterns

### Factory Pattern
The `ProviderFactory` class uses a registry pattern to instantiate TTS providers based on configuration, enabling easy extensibility.

### Abstract Base Class
All providers inherit from `TTSProvider`, ensuring consistent interface across implementations:
- `synthesize()`: Convert text to speech
- `get_available_voices()`: List available voices
- `provider_name`: Provider identification

### Strategy Pattern
Provider selection is dynamic based on configuration or CLI parameters, allowing runtime switching between different TTS strategies.

## Configuration Management

### Environment-Based
All sensitive credentials and settings stored in `.env` file:
- API keys and endpoints
- Default provider selection
- Voice preferences
- Deployment configurations

### Multi-Deployment Support
Azure OpenAI supports multiple deployment configurations for different use cases:
```env
AZURE_OPENAI_DEPLOYMENTS=standard:tts-1:alloy|hd:tts-1-hd:nova
```

## Extensibility

### Adding New Providers

The architecture supports adding new TTS providers with minimal changes:

1. Create new provider class inheriting from `TTSProvider`
2. Implement required methods: `synthesize()`, `get_available_voices()`, `provider_name`
3. Register in `ProviderFactory`
4. Add configuration to `.env.example`

**Potential Future Providers:**
- Google Cloud Text-to-Speech
- AWS Polly
- ElevenLabs
- Local TTS engines (pyttsx3, Coqui TTS)

## Use Case Categories

### 1. Content Creation
- Podcast intros/outros
- YouTube video narration
- Audiobook generation
- E-learning content

### 2. Accessibility
- Screen reader content
- Audio descriptions
- Document reading assistance

### 3. Customer Service
- IVR messages
- Hold music alternatives
- Multi-language support messages

### 4. Marketing
- Advertisement voiceovers
- Product demonstrations
- Social media content

### 5. Development & Testing
- Voice assistant prototyping
- UI/UX testing with audio feedback
- Automated voice response systems

## Performance Considerations

### Audio Generation Times
- **Azure OpenAI**: ~2-3 seconds for short texts (<100 words)
- **Azure Speech**: ~1-2 seconds for short texts, longer for complex SSML

### File Sizes
- **MP3 (16kHz)**: ~15 KB per second of audio
- **WAV (24kHz)**: ~48 KB per second of audio

### Rate Limits
- Azure OpenAI: 3 requests per minute (varies by tier)
- Azure Speech: 20 concurrent requests (varies by tier)

## Security Considerations

- ✅ API keys stored in `.env` (git-ignored)
- ✅ No hardcoded credentials
- ✅ Environment-based configuration
- ⚠️ Input validation on file paths
- ⚠️ Output directory permissions

## Future Enhancements

### Planned Features
- Streaming synthesis for real-time applications
- Audio format conversion options
- Voice cloning with Azure Personal Voice (requires Limited Access)
- Batch processing optimization
- Web API wrapper for remote access

### Potential Improvements
- Caching frequently used syntheses
- Audio quality presets
- Voice recommendation engine
- SSML template generator
- Progress indicators for long texts

## Getting Started

See [README.md](README.md) for detailed installation instructions, configuration guide, and usage examples.

**Quick Start:**
```powershell
# Install and configure
uv sync
cp .env.example .env
# Edit .env with your credentials

# Create input
"Hello, world!" | Out-File -FilePath input\text.txt -Encoding UTF8

# Generate speech
uv run python main.py synthesize --provider azure-speech
```

## License

MIT License - See project repository for details.

---

*Last Updated: October 2025*
