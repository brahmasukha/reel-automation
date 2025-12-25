#!/usr/bin/env python
"""
Simple script to update gaps - copy and run this manually if needed
"""
import json
import shutil

project_path = "C:/Users/kenya/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1223"
draft_file = f"{project_path}/draft_content.json"

print("Reading project...")
with open(draft_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Backup
print("Creating backup...")
shutil.copy2(draft_file, f"{draft_file}.30s_gaps_backup")

# Find video track
video_track = None
for track in data.get('tracks', []):
    if track.get('type') == 'video':
        video_track = track
        break

segments = video_track['segments']
print(f"Found {len(segments)} segments")

# Find gaps (where segments jump more than 5 seconds)
new_segments = []
current_time = 0
reel_count = 1

for i, seg in enumerate(segments):
    src = seg['source_timerange']
    tgt = seg['target_timerange']

    # Check if there's a gap from previous segment
    if i > 0:
        prev_end = new_segments[-1]['target_timerange']['start'] + new_segments[-1]['target_timerange']['duration']
        old_gap = tgt['start'] - prev_end

        if old_gap > 5_000_000:  # 5+ second gap detected
            # This is a reel boundary - add 30 second gap
            current_time += 30_000_000
            reel_count += 1
            print(f"Reel {reel_count} starts at segment {i}")

    # Update segment timeline position
    seg['target_timerange']['start'] = current_time
    current_time += src['duration']
    new_segments.append(seg)

# Update track and duration
video_track['segments'] = new_segments
data['duration'] = current_time

# Save
print("Saving updated project...")
with open(draft_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ DONE! Updated {reel_count} reels with 30-second gaps")
print(f"Total duration: {current_time / 1_000_000:.0f} seconds")
print("\nOpen CapCut now - you'll see much bigger gaps between reels!")
