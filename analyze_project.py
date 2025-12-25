"""
Analyze CapCut project to show reel boundaries clearly
"""
import json
import sys

def analyze_project(project_path):
    """Analyze CapCut project and display reel structure"""

    draft_content_path = f"{project_path}/draft_content.json"

    print(f"\n📊 Analyzing CapCut Project: {project_path}\n")
    print("=" * 80)

    # Read project file
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
    print(f"Total Segments: {len(segments)}\n")

    # Analyze gaps to detect reel boundaries
    GAP_THRESHOLD_US = 5_000_000  # 5 seconds in microseconds

    current_reel = 1
    reel_segments = []
    prev_end_time = 0

    for idx, segment in enumerate(segments):
        source_range = segment.get('source_timerange', {})
        target_range = segment.get('target_timerange', {})

        start_us = source_range.get('start', 0)
        duration_us = source_range.get('duration', 0)
        end_us = start_us + duration_us

        target_start_us = target_range.get('start', 0)

        # Check for gap (indicating new reel)
        if idx > 0:
            gap = target_start_us - prev_end_time
            if gap >= GAP_THRESHOLD_US:
                # New reel detected!
                print(f"\n🎬 REEL {current_reel} ({len(reel_segments)} segments)")
                print("-" * 80)
                for seg_idx, seg_info in enumerate(reel_segments, 1):
                    print(f"  Segment {seg_idx}: {seg_info['start_time']} → {seg_info['end_time']} "
                          f"(Duration: {seg_info['duration']:.1f}s)")

                total_duration = sum(s['duration'] for s in reel_segments)
                print(f"  ✅ Total Reel Duration: {total_duration:.1f}s")
                print(f"  🔹 Gap to next reel: {gap / 1_000_000:.1f}s")

                current_reel += 1
                reel_segments = []

        # Format timestamps
        start_sec = start_us / 1_000_000
        duration_sec = duration_us / 1_000_000
        end_sec = end_us / 1_000_000

        start_time = format_timestamp(start_sec)
        end_time = format_timestamp(end_sec)

        reel_segments.append({
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration_sec
        })

        prev_end_time = target_start_us + duration_us

    # Print last reel
    if reel_segments:
        print(f"\n🎬 REEL {current_reel} ({len(reel_segments)} segments)")
        print("-" * 80)
        for seg_idx, seg_info in enumerate(reel_segments, 1):
            print(f"  Segment {seg_idx}: {seg_info['start_time']} → {seg_info['end_time']} "
                  f"(Duration: {seg_info['duration']:.1f}s)")

        total_duration = sum(s['duration'] for s in reel_segments)
        print(f"  ✅ Total Reel Duration: {total_duration:.1f}s")

    print("\n" + "=" * 80)
    print(f"\n✅ Total Reels Detected: {current_reel}")
    print(f"✅ Total Video Segments: {len(segments)}")
    print(f"\n💡 Tip: Each gap of 5+ seconds indicates a new reel boundary\n")

def format_timestamp(seconds):
    """Convert seconds to MM:SS format"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        # Use latest project
        project_path = "C:/Users/kenya/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1223"

    analyze_project(project_path)
