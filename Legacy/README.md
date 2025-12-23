# Legacy Files

This folder contains the **old manual workflow files** from the original reel automation system.

## ⚠️ These Files Are No Longer Used

The application has been **completely redesigned** with a fully automated workflow. These files are kept here for reference only.

---

## What's in This Folder

### Old Python Scripts

| File | What It Did | Replaced By |
|------|-------------|-------------|
| `transcribe.py` | Manual transcription script | Integrated into [pipeline.py](../pipeline.py) |
| `automate_cuts.py` | Manual cut application | Integrated into [capcut_project_generator.py](../capcut_project_generator.py) |
| `tool_apply_cuts_windows.py` | Windows-specific tool | No longer needed - automated in [pipeline.py](../pipeline.py) |

### Old Batch Files

| File | What It Did | Replaced By |
|------|-------------|-------------|
| `Get_Transcript.bat` | Launcher for transcription | [Launch_Reel_Automation.bat](../Launch_Reel_Automation.bat) + [gui.py](../gui.py) |
| `Apply_Cuts.bat` | Launcher for cuts application | Same as above |

### Old Configuration/Data

| File | What It Was | Replaced By |
|------|-------------|-------------|
| `cuts.txt` | Manual timestamp input file | AI generates timestamps automatically |
| `AI_Prompt.md` | Manual AI prompting guide | Built into [ai_timestamp_generator.py](../ai_timestamp_generator.py) |

### Old Documentation

| File | What It Was | Replaced By |
|------|-------------|-------------|
| `WINDOWS_SETUP.md` | Old setup guide | [START_HERE.md](../START_HERE.md), [SETUP_GUIDE.md](../SETUP_GUIDE.md), [GEMINI_SETUP.md](../GEMINI_SETUP.md) |

---

## Old vs New Workflow

### ❌ OLD WORKFLOW (These Files)

```
1. Run Get_Transcript.bat
   → User provides video path manually
   → Wait for transcription

2. Copy transcript
   → Open ChatGPT/Claude manually
   → Paste AI_Prompt.md
   → Paste transcript
   → Copy AI response

3. Create CapCut project
   → Open CapCut manually
   → Import video manually
   → Close CapCut

4. Edit cuts.txt
   → Paste timestamps manually
   → Add project path manually

5. Run Apply_Cuts.bat
   → Script applies cuts

6. Open CapCut manually
   → Review reels
```

**Manual Steps**: 6-7 steps with lots of copying/pasting

---

### ✅ NEW WORKFLOW (Current Codebase)

```
1. Double-click Launch_Reel_Automation.bat

2. Select video in GUI

3. Click "Process Video"

   ✨ Everything happens automatically ✨

4. CapCut opens with reels ready
```

**Manual Steps**: 2 clicks!

---

## Can I Delete This Folder?

**Yes!** These files are **not used** by the new system at all.

### Before Deleting

Make sure you're comfortable with the new workflow:
- ✅ GUI application works
- ✅ AI integration works (Gemini/OpenAI/Anthropic)
- ✅ CapCut projects generate correctly
- ✅ You've processed a few test videos successfully

### If You Need These Files

The only reason to keep them would be:
- Historical reference
- Learning how the old system worked
- Comparing old vs new approach

Otherwise, feel free to delete this entire folder!

---

## Migration Notes

### What Changed

| Old Component | New Component | Improvement |
|---------------|---------------|-------------|
| Manual transcription | Automated in pipeline | No user interaction needed |
| Manual AI prompting | Built-in AI integration | Direct API calls |
| Manual CapCut project creation | Automated project generation | Creates projects from scratch |
| Manual cuts.txt editing | AI generates timestamps | Zero manual editing |
| Multiple batch files | Single GUI application | One-click operation |

### Breaking Changes

**None!** The new system is a complete rewrite, not an update to the old system.

If for some reason you need to use the old workflow:
1. Keep this folder
2. Use the old batch files
3. Follow the old WINDOWS_SETUP.md

But we **strongly recommend** using the new automated system instead!

---

## File Details

### transcribe.py
- Used Whisper to transcribe videos
- Required manual video path input
- Saved transcript to `.transcript.txt`
- **Now**: Built into [pipeline.py](../pipeline.py) `_transcribe_video()` method

### automate_cuts.py
- Read `cuts.txt` for timestamps
- Modified existing CapCut projects
- Required project to exist first
- **Now**: Replaced by [capcut_project_generator.py](../capcut_project_generator.py) which creates projects from scratch

### tool_apply_cuts_windows.py
- Found latest CapCut project on Windows
- Updated `cuts.txt` with project path
- Called `automate_cuts.py`
- **Now**: Not needed - projects created directly

### cuts.txt
- Manual file with format:
  ```
  PATH: /path/to/draft_info.json

  00:18:06.0  00:18:25.0
  00:18:25.0  00:18:41.8
  ```
- **Now**: AI generates timestamps automatically via [ai_timestamp_generator.py](../ai_timestamp_generator.py)

### AI_Prompt.md
- Template for prompting ChatGPT/Claude
- User had to copy/paste manually
- **Now**: Built into `AITimestampGenerator.get_system_prompt()` with direct API integration

### Get_Transcript.bat & Apply_Cuts.bat
- Windows launchers for separate steps
- **Now**: Single [Launch_Reel_Automation.bat](../Launch_Reel_Automation.bat) + [gui.py](../gui.py) does everything

### WINDOWS_SETUP.md
- Setup guide for the old manual workflow
- **Now**: Replaced by modern documentation:
  - [START_HERE.md](../START_HERE.md) - Quick start
  - [SETUP_GUIDE.md](../SETUP_GUIDE.md) - Detailed setup
  - [GEMINI_SETUP.md](../GEMINI_SETUP.md) - FREE Gemini setup
  - [README.md](../README.md) - Full documentation

---

## Questions?

**Q: Should I delete this folder?**
A: Up to you! It's safe to delete once you're comfortable with the new system.

**Q: Can I use the old files?**
A: Yes, they still work independently, but the new system is much better!

**Q: What if the new system breaks?**
A: The new system is well-tested. If you have issues, check the documentation or the log output.

**Q: Can I mix old and new?**
A: No need to! The new system does everything the old system did, but automatically.

---

## Deletion Command

When you're ready to remove this folder:

**Windows (Command Prompt)**:
```cmd
rmdir /s /q Legacy
```

**Windows (PowerShell)**:
```powershell
Remove-Item -Recurse -Force Legacy
```

**Or**: Just right-click the folder and delete it!

---

**Last Updated**: December 2025
**System Version**: 2.0 (Fully Automated)
