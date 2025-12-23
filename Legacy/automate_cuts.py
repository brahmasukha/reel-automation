import json
import copy
import uuid
import shutil
import os
import time

# Configuration
INPUT_FILE = '/Users/pro/Movies/CapCut/User Data/Projects/com.lveditor.draft/1221 (1)/draft_info.json'

import json
import copy
import uuid
import shutil
import os
import time

# Configuration
# Path is now read from cuts.txt
CUTS_FILE = os.path.join(os.path.dirname(__file__), 'cuts.txt')

GAP_BETWEEN_REELS_SECONDS = 10

def parse_cuts_file(file_path):
    """
    Parses a text file with the format:
    PATH: /path/to/draft_info.json
    
    00:18:06.0  00:18:25.0
    00:18:25.0  00:18:41.8
    
    00:21:20.0  00:21:28.0
    
    Returns: (input_file_path, reels_list)
    """
    reels = []
    current_reel_cuts = []
    input_file_path = None
    
    if not os.path.exists(file_path):
        print(f"Error: Cuts file not found at {file_path}")
        return None, []

    print(f"Reading configuration from {file_path}...")
    with open(file_path, 'r') as f:
        # Read lines without stripping strictly yet, to preserve empty lines
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        
        # 1. Handle Path Config
        if stripped.upper().startswith("PATH:"):
            input_file_path = stripped[5:].strip()
            input_file_path = input_file_path.strip('"').strip("'")
            print(f"Target Project: {input_file_path}")
            continue

        # 2. Handle Empty Lines (Reel Separators)
        if not stripped:
            if current_reel_cuts:
                reels.append(current_reel_cuts)
                current_reel_cuts = []
            continue
            
        # 3. Handle Timestamps (Start End)
        parts = stripped.split()
        if len(parts) >= 2:
            start_str = parts[0]
            end_str = parts[1]
            
            # Basic validation: check if looks like timestamp
            if any(c.isdigit() for c in start_str) and any(c.isdigit() for c in end_str):
                current_reel_cuts.append((start_str, end_str))
        
        # Legacy support for single timestamp per line? 
        # The user's new request is strictly "Start End" on one line.
        # We will prioritize the new format.

    # Append the last reel if exists
    if current_reel_cuts:
        reels.append(current_reel_cuts)
        
    return input_file_path, reels

def time_str_to_us(time_str):
    """Converts a time string to microseconds. Supports HH:MM:SS.ms and MM.SS"""
    # 1. Handle standard colon format (HH:MM:SS.ms or MM:SS)
    if ':' in time_str:
        parts = list(map(float, time_str.split(':')))
        if len(parts) == 3:
            hours, minutes, seconds = parts
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = parts
        else:
            # Fallback
            hours = 0
            minutes = 0
            seconds = parts[0]
            
    # 2. Handle legacy dot format (MM.SS) like '1.20'
    else:
        # Assume MM.SS if it looks like a float/decimal
        try:
             # Replace dot with colon to reuse logic or manually parse
             # But '1.20' -> 1 min 20 sec usually. '1.5' -> 1 min 50 sec? Or 1.5 min?
             # User content implies '1.20' was 1m 20s.
             parts = list(map(float, time_str.replace('.', ':').split(':')))
             if len(parts) == 2:
                 hours = 0
                 minutes, seconds = parts
             else:
                 # Just seconds?
                 hours = 0
                 minutes = 0
                 seconds = float(time_str)
        except ValueError:
             raise ValueError(f"Invalid time format: {time_str}")

    total_seconds = hours * 3600 + minutes * 60 + seconds
    return int(total_seconds * 1000000)

def main():
    # Parse the text file to get Path and Cuts
    INPUT_FILE, REELS = parse_cuts_file(CUTS_FILE)
    
    if not INPUT_FILE:
        print("Error: No 'PATH:' found in cuts.txt. Please add 'PATH: /path/to/draft_info.json' at the top.")
        return
        
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Project file not found at {INPUT_FILE}")
        return
        
    if not REELS:
        print("No cuts found to process.")
        return

    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    # Find the main video track
    tracks = data.get('tracks', [])
    video_track = None
    for track in tracks:
        if track.get('type') == 'video':
            video_track = track
            break
            
    if not video_track:
        print("Error: No video track found.")
        return

    # Assuming the first segment is the one we want to chop up
    # We will use it as a template for our new segments
    original_segments = video_track.get('segments', [])
    if not original_segments:
        print("Error: No segments found in video track.")
        return
        
    template_segment = original_segments[0]
    
    # Clear existing segments
    new_segments = []
    
    current_timeline_pos = 0
    reel_gap_us = int(GAP_BETWEEN_REELS_SECONDS * 1000000)
    
    print("Processing Reels...")
    for reel_idx, cuts in enumerate(REELS):
        print(f"  Building Reel {reel_idx + 1} with {len(cuts)} cuts...")
        
        for cut_idx, (start_str, end_str) in enumerate(cuts):
            try:
                start_us = time_str_to_us(start_str)
                end_us = time_str_to_us(end_str)
            except ValueError as e:
                print(f"    Error parsing time in Reel {reel_idx+1}, Cut {cut_idx+1}: {e}")
                continue

            duration_us = end_us - start_us
            
            if duration_us <= 0:
                print(f"    Warning: Cut {cut_idx+1} ({start_str}-{end_str}) has invalid duration. Skipping.")
                continue
                
            print(f"    - Adding segment: {start_str} -> {end_str} ({duration_us/1000000}s)")
            
            # Create new segment
            segment = copy.deepcopy(template_segment)
            
            # Generate a unique ID for the new segment to prevent merging
            segment['id'] = str(uuid.uuid4()).upper()
            
            # Update source range (which part of the original video to play)
            segment['source_timerange'] = {
                "start": start_us,
                "duration": duration_us
            }
            
            # Update target range (where to place it on the timeline)
            segment['target_timerange'] = {
                "start": current_timeline_pos,
                "duration": duration_us
            }
            
            new_segments.append(segment)
            
            # Advance timeline position (seamlessly within a reel)
            current_timeline_pos += duration_us
            
        # After finishing a Reel, add the gap
        print(f"  > Reel {reel_idx + 1} complete. Adding {GAP_BETWEEN_REELS_SECONDS}s gap.")
        current_timeline_pos += reel_gap_us

    # Update the track with new segments
    video_track['segments'] = new_segments
    
    # Update total duration (remove the last trailing gap for accuracy)
    data['duration'] = current_timeline_pos - reel_gap_us

    # --- Backup and Save Logic ---
    
    # Create valid backup path in the same directory
    input_dir = os.path.dirname(INPUT_FILE)
    backup_filename = f"draft_info_BACKUP_{int(time.time())}.json"
    backup_path = os.path.join(input_dir, backup_filename)
    
    print(f"Creating backup at: {backup_path}")
    shutil.copy2(INPUT_FILE, backup_path)
    
    print(f"Overwriting original file: {INPUT_FILE}")
    with open(INPUT_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
    print("Done! You can now open CapCut.")

if __name__ == "__main__":
    main()
