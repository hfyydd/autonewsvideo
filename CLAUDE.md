# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated news video generator that transforms RSS news feeds into video content. It uses AI to rewrite news articles into video scripts, generates text-to-speech audio, creates adaptive card-style images, and composes them into final videos.

## Development Setup

This project uses `uv` for dependency management. Python 3.13+ is required.

### Common Commands

**Run the application:**
```bash
uv run main.py
```

**Install dependencies:**
```bash
uv sync
```

**Add new dependencies:**
```bash
uv add <package-name>
```

**Set API Key (for AI features):**
```bash
export QWEN_API_KEY="your-api-key"
```

## Architecture

### Modular Service Architecture

The application follows a clean separation between UI, business logic, and services:

```
GUI (Flet) → Models → Services → Output
```

### Core Components

1. **models/news.py**: Data models
   - `NewsItem`: Represents a single news article with AI-generated content and media assets
   - `VideoProject`: Video generation project configuration

2. **services/**:
   - `rss_fetcher.py`: Fetches news from multiple RSS sources in parallel
   - `ai_writer.py`: Uses Qwen (OpenAI-compatible) to generate video scripts with title + bullet points
   - `tts_service.py`: Edge TTS for speech synthesis, returns audio path and duration
   - `image_generator.py`: Creates adaptive-size news cards (1920x1080) using Pillow
   - `video_composer.py`: Composites images and audio using MoviePy

3. **main.py**: Flet GUI with 4-step workflow
   - Step 1: Fetch news from preset RSS categories
   - Step 2: Multi-select news items
   - Step 3: Configure style and voice
   - Step 4: Generate video with progress tracking

### Key Design Patterns

**Adaptive Card Layout**: Card dimensions are calculated dynamically based on content length
- `calculate_card_dimensions()` in image_generator.py analyzes title/bullet points
- Cards scale between min_height (500px) and max_height (980px)
- Always centered on 1920x1080 canvas

**Pipeline Processing**: Each news item goes through:
1. AI content generation (title + 2-4 bullet points)
2. TTS audio generation (full text → MP3 + duration)
3. Image generation (card with all content on one image)
4. Video composition (each image displays for its audio duration)

**Configuration**: All settings in `config.py`:
- RSS_PRESETS: Pre-configured news sources by category
- CARD_STYLES: Color schemes (blue/pink/green/purple)
- LAYOUT_CONFIG: Typography and spacing parameters
- TTS_VOICES: Available Edge TTS voices

### Application Flow

1. User selects RSS category → `fetch_multiple_sources()` retrieves news
2. User selects news items → stored in NewsItem list with `selected=True`
3. Click "Generate Video" triggers async pipeline:
   - For each selected news: `generate_news_card_content()` → AI rewrites
   - For each: `generate_news_audio()` → TTS creates audio + gets duration
   - For each: `create_adaptive_news_card()` → Pillow generates card image
   - Finally: `compose_news_collection_video()` → MoviePy concatenates all
4. Output video saved to `output/videos/news_collection.mp4`

### Important Implementation Details

- **Async handling**: TTS uses asyncio, wrapped in sync functions for Flet compatibility
- **Font fallback**: If fonts missing in `assets/fonts/`, uses default (may not display Chinese)
- **AI fallback**: If QWEN_API_KEY not set, uses `_generate_mock_content()` for testing
- **Error handling**: Each service has try/except with user-friendly error messages

## Dependencies

- **flet**: Cross-platform GUI framework
- **feedparser**: RSS/Atom parsing
- **openai**: SDK for Qwen API (OpenAI-compatible endpoint)
- **edge-tts**: Free, high-quality TTS
- **Pillow**: Image generation and manipulation
- **moviepy**: Video composition (requires ffmpeg)
- **mutagen**: Audio duration detection

## Output Structure

```
output/
├── images/       # news_card_000.png, news_card_001.png, ...
├── audio/        # news_000.mp3, news_001.mp3, ...
└── videos/       # news_collection.mp4
```

## Common Tasks

**Add new RSS source**: Edit `config.py` RSS_PRESETS

**Change card colors**: Modify `config.py` CARD_STYLES

**Adjust layout**: Update `config.py` LAYOUT_CONFIG (font sizes, spacing, etc.)

**Change TTS voice**: Add to `config.py` TTS_VOICES (see Edge TTS voice list)

**Debug card sizing**: Check console output from `create_adaptive_news_card()` which prints dimensions
