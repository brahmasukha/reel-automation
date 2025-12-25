#!/usr/bin/env python
"""Check if gaps exist in CapCut project"""
import json
import sys
import os

# Find latest project
projects_root = "C:/Users/kenya/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft"

# Get all project folders
import glob
subdirs = glob.glob(os.path.join(projects_root, '*'))
valid_projects = []

for d in subdirs:
    if os.path.isdir(d) and os.path.exists(os.path.join(d, 'draft_content.json')):
        valid_projects.append(d)

if not valid_projects:
    print("No projects found!")
    sys.exit(1)

latest_project = max(valid_projects, key=os.path.getmtime)
project_file = os.path.join(latest_project, 'draft_content.json')

print(f'Analyzing: {os.path.basename(latest_project)}\n')

with open(project_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find video track
video_track = None
for track in data.get('tracks', []):
    if track.get('type') == 'video':
        video_track = track
        break

segments = video_track['segments']
print(f'Total segments: {len(segments)}')
print(f'Total duration: {data["duration"] / 1_000_000:.1f} seconds\n')

# Check ALL segments for gaps
print('Checking timeline positions...\n')
gap_count = 0

for i in range(min(15, len(segments))):  # Show first 15 segments
    seg = segments[i]
    tgt = seg['target_timerange']
    render_idx = seg.get('render_index', 'MISSING')
    start_sec = tgt['start'] / 1_000_000
    dur_sec = tgt['duration'] / 1_000_000
    end_sec = start_sec + dur_sec

    if i > 0:
        prev_end = segments[i-1]['target_timerange']['start'] + segments[i-1]['target_timerange']['duration']
        prev_end_sec = prev_end / 1_000_000
        gap_sec = start_sec - prev_end_sec

        print(f'Seg {i}: render_idx={render_idx}, start={start_sec:.1f}s, dur={dur_sec:.1f}s, gap_from_prev={gap_sec:.1f}s')

        if gap_sec > 1.0:  # Gap detected
            gap_count += 1
    else:
        print(f'Seg {i}: render_idx={render_idx}, start={start_sec:.1f}s, dur={dur_sec:.1f}s')

print(f'\n{"✅" if gap_count > 0 else "❌"} Found {gap_count} gaps in first 15 segments')

# Count all gaps
total_gaps = 0
for i in range(1, len(segments)):
    prev_end = segments[i-1]['target_timerange']['start'] + segments[i-1]['target_timerange']['duration']
    curr_start = segments[i]['target_timerange']['start']
    gap = curr_start - prev_end
    if gap > 1_000_000:  # 1+ second
        total_gaps += 1

print(f'Total gaps in ALL {len(segments)} segments: {total_gaps}\n')

input("Press Enter to exit...")
