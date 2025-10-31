# AI Voice

A centralized Python solution for text-to-speech conversion supporting multiple Azure AI providers with file-based input and SSML support.

## Features

- 🎯 **Multi-Provider Support**: Azure OpenAI TTS and Azure AI Speech
- 📄 **File-Based Input**: Read text from files or use SSML for advanced control
- 🔧 **Flexible Configuration**: Support for multiple Azure OpenAI deployments
- 🎨 **Rich Voice Selection**: 6 voices (Azure OpenAI) or 567+ voices (Azure Speech)
- 🎭 **SSML Support**: Full control over speaking styles, rate, pitch, and emphasis
- ⚙️ **Environment Config**: All settings in `.env` file
- 📦 **UV Project**: Modern Python packaging

## Quick Start

### 1. Install

```powershell
# Install UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your Azure credentials
```

### 2. Create Input

```powershell
"Hello, world!" | Out-File -FilePath input\text.txt -Encoding UTF8
```

### 3. Generate Speech

```powershell
# Azure OpenAI (simple, 6 voices)
uv run python main.py synthesize --provider azure-openai

# Azure AI Speech (advanced, 567+ voices with styles)
uv run python main.py synthesize --provider azure-speech --voice en-US-JennyNeural --style cheerful
```

## Configuration

Edit `.env` file:

```env
# Default provider
DEFAULT_PROVIDER=azure-speech

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENTS=tts-1:tts-1:alloy

# Azure AI Speech
AZURE_SPEECH_API_KEY=your_key
AZURE_SPEECH_REGION=eastus
AZURE_SPEECH_VOICE=en-US-JennyNeural
```

## Usage Examples

### Azure OpenAI (Simple TTS)

```powershell
# Basic
uv run python main.py synthesize --provider azure-openai

# Custom voice
uv run python main.py synthesize --provider azure-openai --voice nova

# Adjust speed
uv run python main.py synthesize --provider azure-openai --speed 1.2
```

**Voices**: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

### Azure AI Speech (Advanced TTS)

```powershell
# With voice
uv run python main.py synthesize --provider azure-speech --voice en-US-AriaNeural

# With style
uv run python main.py synthesize --provider azure-speech --style cheerful

# Adjust rate and pitch
uv run python main.py synthesize --provider azure-speech --rate 0.9 --pitch +5%

# Combined
uv run python main.py synthesize --provider azure-speech --voice en-US-GuyNeural --style excited --rate 1.1
```

**Popular Voices**:
- `en-US-JennyNeural`, `en-US-GuyNeural`, `en-US-AriaNeural`
- `en-GB-SoniaNeural`, `en-AU-NatashaNeural`
- `ja-JP-NanamiNeural`, `zh-CN-XiaoxiaoNeural`

[Full voice list](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts)

**Styles**: `cheerful`, `sad`, `angry`, `excited`, `friendly`, `calm`, `newscast`, `customerservice`

### Discovery Commands

```powershell
# List providers
uv run python main.py providers

# List all voices
uv run python main.py voices azure-speech

# Get voice details (styles, roles, properties)
uv run python main.py voice-info en-US-AriaNeural
```

### Custom Files

```powershell
# Use different input file
uv run python main.py synthesize --input my-script.txt

# Custom output
uv run python main.py synthesize --output my-audio.mp3
```

## SSML Support (Advanced)

SSML (Speech Synthesis Markup Language) gives you fine-grained control over speech synthesis. The project automatically detects SSML files (starting with `<?xml` or `<speak>`).

### SSML Examples

Ready-to-use examples are in `input/examples/`:

1. **customer_service.ssml** - Customer support with empathy
2. **announcement.ssml** - Marketing announcement with excitement  
3. **multilingual.ssml** - Multiple languages in one file
4. **education_recursion.ssml** - Educational content with natural pacing

### Using SSML Examples

```powershell
# Copy example to input
Copy-Item input\examples\customer_service.ssml input\text.txt

# Generate audio
uv run python main.py synthesize --provider azure-speech --output customer.mp3
```

### SSML Quick Reference

#### Basic Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
    
    <voice name="en-US-JennyNeural">
        Your text here
    </voice>
</speak>
```

#### Speaking Styles

```xml
<voice name="en-US-AriaNeural">
    <mstts:express-as style="cheerful">
        I'm so happy to help you today!
    </mstts:express-as>
</voice>
```

Available styles: `cheerful`, `sad`, `angry`, `excited`, `friendly`, `terrified`, `shouting`, `whispering`, `hopeful`, `calm`, `assistant`, `chat`, `customerservice`, `newscast`

#### Prosody (Rate, Pitch, Volume)

```xml
<voice name="en-US-GuyNeural">
    <!-- Slower speech, lower pitch -->
    <prosody rate="0.85" pitch="-2%">
        Speaking slowly and calmly.
    </prosody>
    
    <!-- Faster, higher pitch -->
    <prosody rate="1.3" pitch="+10%">
        Speaking quickly with excitement!
    </prosody>
</voice>
```

- **Rate**: `0.5` to `2.0` or `-50%` to `+100%`
- **Pitch**: `-50%` to `+50%`
- **Volume**: `0` to `100` or `x-soft`, `soft`, `medium`, `loud`, `x-loud`

#### Pauses (Breaks)

```xml
<voice name="en-US-JennyNeural">
    <p>First sentence. <break time="500ms"/> Second sentence.</p>
    <p>After this, a longer pause. <break time="1000ms"/> Continue here.</p>
</voice>
```

**Break strengths**: `x-weak`, `weak`, `medium`, `strong`, `x-strong`

#### Emphasis

```xml
<voice name="en-US-GuyNeural">
    This is <emphasis level="moderate">really</emphasis> important!
    This is <emphasis level="strong">extremely</emphasis> critical!
</voice>
```

**Levels**: `reduced`, `none`, `moderate`, `strong`

#### Multilingual

```xml
<voice name="en-US-AndrewMultilingualNeural">
    <p>Hello in English.</p>
    <p><lang xml:lang="es-ES">Hola en español.</lang></p>
    <p><lang xml:lang="fr-FR">Bonjour en français.</lang></p>
    <p><lang xml:lang="ja-JP">こんにちは日本語で。</lang></p>
</voice>
```

#### Say-As (Format Numbers, Dates, etc.)

```xml
<voice name="en-US-JennyNeural">
    <!-- Numbers -->
    <say-as interpret-as="cardinal">12345</say-as> items
    <say-as interpret-as="ordinal">3</say-as> place
    
    <!-- Dates -->
    <say-as interpret-as="date" format="mdy">10/31/2025</say-as>
    
    <!-- Time -->
    <say-as interpret-as="time" format="hms12">2:30pm</say-as>
    
    <!-- Phone -->
    <say-as interpret-as="telephone">555-123-4567</say-as>
</voice>
```

#### Paragraphs and Sentences

```xml
<voice name="en-US-AriaNeural">
    <p>This is the first paragraph.</p>
    <p>
        <s>First sentence.</s>
        <s>Second sentence.</s>
    </p>
</voice>
```

### Complete SSML Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
    
    <voice name="en-US-AriaNeural">
        <!-- Cheerful greeting -->
        <mstts:express-as style="cheerful">
            <prosody rate="1.05" pitch="+3%">
                Hello! Welcome to our service.
                <break time="600ms"/>
            </prosody>
        </mstts:express-as>
        
        <!-- Professional information -->
        <mstts:express-as style="customerservice">
            <prosody rate="0.95">
                <p>
                    We're here to help you <emphasis level="moderate">24/7</emphasis>.
                    <break time="400ms"/>
                    Your satisfaction is our priority.
                </p>
            </prosody>
        </mstts:express-as>
        
        <!-- Closing with calm tone -->
        <mstts:express-as style="calm">
            <prosody rate="0.9" pitch="-2%">
                Thank you for choosing us. Have a great day!
            </prosody>
        </mstts:express-as>
    </voice>
</speak>
```

### Creating Custom SSML

1. Create a new `.ssml` file in `input/examples/`
2. Use the structure and elements above
3. Copy to `input/text.txt` or use `--input` parameter
4. Generate: `uv run python main.py synthesize --provider azure-speech`

### SSML Best Practices

- ✅ Use `<p>` for paragraphs and `<s>` for sentences
- ✅ Add `<break>` between ideas (400-800ms)
- ✅ Keep rate between 0.8-1.2 for natural speech
- ✅ Use subtle pitch changes (-5% to +5%)
- ✅ Match styles to content (calm for meditation, excited for announcements)
- ❌ Don't overuse emphasis - reserve for key points
- ❌ Avoid extreme rate (<0.7 or >1.5) unless intentional
- ❌ Don't mix too many styles in one document

## Project Structure

```
ai-voice/
├── main.py              # CLI entry point
├── input/
│   ├── text.txt        # Default input (create this)
│   └── examples/       # SSML examples
│       ├── customer_service.ssml
│       ├── announcement.ssml
│       ├── multilingual.ssml
│       └── education_recursion.ssml
├── output/             # Generated audio (auto-created)
├── src/
│   ├── config.py       # Configuration
│   ├── factory.py      # Provider factory
│   └── providers/      # TTS implementations
└── .env               # Configuration (create from .env.example)
```

## CLI Reference

### Commands

```bash
synthesize              # Generate speech from text
providers               # List available providers
deployments             # List Azure OpenAI deployments
voices <provider>       # List voices for provider
voice-info <name>       # Get detailed voice information
```

### Synthesize Options

```bash
--provider <name>       # azure-openai | azure-speech
--input <file>          # Input file (default: input/text.txt)
--output <file>         # Output file (default: auto-generated)
--voice <name>          # Voice to use
--style <name>          # Speaking style (Azure Speech only)
--rate <value>          # Speech rate 0.5-2.0 (Azure Speech only)
--pitch <value>         # Pitch adjustment -50% to +50% (Azure Speech only)
--speed <value>         # Speed 0.25-4.0 (Azure OpenAI only)
--deployment <name>     # Deployment name (Azure OpenAI only)
```

## Requirements

- Python 3.10+
- UV package manager
- Azure OpenAI OR Azure AI Speech credentials

## License

MIT
