# 📏 Reel Gap Update Guide

## ✅ What I've Done

### 1. Updated Configuration Files
Changed the gap between reels from **10 seconds** to **30 seconds**:

- ✅ [.env](.env) - Line 24: `GAP_BETWEEN_REELS_SECONDS=30`
- ✅ [.env.example](.env.example) - Line 24: `GAP_BETWEEN_REELS_SECONDS=30`
- ✅ [capcut_project_generator.py](capcut_project_generator.py) - Fixed gap logic

**All future projects** will now have 30-second gaps between reels automatically!

---

## 🔧 Update Your Existing Project (1223)

Your current CapCut project (created today with 7 reels) still has 10-second gaps. To update it to 30-second gaps:

### Option 1: Run the Simple Script (EASIEST)

1. **Close CapCut** if it's open
2. Open Command Prompt or PowerShell
3. Navigate to the project folder:
   ```bash
   cd "C:\Users\kenya\Documents\BSK\Code\reel-automation"
   ```
4. Run the update script:
   ```bash
   python SIMPLE_update_gaps.py
   ```
5. Open CapCut - you'll see 30-second gaps!

### Option 2: Manual Python Execution

If you have Python installed directly:
```bash
python -c "import json, shutil; data=json.load(open('C:/Users/kenya/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1223/draft_content.json')); exec(open('SIMPLE_update_gaps.py').read())"
```

### Option 3: Re-generate Project

Just run your GUI app with the same video - it will create a NEW project with 30-second gaps automatically!

---

## 📊 What Changed

### Before (10-second gaps):
```
[Reel 1 segments] → 10s gap → [Reel 2 segments] → 10s gap → [Reel 3...]
```

### After (30-second gaps):
```
[Reel 1 segments] → 30s gap → [Reel 2 segments] → 30s gap → [Reel 3...]
```

**Why 30 seconds?**
- Much easier to visually identify reel boundaries in CapCut timeline
- Clear separation makes it easy to export individual reels
- Professional editors typically use 20-40 second gaps for reel separation

---

## 🎯 Verify the Update

After running the update script, open CapCut and check:

1. ✅ You should see **much larger gaps** between segment groups
2. ✅ Scroll through the timeline - each reel group is now clearly separated
3. ✅ Total project duration increased by ~120 seconds (6 gaps × 20 extra seconds)

---

## 🚨 Important Notes

- **Backup Created**: The script automatically creates a backup before modifying
  - Location: `draft_content.json.30s_gaps_backup`

- **Don't Panic**: If something goes wrong, you can restore from backup:
  1. Close CapCut
  2. Delete `draft_content.json`
  3. Rename `draft_content.json.30s_gaps_backup` to `draft_content.json`

- **Future Projects**: All new projects will automatically use 30-second gaps

---

## 📝 Files Modified

1. **[.env](c:\Users\kenya\Documents\BSK\Code\reel-automation\.env)** - Config updated
2. **[.env.example](c:\Users\kenya\Documents\BSK\Code\reel-automation\.env.example)** - Example updated
3. **[capcut_project_generator.py](c:\Users\kenya\Documents\BSK\Code\reel-automation\capcut_project_generator.py)** - Fixed gap calculation logic

## 📝 Scripts Created

1. **[SIMPLE_update_gaps.py](c:\Users\kenya\Documents\BSK\Code\reel-automation\SIMPLE_update_gaps.py)** - Simple one-time updater for existing project
2. **[update_gaps.py](c:\Users\kenya\Documents\BSK\Code\reel-automation\update_gaps.py)** - Full-featured updater with detailed output
3. **[analyze_project.py](c:\Users\kenya\Documents\BSK\Code\reel-automation\analyze_project.py)** - Analyze reel structure

---

## 🎬 Next Steps

1. **Update existing project**: Run `SIMPLE_update_gaps.py`
2. **Or regenerate**: Process the same video again with the GUI
3. **Check result**: Open CapCut and verify the 30-second gaps

---

**Questions?** The gaps are configured in [.env](c:\Users\kenya\Documents\BSK\Code\reel-automation\.env) line 24. You can change this to any value you want (15s, 45s, etc.)!
