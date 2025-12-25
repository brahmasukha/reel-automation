#!/usr/bin/env python
"""
FINAL FIX for gaps issue.

The problem: CapCut is somehow still ignoring our timeline positions.
Let's check EVERY field that might affect segment positioning.
"""
import json
import os
import glob
import shutil

# Find latest project
projects_root = "C:/Users/kenya/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft"
subdirs = glob.glob(os.path.join(projects_root, '*'))
valid_projects = [d for d in subdirs if os.path.isdir(d) and os.path.exists(os.path.join(d, 'draft_content.json'))]

if not valid_projects:
    print("No projects found!")
    input("Press Enter to exit...")
    exit(1)

latest_project = max(valid_projects, key=os.path.getmtime)
draft_file = os.path.join(latest_project, 'draft_content.json')

print(f'Analyzing: {os.path.basename(latest_project)}\n')

with open(draft_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find video track
video_track = None
for track in data.get('tracks', []):
    if track.get('type') == 'video':
        video_track = track
        break

segments = video_track['segments']
print(f'Total segments: {len(segments)}')
print(f'Checking first 5 segments...\n')

# Check what fields exist in segments
for i in range(min(5, len(segments))):
    seg = segments[i]
    tgt = seg.get('target_timerange', {})
    src = seg.get('source_timerange', {})

    print(f'\nSegment {i}:')
    print(f'  render_index: {seg.get("render_index")}')
    print(f'  track_render_index: {seg.get("track_render_index")}')
    print(f'  target_timerange.start: {tgt.get("start", 0) / 1_000_000:.1f}s')
    print(f'  target_timerange.duration: {tgt.get("duration", 0) / 1_000_000:.1f}s')
    print(f'  source_timerange.start: {src.get("start", 0) / 1_000_000:.1f}s')
    print(f'  source_timerange.duration: {src.get("duration", 0) / 1_000_000:.1f}s')

    # Check if there are ANY other timing-related fields
    timing_fields = ['render_index', 'track_render_index', 'target_timerange', 'source_timerange']
    other_fields = [k for k in seg.keys() if 'time' in k.lower() or 'index' in k.lower() or 'render' in k.lower()]
    if set(other_fields) != set(timing_fields):
        print(f'  ⚠️  OTHER TIMING FIELDS: {set(other_fields) - set(timing_fields)}')

print('\n\n' + '='*60)
print('DIAGNOSIS:')
print('='*60)

# Check for gaps
gap_count = 0
for i in range(1, min(15, len(segments))):
    prev_end = segments[i-1]['target_timerange']['start'] + segments[i-1]['target_timerange']['duration']
    curr_start = segments[i]['target_timerange']['start']
    gap = (curr_start - prev_end) / 1_000_000

    if gap > 1.0:
        gap_count += 1
        print(f'✅ GAP found between segment {i-1} and {i}: {gap:.1f}s')

if gap_count == 0:
    print('❌ NO GAPS FOUND in target_timerange values!')
    print('\nPossible causes:')
    print('1. Code is not actually running (wrong file being modified)')
    print('2. CapCut is loading a cached version')
    print('3. Another field is overriding the timeline positions')
else:
    print(f'\n✅ Gaps ARE present in the JSON ({gap_count} found)')
    print('\nBut CapCut is not displaying them!')
    print('\nPossible causes:')
    print('1. CapCut requires the project to be closed before loading changes')
    print('2. track_render_index might need to be updated')
    print('3. There might be a CapCut cache that needs clearing')
    print('4. The "free_render_index_mode_on" flag might be affecting this')

print('\nChecking free_render_index_mode_on flag...')
print(f'  free_render_index_mode_on = {data.get("free_render_index_mode_on")}')

print('\n' + '='*60)
input('\nPress Enter to exit...')
