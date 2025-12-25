"""
Configuration module for Reel Automation
Loads settings from .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')

# Helper function to construct paths that work on both Windows and WSL
def _get_localappdata_paths():
    """Get LOCALAPPDATA paths for both Windows and WSL"""
    paths = []

    # Try Windows LOCALAPPDATA environment variable (native Windows)
    localappdata = os.environ.get('LOCALAPPDATA')
    if localappdata:
        paths.append(localappdata)

    # Try common WSL paths (when running from WSL)
    # Get username from HOME or USER environment variable
    home = os.environ.get('HOME', '')
    if '/home/' in home or '/root' in home:
        # We're in WSL, construct Windows path
        username = os.environ.get('USER', os.environ.get('USERNAME', ''))
        if username:
            wsl_localappdata = f'/mnt/c/Users/{username}/AppData/Local'
            paths.append(wsl_localappdata)

    return paths

# CapCut Configuration
# Try CapCut first (international version), then JianyingPro (Chinese version)

# Helper function to get CapCut projects root path
def _get_capcut_projects_root():
    """Get CapCut projects root path for both Windows and WSL"""
    # Try to get paths from LOCALAPPDATA
    localappdata_paths = _get_localappdata_paths()
    
    candidates = []

    for localappdata in localappdata_paths:
        # Candidate 1: CapCut (international version)
        capcut_path = os.path.join(localappdata, 'CapCut', 'User Data', 'Projects', 'com.lveditor.draft')
        if os.path.exists(capcut_path):
            candidates.append(capcut_path)

        # Candidate 2: JianyingPro (Chinese version)
        jianyingpro_path = os.path.join(localappdata, 'JianyingPro', 'User Data', 'Projects', 'com.lveditor.draft')
        if os.path.exists(jianyingpro_path):
            candidates.append(jianyingpro_path)

    if not candidates:
        # Fallback for WSL when no paths detected
        username = os.environ.get('USER', os.environ.get('USERNAME', 'user'))
        return f'/mnt/c/Users/{username}/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft'
        
    if len(candidates) == 1:
        return candidates[0]
        
    # If multiple candidates exist, find the one with the most recently modified project
    best_candidate = candidates[0]
    latest_mtime = 0
    
    for candidate in candidates:
        try:
            # Check modification time of the directory itself
            mtime = os.path.getmtime(candidate)
            
            # Also check subdirectories (projects) to be more accurate
            # because the root folder mtime might not update when a subdir is modified
            import glob
            subdirs = glob.glob(os.path.join(candidate, '*'))
            for d in subdirs:
                if os.path.isdir(d):
                    try:
                        pmtime = os.path.getmtime(d)
                        if pmtime > mtime:
                            mtime = pmtime
                    except:
                        pass
            
            if mtime > latest_mtime:
                latest_mtime = mtime
                best_candidate = candidate
        except:
            pass
            
    return best_candidate

CAPCUT_PROJECTS_ROOT = _get_capcut_projects_root()
GAP_BETWEEN_REELS_SECONDS = int(os.getenv('GAP_BETWEEN_REELS_SECONDS', '10'))
MAX_REEL_DURATION = int(os.getenv('MAX_REEL_DURATION', '58'))

# Cut Buffer Configuration (prevents cutting words mid-sentence)
CUT_START_BUFFER_SECONDS = float(os.getenv('CUT_START_BUFFER_SECONDS', '0.8'))
CUT_END_BUFFER_SECONDS = float(os.getenv('CUT_END_BUFFER_SECONDS', '0.8'))

# Transcription Configuration
TRANSCRIPTION_METHOD = os.getenv('TRANSCRIPTION_METHOD', 'local').lower()
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')

# Gemini Rate Limiting
GEMINI_API_DELAY_SECONDS = int(os.getenv('GEMINI_API_DELAY_SECONDS', '5'))

# Reel Generation Settings
MIN_REELS_PER_3MIN = int(os.getenv('MIN_REELS_PER_3MIN', '1'))
REEL_GENERATION_MODE = os.getenv('REEL_GENERATION_MODE', 'balanced').lower()

# CapCut Executable Path (Windows)
# Support both CapCut (international) and JianyingPro (Chinese) versions
# Also support both native Windows and WSL paths

# Build executable paths
CAPCUT_EXE_PATHS = []

# Add LOCALAPPDATA-based paths (works for both Windows and WSL)
for localappdata in _get_localappdata_paths():
    # CapCut (international version)
    CAPCUT_EXE_PATHS.append(os.path.join(localappdata, 'CapCut', 'Apps', 'CapCut.exe'))
    # JianyingPro (Chinese version)
    CAPCUT_EXE_PATHS.append(os.path.join(localappdata, 'JianyingPro', 'Apps', 'JianyingPro.exe'))

# Add standard Program Files paths
CAPCUT_EXE_PATHS.extend([
    r'C:\Program Files\CapCut\CapCut.exe',
    r'C:\Program Files (x86)\CapCut\CapCut.exe',
    r'C:\Program Files\JianyingPro\JianyingPro.exe',
    r'C:\Program Files (x86)\JianyingPro\JianyingPro.exe',
    # WSL paths for Program Files
    '/mnt/c/Program Files/CapCut/CapCut.exe',
    '/mnt/c/Program Files (x86)/CapCut/CapCut.exe',
    '/mnt/c/Program Files/JianyingPro/JianyingPro.exe',
    '/mnt/c/Program Files (x86)/JianyingPro/JianyingPro.exe',
])

def validate_config():
    """Validate configuration settings"""
    errors = []

    if AI_PROVIDER == 'openai' and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required when using OpenAI provider")

    if AI_PROVIDER == 'anthropic' and not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY is required when using Anthropic provider")

    if AI_PROVIDER == 'gemini' and not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is required when using Gemini provider")

    if AI_PROVIDER not in ['openai', 'anthropic', 'gemini']:
        errors.append(f"Invalid AI_PROVIDER: {AI_PROVIDER}. Must be 'openai', 'anthropic', or 'gemini'")

    if TRANSCRIPTION_METHOD not in ['local', 'online']:
        errors.append(f"Invalid TRANSCRIPTION_METHOD: {TRANSCRIPTION_METHOD}. Must be 'local' or 'online'")

    return errors

def get_capcut_executable():
    """Find CapCut executable path"""
    for path in CAPCUT_EXE_PATHS:
        if os.path.exists(path):
            return path
    return None
