# Architecture Documentation

## System Overview

This is a fully automated pipeline that converts long-form videos into short-form reels without manual intervention.

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              GUI (gui.py)                               │  │
│  │  - File selection dialog                                │  │
│  │  - Progress tracking                                     │  │
│  │  - Log display                                          │  │
│  │  - Configuration validation                             │  │
│  └────────────────────┬────────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE ORCHESTRATOR                        │
│                      (pipeline.py)                              │
│                                                                 │
│  Coordinates all steps and manages workflow:                   │
│  1. Transcription                                              │
│  2. AI Analysis                                                │
│  3. Project Generation                                         │
│  4. CapCut Launch                                              │
└───┬─────────────────┬─────────────────┬────────────────────┬───┘
    │                 │                 │                    │
    ▼                 ▼                 ▼                    ▼
┌─────────┐   ┌────────────┐   ┌───────────┐   ┌──────────────┐
│ Whisper │   │    AI      │   │  CapCut   │   │   CapCut     │
│  Model  │   │ Timestamp  │   │  Project  │   │   Launcher   │
│         │   │ Generator  │   │ Generator │   │              │
└─────────┘   └────────────┘   └───────────┘   └──────────────┘
```

## Module Breakdown

### 1. Configuration Layer (`config.py`)

**Purpose**: Centralized configuration management

**Responsibilities**:
- Load environment variables from `.env`
- Validate API keys
- Define constants (paths, settings)
- Locate CapCut executable

**Key Functions**:
- `validate_config()` - Ensures all required settings are present
- `get_capcut_executable()` - Finds CapCut installation

### 2. GUI Layer (`gui.py`)

**Purpose**: User interface for video selection and progress monitoring

**Components**:
- **Video Selection**: File browser for input video
- **Progress Bar**: Visual feedback of pipeline progress
- **Log Display**: Real-time logging of all operations
- **Status Updates**: Current step information

**Threading**:
- Main thread: GUI event loop
- Worker thread: Pipeline execution
- Communication via `root.after()` for thread-safe UI updates

### 3. Pipeline Orchestrator (`pipeline.py`)

**Purpose**: Coordinates the entire workflow

**Class**: `ReelAutomationPipeline`

**Workflow**:
```python
def run(video_path):
    1. _transcribe_video()      # 0-30%
    2. _generate_timestamps()   # 30-60%
    3. _create_capcut_project() # 60-90%
    4. _launch_capcut()         # 90-100%
```

**Features**:
- Progress callbacks for UI updates
- Logging callbacks for transparency
- Error handling and recovery
- Resource cleanup

### 4. Transcription Module (`transcribe.py` + Pipeline integration)

**Purpose**: Convert speech to text with timestamps

**Technology**: OpenAI Whisper (runs locally)

**Process**:
1. Load Whisper model (cached for reuse)
2. Transcribe audio track
3. Generate timestamped segments
4. Save to `.transcript.txt`

**Output Format**:
```
[00:00:05 -> 00:00:15] Spoken text here
[00:00:15 -> 00:00:25] More spoken text
```

**Model Options**:
- `tiny`: Fastest, least accurate (~1GB RAM)
- `base`: Good balance (~1GB RAM) ⭐ Default
- `small`: Better accuracy (~2GB RAM)
- `medium`: High accuracy (~5GB RAM)
- `large`: Best accuracy (~10GB RAM)

### 5. AI Timestamp Generator (`ai_timestamp_generator.py`)

**Purpose**: Analyze transcript and generate optimal reel cuts

**Class**: `AITimestampGenerator`

**Supported Providers**:
- **OpenAI**: GPT-4 Turbo, GPT-4, GPT-3.5 Turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus

**AI Prompt Strategy**:

The system uses a specialized prompt that instructs the AI to:

1. **Identify Themes**: Find compelling narrative threads
2. **Apply Formula**: Structure reels as Hook → Context → Payoff
3. **Optimize Flow**: Ensure smooth audio transitions
4. **Time Constraint**: Keep reels under 58 seconds
5. **Re-arrange**: Can move segments for maximum impact

**Input**: Full transcript with timestamps

**Output**: Structured reel data
```python
[
    [("00:15:30", "00:15:35", "HOOK"), ("00:01:00", "00:01:10", "CONTEXT"), ...],
    [("00:20:00", "00:20:05", "HOOK"), ...],
]
```

**Parsing**:
- Regex-based timestamp extraction
- Handles multiple formats: `HH:MM:SS`, `MM:SS`, `HH:MM:SS.ms`
- Separates reels by blank lines
- Extracts comments for context

### 6. CapCut Project Generator (`capcut_project_generator.py`)

**Purpose**: Create valid CapCut projects from scratch

**Class**: `CapCutProjectGenerator`

**Process**:

1. **Create Project Folder**
   - Generate UUID for project
   - Create folder in CapCut's project directory
   - `%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft\{UUID}`

2. **Copy Video**
   - Copy source video to project folder
   - Preserve original video file

3. **Generate `draft_info.json`**
   - Material references (video file)
   - Track structure (video + audio)
   - Segment definitions with timeranges

4. **Apply Cuts**
   - Create segments for each timestamp pair
   - Set `source_timerange` (what part of video to play)
   - Set `target_timerange` (where to place on timeline)
   - Add gaps between reels (default: 10 seconds)

**JSON Structure**:
```json
{
  "version": "7.7.0",
  "duration": 1234567890,  // microseconds
  "materials": {
    "videos": [{ "id": "...", "path": "..." }]
  },
  "tracks": [
    {
      "type": "video",
      "segments": [
        {
          "id": "unique-uuid",
          "source_timerange": { "start": 100000, "duration": 50000 },
          "target_timerange": { "start": 0, "duration": 50000 }
        }
      ]
    }
  ]
}
```

**Key Concepts**:
- **Source Timerange**: Which part of the original video to use
- **Target Timerange**: Where to place it on the timeline
- **Segments**: Individual video clips on the timeline
- **Tracks**: Layers (video, audio, effects)

### 7. CapCut Launcher

**Purpose**: Open CapCut with the generated project

**Implementation**:
```python
subprocess.Popen([capcut_exe],
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    stdout=DEVNULL, stderr=DEVNULL)
```

**Search Paths**:
1. `%LOCALAPPDATA%\JianyingPro\Apps\JianyingPro.exe`
2. `C:\Program Files\JianyingPro\JianyingPro.exe`
3. `C:\Program Files (x86)\JianyingPro\JianyingPro.exe`

**Fallback**: If not found, project is still created - user opens manually

## Data Flow

### Video Processing Pipeline

```
┌──────────────┐
│ Input Video  │
│  (MP4, etc)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│   Whisper Model      │
│  - Load audio track  │
│  - Transcribe        │
│  - Generate segments │
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────┐
│     Transcript File         │
│ [00:00:05 -> 00:00:15] ...  │
│ [00:00:15 -> 00:00:25] ...  │
└──────┬──────────────────────┘
       │
       ▼
┌────────────────────────────┐
│   AI Analysis (GPT/Claude) │
│  - Read transcript         │
│  - Identify themes         │
│  - Apply formula           │
│  - Generate timestamps     │
└──────┬─────────────────────┘
       │
       ▼
┌───────────────────────────────┐
│    Timestamp Data             │
│ Reel 1: [(start, end), ...]   │
│ Reel 2: [(start, end), ...]   │
└──────┬────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  CapCut Project Generator    │
│  - Create project folder     │
│  - Copy video                │
│  - Generate JSON             │
│  - Apply cuts                │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│   CapCut Project Folder      │
│   ├── draft_info.json        │
│   └── video.mp4              │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│     Launch CapCut            │
│  Opens with project loaded   │
└──────────────────────────────┘
```

## Future Architecture (Batch Processing)

The current architecture is designed to support batch processing:

```
┌─────────────────────────────────────┐
│   Batch Processor (future)          │
│                                     │
│   For each video in input folder:  │
│     1. Run pipeline                │
│     2. Create separate project     │
│     3. Organize output             │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Output Structure:                 │
│   output/                           │
│   ├── video1_reels/                │
│   │   └── [CapCut Project]         │
│   ├── video2_reels/                │
│   │   └── [CapCut Project]         │
│   └── ...                           │
└─────────────────────────────────────┘
```

**Implementation Plan**:
1. Create `batch_processor.py`
2. Add parallel processing (concurrent videos)
3. Organize projects in separate folders
4. Generate batch report
5. Optional: Auto-export from CapCut via automation

## Error Handling

### Configuration Errors
- **No API Key**: Detected on startup, GUI disabled
- **Invalid Provider**: Validation error shown
- **Missing .env**: Warning with setup instructions

### Pipeline Errors
- **File Not Found**: Video path validation
- **Transcription Failed**: Whisper error catching
- **AI API Error**: Rate limiting, network issues
- **Project Creation Failed**: Disk space, permissions

### Recovery Strategies
- **Caching**: Whisper model loaded once
- **Retries**: API calls with exponential backoff (future)
- **Logging**: Detailed error messages in GUI
- **Graceful Degradation**: Project created even if CapCut launch fails

## Performance Considerations

### Bottlenecks
1. **Whisper Transcription**: 10-30% of real-time (depends on model)
2. **AI API Call**: 5-30 seconds (depends on transcript length)
3. **File Operations**: Minimal (< 1 second)

### Optimization Opportunities
- **Model Caching**: Whisper model loaded once ✅
- **GPU Acceleration**: Whisper can use CUDA (future)
- **Parallel Processing**: Batch mode can process multiple videos (future)
- **Async API Calls**: Non-blocking AI requests (future)

### Resource Usage
- **RAM**: 1-10 GB (depends on Whisper model)
- **Disk**: ~2x video size (original + project copy)
- **Network**: ~1-10 KB for AI API (transcript + response)

## Security Considerations

### API Keys
- Stored in `.env` (not committed to git)
- Validated on startup
- Never logged or displayed

### File Handling
- Input validation (file exists, readable)
- Safe path construction (prevent traversal)
- Backup creation before modifications

### External Dependencies
- Whisper: Runs locally (no data sent externally)
- AI APIs: Only transcript sent (no video data)
- CapCut: Project files follow official format

## Testing Strategy

### Unit Tests (Future)
- Configuration validation
- Timestamp parsing
- Time format conversion
- JSON structure generation

### Integration Tests (Future)
- Full pipeline with sample video
- AI API mocking
- CapCut project validation

### Manual Testing Checklist
- [ ] GUI launches without errors
- [ ] Video file selection works
- [ ] Progress bar updates correctly
- [ ] Logs display properly
- [ ] CapCut project is valid
- [ ] CapCut opens with project

## Deployment

### For Team Use

1. **Shared Setup**:
   - One `.env.example` in repository
   - Each team member creates their own `.env`
   - API keys can be shared or individual

2. **Distribution**:
   - Clone repository
   - Run setup script
   - Launch via batch file

3. **Updates**:
   - Pull latest code
   - Re-run `pip install -r requirements.txt`
   - Restart application

### For Production (Future)

- **Docker Container**: Package with dependencies
- **Executable**: PyInstaller for standalone app
- **Web Service**: Flask/FastAPI wrapper for API access
- **Cloud Deployment**: AWS Lambda for serverless processing

---

This architecture provides a solid foundation for the current single-video workflow while being designed for easy expansion to batch processing and additional features.
