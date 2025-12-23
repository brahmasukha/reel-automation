"""
CapCut Project Generator Module
Creates CapCut projects from scratch with video cuts applied
"""
import json
import os
import shutil
import uuid
import time
from typing import List, Tuple
import config


class CapCutProjectGenerator:
    """Generates CapCut project files from video and timestamp data"""

    def __init__(self):
        self.projects_root = config.CAPCUT_PROJECTS_ROOT
        self.gap_between_reels = config.GAP_BETWEEN_REELS_SECONDS * 1000000  # Convert to microseconds

    def find_latest_project(self):
        """Find the most recently modified CapCut project"""
        import glob

        if not os.path.exists(self.projects_root):
            return None

        subdirs = glob.glob(os.path.join(self.projects_root, '*'))
        valid_projects = []

        for d in subdirs:
            # Check for draft_content.json (new CapCut) or draft_info.json (old CapCut)
            if os.path.isdir(d) and (os.path.exists(os.path.join(d, 'draft_content.json')) or
                                     os.path.exists(os.path.join(d, 'draft_info.json'))):
                valid_projects.append(d)

        if not valid_projects:
            return None

        return max(valid_projects, key=os.path.getmtime)

    def modify_existing_project(self, project_path: str, reels: List[List[Tuple[str, str, str]]],
                               progress_callback=None) -> str:
        """
        Modify an existing CapCut project with new cuts (Legacy approach)

        Args:
            project_path: Path to the existing project folder
            reels: List of reels, each containing (start, end, comment) tuples
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the modified draft file
        """
        # Support both new CapCut (draft_content.json) and old CapCut (draft_info.json)
        draft_content_path = os.path.join(project_path, 'draft_content.json')
        draft_info_path = os.path.join(project_path, 'draft_info.json')

        if os.path.exists(draft_content_path):
            draft_file_path = draft_content_path
            file_name = 'draft_content.json'
        elif os.path.exists(draft_info_path):
            draft_file_path = draft_info_path
            file_name = 'draft_info.json'
        else:
            raise FileNotFoundError(f"No draft file found at: {project_path}\nLooked for: draft_content.json or draft_info.json")

        if progress_callback:
            progress_callback(f"Modifying existing project: {os.path.basename(project_path)}")
            progress_callback(f"Using file: {file_name}")
            progress_callback(f"Full path: {draft_file_path}")

        # Read existing project
        with open(draft_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Create backup
        backup_filename = file_name.replace('.json', f'_BACKUP_{int(time.time())}.json')
        backup_path = os.path.join(project_path, backup_filename)
        shutil.copy2(draft_file_path, backup_path)

        if progress_callback:
            progress_callback(f"Backup created at: {os.path.basename(backup_path)}")
            progress_callback("Applying cuts...")

        # Find video track
        tracks = data.get('tracks', [])
        video_track = None
        for track in tracks:
            if track.get('type') == 'video':
                video_track = track
                break

        if not video_track:
            raise ValueError("No video track found in project")

        # Get template segment
        original_segments = video_track.get('segments', [])
        if not original_segments:
            raise ValueError("No segments found in video track")

        template_segment = original_segments[0]
        
        if progress_callback:
            progress_callback(f"Found {len(original_segments)} original segments. Using first as template.")
            progress_callback(f"Processing {len(reels)} reels...")

        # Build new segments from reels
        new_segments = []
        current_timeline_pos = 0

        for reel_idx, reel in enumerate(reels):
            for cut_idx, (start_str, end_str, comment) in enumerate(reel):
                start_us = self._time_str_to_us(start_str)
                end_us = self._time_str_to_us(end_str)
                duration_us = end_us - start_us

                if duration_us <= 0:
                    continue

                # Create new segment from template
                import copy
                segment = copy.deepcopy(template_segment)

                # Update with new values
                segment['id'] = str(uuid.uuid4()).upper()
                segment['source_timerange'] = {
                    "start": start_us,
                    "duration": duration_us
                }
                segment['target_timerange'] = {
                    "start": current_timeline_pos,
                    "duration": duration_us
                }
                # segment['render_index'] = len(new_segments) # Removed to match legacy script

                new_segments.append(segment)
                current_timeline_pos += duration_us

            # Add gap between reels
            current_timeline_pos += self.gap_between_reels

        # Update track with new segments
        video_track['segments'] = new_segments

        # Update total duration (remove last gap)
        data['duration'] = current_timeline_pos - self.gap_between_reels

        # Save modified project
        with open(draft_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        if progress_callback:
            progress_callback(f"Project modified successfully! Added {len(new_segments)} segments.")
            progress_callback(f"Saved to: {draft_file_path}")

        return draft_file_path

    def create_project(self, video_path: str, reels: List[List[Tuple[str, str, str]]],
                      project_name: str = None, progress_callback=None, use_existing=True) -> str:
        """
        Create a new CapCut project with video and cuts applied

        Args:
            video_path: Path to the source video file
            reels: List of reels, each containing (start, end, comment) tuples
            project_name: Optional custom project name
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the created project's draft_info.json
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if progress_callback:
            progress_callback("Creating CapCut project structure...")

        # Generate project folder
        project_id = str(uuid.uuid4())
        project_folder = os.path.join(self.projects_root, project_id)
        os.makedirs(project_folder, exist_ok=True)

        # Copy video to project folder
        video_filename = os.path.basename(video_path)
        project_video_path = os.path.join(project_folder, video_filename)

        if progress_callback:
            progress_callback(f"Copying video to project folder...")

        shutil.copy2(video_path, project_video_path)

        # Get video duration (we'll use ffmpeg for this)
        video_duration_us = self._get_video_duration(video_path)

        if progress_callback:
            progress_callback("Generating project JSON with cuts...")

        # Generate draft_info.json
        draft_info = self._generate_draft_info(
            project_video_path,
            video_duration_us,
            reels,
            project_name or os.path.splitext(video_filename)[0]
        )

        # Save draft_info.json
        draft_info_path = os.path.join(project_folder, 'draft_info.json')
        with open(draft_info_path, 'w', encoding='utf-8') as f:
            json.dump(draft_info, f, indent=2)

        if progress_callback:
            progress_callback(f"CapCut project created successfully!")

        return draft_info_path

    def _get_video_duration(self, video_path: str) -> int:
        """Get video duration in microseconds using ffmpeg"""
        try:
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
                capture_output=True,
                text=True,
                check=True
            )
            duration_seconds = float(result.stdout.strip())
            return int(duration_seconds * 1000000)
        except Exception as e:
            print(f"Warning: Could not get video duration: {e}")
            # Return a default large duration
            return 3600 * 1000000  # 1 hour in microseconds

    def _time_str_to_us(self, time_str: str) -> int:
        """Convert time string to microseconds"""
        # Handle HH:MM:SS.ms or MM:SS format
        if ':' in time_str:
            parts = list(map(float, time_str.split(':')))
            if len(parts) == 3:
                hours, minutes, seconds = parts
            elif len(parts) == 2:
                hours = 0
                minutes, seconds = parts
            else:
                hours = 0
                minutes = 0
                seconds = parts[0]
        else:
            # Just seconds
            hours = 0
            minutes = 0
            seconds = float(time_str)

        total_seconds = hours * 3600 + minutes * 60 + seconds
        return int(total_seconds * 1000000)

    def _generate_draft_info(self, video_path: str, video_duration_us: int,
                            reels: List[List[Tuple[str, str, str]]], project_name: str) -> dict:
        """
        Generate CapCut draft_info.json structure

        This creates a minimal but valid CapCut project structure
        """
        video_id = str(uuid.uuid4()).upper()
        material_id = str(uuid.uuid4()).upper()

        # Build video segments from reels
        segments = []
        current_timeline_pos = 0

        for reel_idx, reel in enumerate(reels):
            for cut_idx, (start_str, end_str, comment) in enumerate(reel):
                start_us = self._time_str_to_us(start_str)
                end_us = self._time_str_to_us(end_str)
                duration_us = end_us - start_us

                if duration_us <= 0:
                    continue

                # Create segment
                segment_id = str(uuid.uuid4()).upper()
                segment = {
                    "id": segment_id,
                    "category_id": "",
                    "category_name": "video",
                    "check_flag": 1,
                    "clip": {
                        "alpha": 1.0,
                        "flip": {"horizontal": False, "vertical": False},
                        "rotation": 0.0,
                        "scale": {"x": 1.0, "y": 1.0},
                        "transform": {"x": 0.0, "y": 0.0}
                    },
                    "common_keyframes": [],
                    "enable_adjust": True,
                    "enable_color_curves": True,
                    "enable_color_match_adjust": False,
                    "enable_color_wheels": True,
                    "enable_lut": True,
                    "enable_smart_color_adjust": False,
                    "extra_material_refs": [],
                    "group_id": "",
                    "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000},
                    "is_placeholder": False,
                    "is_tone_modify": False,
                    "keyframe_refs": [],
                    "last_nonzero_volume": 1.0,
                    "material_id": material_id,
                    "render_index": len(segments),
                    "reverse": False,
                    "source_timerange": {
                        "duration": duration_us,
                        "start": start_us
                    },
                    "speed": 1.0,
                    "target_timerange": {
                        "duration": duration_us,
                        "start": current_timeline_pos
                    },
                    "template_id": "",
                    "template_scene": "default",
                    "track_attribute": 0,
                    "track_render_index": 0,
                    "uniform_scale": {
                        "on": True,
                        "value": 1.0
                    },
                    "visible": True,
                    "volume": 1.0
                }
                segments.append(segment)
                current_timeline_pos += duration_us

            # Add gap between reels
            current_timeline_pos += self.gap_between_reels

        # Calculate total duration (remove last gap)
        total_duration = current_timeline_pos - self.gap_between_reels if segments else 0

        # Build the complete draft_info structure
        draft_info = {
            "version": "7.7.0",
            "id": str(uuid.uuid4()).upper(),
            "type": "draft",
            "platform": "windows",
            "create_time": int(time.time()),
            "duration": total_duration,
            "name": project_name,
            "materials": {
                "videos": [{
                    "id": material_id,
                    "path": video_path.replace('\\', '/'),
                    "type": "video",
                    "duration": video_duration_us,
                    "width": 1920,
                    "height": 1080,
                    "create_time": int(time.time())
                }],
                "audios": [],
                "images": [],
                "texts": []
            },
            "tracks": [
                {
                    "id": str(uuid.uuid4()).upper(),
                    "type": "video",
                    "segments": segments
                },
                {
                    "id": str(uuid.uuid4()).upper(),
                    "type": "audio",
                    "segments": []
                }
            ],
            "canvasConfig": {
                "width": 1080,
                "height": 1920,
                "ratio": "9:16"
            }
        }

        return draft_info


def test_project_generator():
    """Test the project generator"""
    # This is just a structure test - won't actually run without a real video
    generator = CapCutProjectGenerator()

    sample_reels = [
        [("00:00:05", "00:00:15", "HOOK"), ("00:00:15", "00:00:30", "CONTEXT")],
        [("00:01:00", "00:01:10", "HOOK"), ("00:01:10", "00:01:40", "PAYOFF")]
    ]

    print("CapCut Project Generator initialized successfully!")
    print(f"Projects will be created in: {generator.projects_root}")


if __name__ == "__main__":
    test_project_generator()
