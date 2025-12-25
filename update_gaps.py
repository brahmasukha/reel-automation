"""
Update CapCut project to increase gaps between reels from 10s to 30s
"""
import json
import shutil
from datetime import datetime

def update_reel_gaps(project_path, new_gap_seconds=30):
    """Update gaps between reels in existing CapCut project"""

    draft_content_path = f"{project_path}/draft_content.json"

    print(f"\n🔧 Updating CapCut Project: {project_path}")
    print(f"📏 New gap between reels: {new_gap_seconds} seconds\n")
    print("=" * 80)

    # Create backup
    backup_path = f"{project_path}/draft_content_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy2(draft_content_path, backup_path)
    print(f"✅ Backup created: {backup_path}")

    # Read project
    with open(draft_content_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find video track
    tracks = data.get('tracks', [])
    video_track = None
    for track in tracks:
        if track.get('type') == 'video':
            video_track = track
            break

    if not video_track:
        print("❌ No video track found!")
        return

    segments = video_track.get('segments', [])
    print(f"\n📊 Found {len(segments)} total segments")

    # Detect reels based on current gaps
    OLD_GAP_US = 10_000_000  # 10 seconds in microseconds
    NEW_GAP_US = new_gap_seconds * 1_000_000  # New gap in microseconds
    GAP_THRESHOLD = 5_000_000  # 5 seconds threshold to detect gaps

    reel_starts = []
    prev_end_time = 0

    for idx, segment in enumerate(segments):
        target_range = segment.get('target_timerange', {})
        target_start = target_range.get('start', 0)
        target_duration = target_range.get('duration', 0)

        if idx > 0:
            gap = target_start - prev_end_time
            if gap >= GAP_THRESHOLD:
                reel_starts.append(idx)  # Mark the start of a new reel

        prev_end_time = target_start + target_duration

    num_reels = len(reel_starts) + 1  # +1 for first reel
    print(f"🎬 Detected {num_reels} reels with {len(reel_starts)} gaps")

    # Rebuild timeline with new gaps
    print(f"\n🔨 Rebuilding timeline with {new_gap_seconds}s gaps...")

    current_timeline_pos = 0
    reel_idx = 0

    for seg_idx, segment in enumerate(segments):
        source_range = segment.get('source_timerange', {})
        duration_us = source_range.get('duration', 0)

        # Check if this is the start of a new reel
        if seg_idx in reel_starts:
            reel_idx += 1
            # Add new gap
            current_timeline_pos += NEW_GAP_US
            print(f"  ⏸  Gap #{reel_idx}: Added {new_gap_seconds}s gap before segment {seg_idx}")

        # Update segment timeline position
        segment['target_timerange']['start'] = current_timeline_pos
        current_timeline_pos += duration_us

    # Update total duration
    data['duration'] = current_timeline_pos

    # Save updated project
    with open(draft_content_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Project updated successfully!")
    print(f"📏 Total duration: {current_timeline_pos / 1_000_000:.1f}s")
    print(f"🎬 Reels: {num_reels}")
    print(f"⏸  Gaps: {len(reel_starts)} x {new_gap_seconds}s = {len(reel_starts) * new_gap_seconds}s total")
    print("\n💡 Open CapCut to see the changes. The gaps are now much more visible!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    # Update the latest project
    project_path = "C:/Users/kenya/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1223"
    update_reel_gaps(project_path, new_gap_seconds=30)
