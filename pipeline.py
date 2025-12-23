"""
Main Pipeline Orchestrator
Chains all steps: Transcription -> AI Analysis -> Project Generation -> CapCut Launch
"""
import os
import sys
import subprocess
import datetime
import config

# Conditional imports based on transcription method
if config.TRANSCRIPTION_METHOD == 'local':
    import whisper
elif config.TRANSCRIPTION_METHOD == 'online':
    from online_transcription import OnlineTranscriber

from ai_timestamp_generator import AITimestampGenerator
from capcut_project_generator import CapCutProjectGenerator


class ReelAutomationPipeline:
    """Main pipeline that orchestrates the entire reel automation process"""

    def __init__(self, progress_callback=None, log_callback=None):
        """
        Initialize the pipeline

        Args:
            progress_callback: Function to call with progress updates (percentage)
            log_callback: Function to call with log messages
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.whisper_model = None
        self.online_transcriber = None
        self.ai_generator = None
        self.project_generator = None

    def log(self, message: str):
        """Log a message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def update_progress(self, percentage: int, status: str):
        """Update progress"""
        self.log(status)
        if self.progress_callback:
            self.progress_callback(percentage, status)

    def run(self, video_path: str, open_capcut: bool = True) -> str:
        """
        Run the complete pipeline

        Args:
            video_path: Path to the input video file
            open_capcut: Whether to open CapCut at the end

        Returns:
            Path to the created CapCut project
        """
        try:
            # Validate input
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")

            self.update_progress(0, "Starting reel automation pipeline...")

            # Step 1: Transcribe video
            if config.TRANSCRIPTION_METHOD == 'local':
                self.update_progress(10, "Step 1/4: Transcribing video with Whisper (local)...")
            else:
                self.update_progress(10, f"Step 1/4: Transcribing video with {config.AI_PROVIDER.upper()} API (online)...")

            transcript_text = self._transcribe_video(video_path)
            self.update_progress(30, "Transcription complete!")

            # Step 2: Generate timestamps with AI
            self.update_progress(35, "Step 2/4: Analyzing transcript with AI...")
            reels = self._generate_timestamps(transcript_text)
            self.update_progress(60, f"AI generated {len(reels)} reels!")

            # Step 3: Create CapCut project
            self.update_progress(65, "Step 3/4: Creating CapCut project...")
            project_path = self._create_capcut_project(video_path, reels)
            self.update_progress(90, "CapCut project created successfully!")

            # Step 4: Open CapCut
            if open_capcut:
                self.update_progress(95, "Step 4/4: Launching CapCut...")
                self._launch_capcut()
                self.update_progress(100, "Complete! CapCut is opening...")
            else:
                self.update_progress(100, "Complete! Project ready.")

            return project_path

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            raise

    def _transcribe_video(self, video_path: str) -> str:
        """
        Transcribe video using either local Whisper or online AI API

        Returns:
            Formatted transcript string with timestamps
        """
        if config.TRANSCRIPTION_METHOD == 'online':
            # Use online transcription
            return self._transcribe_video_online(video_path)
        else:
            # Use local Whisper
            return self._transcribe_video_local(video_path)

    def _transcribe_video_local(self, video_path: str) -> str:
        """
        Transcribe video using local Whisper

        Returns:
            Formatted transcript string with timestamps
        """
        # Check if transcript already exists
        transcript_path = video_path + ".transcript.txt"
        if os.path.exists(transcript_path):
            self.log(f"Found existing transcript: {transcript_path}")
            self.log("Reusing saved transcript (skipping Whisper transcription)")
            with open(transcript_path, "r", encoding="utf-8") as f:
                return f.read()

        self.log(f"Loading Whisper model '{config.WHISPER_MODEL}'...")

        # Add ffmpeg to PATH if it exists in current directory
        local_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg.exe')
        if os.path.exists(local_ffmpeg):
            os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ.get("PATH", "")

        # Load Whisper model (cache it for reuse)
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model(config.WHISPER_MODEL)

        self.log(f"Transcribing: {os.path.basename(video_path)}")
        result = self.whisper_model.transcribe(video_path)

        # Format transcript with timestamps
        transcript_lines = []
        transcript_lines.append(f"Transcription for: {os.path.basename(video_path)}")
        transcript_lines.append("-" * 50)
        transcript_lines.append("")

        for segment in result["segments"]:
            start = str(datetime.timedelta(seconds=int(segment["start"])))
            end = str(datetime.timedelta(seconds=int(segment["end"])))
            text = segment["text"].strip()
            transcript_lines.append(f"[{start} -> {end}] {text}")

        transcript_text = "\n".join(transcript_lines)

        # Save transcript to file
        transcript_path = video_path + ".transcript.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        self.log(f"Transcript saved to: {transcript_path}")

        return transcript_text

    def _transcribe_video_online(self, video_path: str) -> str:
        """
        Transcribe video using online AI API

        Returns:
            Formatted transcript string with timestamps
        """
        # Check if transcript already exists
        transcript_path = video_path + ".transcript.txt"
        if os.path.exists(transcript_path):
            self.log(f"Found existing transcript: {transcript_path}")
            self.log("Reusing saved transcript (skipping online transcription)")
            with open(transcript_path, "r", encoding="utf-8") as f:
                return f.read()

        # Initialize online transcriber (cache it for reuse)
        if self.online_transcriber is None:
            self.online_transcriber = OnlineTranscriber(log_callback=self.log_callback)

        # Transcribe using AI API
        transcript_text = self.online_transcriber.transcribe(video_path)

        # Save transcript to file
        transcript_path = video_path + ".transcript.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        self.log(f"Transcript saved to: {transcript_path}")

        return transcript_text

    def _generate_timestamps(self, transcript: str) -> list:
        """
        Generate reel timestamps using AI

        Returns:
            List of reels with timestamp data
        """
        if self.ai_generator is None:
            self.ai_generator = AITimestampGenerator()

        def ai_progress(msg):
            self.log(msg)

        reels = self.ai_generator.generate_timestamps(transcript, progress_callback=ai_progress)

        # Log the generated reels
        self.log("\n" + "="*50)
        self.log("GENERATED REELS:")
        self.log("="*50)
        for idx, reel in enumerate(reels, 1):
            total_duration = 0
            self.log(f"\nReel {idx}:")
            for start_str, end_str, comment in reel:
                # Calculate duration for this segment
                start_us = self._time_str_to_seconds(start_str)
                end_us = self._time_str_to_seconds(end_str)
                duration = end_us - start_us
                total_duration += duration
                comment_str = f" ({comment})" if comment else ""
                self.log(f"  {start_str} -> {end_str}{comment_str}")
            self.log(f"  Total Duration: {total_duration:.1f}s")

        self.log("="*50 + "\n")

        return reels

    def _time_str_to_seconds(self, time_str: str) -> float:
        """Convert time string to seconds (for logging purposes)"""
        if ':' in time_str:
            parts = list(map(float, time_str.split(':')))
            if len(parts) == 3:
                hours, minutes, seconds = parts
            elif len(parts) == 2:
                hours = 0
                minutes, seconds = parts
            else:
                return float(parts[0])
            return hours * 3600 + minutes * 60 + seconds
        else:
            return float(time_str)

    def _create_capcut_project(self, video_path: str, reels: list) -> str:
        """
        Create CapCut project with cuts applied
        
        Returns:
            Path to draft_info.json
        """
        if self.project_generator is None:
            self.project_generator = CapCutProjectGenerator()

        def project_progress(msg):
            self.log(msg)

        # video_name = os.path.splitext(os.path.basename(video_path))[0]
        # project_name = f"{video_name}_Reels_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # --- LEGACY WORKFLOW START ---
        self.log("\n" + "="*60)
        self.log("MANUAL STEP REQUIRED")
        self.log("="*60)
        self.log("1. Open CapCut manually.")
        self.log("2. Create a NEW project.")
        self.log("3. Import the video you want to process.")
        self.log("4. Drag the video to the timeline.")
        self.log("5. Close the project (go back to homepage) to ensure it saves.")
        self.log("="*60)
        
        input("\nPress Enter after you have created and closed the project...")
        
        self.log("Looking for the latest project...")
        latest_project = self.project_generator.find_latest_project()
        
        if not latest_project:
            raise FileNotFoundError("Could not find any CapCut projects. Please make sure you created one.")
            
        self.log(f"Found latest project: {latest_project}")
        
        project_path = self.project_generator.modify_existing_project(
            latest_project,
            reels,
            progress_callback=project_progress
        )
        # --- LEGACY WORKFLOW END ---

        # DISABLED AUTOMATED CREATION
        # project_path = self.project_generator.create_project(
        #     video_path,
        #     reels,
        #     project_name=project_name,
        #     progress_callback=project_progress
        # )

        self.log(f"Project modified at: {project_path}")

        return project_path

    def _launch_capcut(self):
        """Launch CapCut application"""
        capcut_exe = config.get_capcut_executable()

        if not capcut_exe:
            self.log("WARNING: CapCut executable not found!")
            self.log("Please open CapCut manually and load the latest project.")
            self.log("\nSearched locations:")
            for path in config.CAPCUT_EXE_PATHS:
                self.log(f"  - {path}")
            return

        self.log(f"Launching CapCut from: {capcut_exe}")

        try:
            # Check if running on WSL (Windows Subsystem for Linux)
            is_wsl = 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False

            if is_wsl:
                # On WSL, use cmd.exe to launch Windows applications
                # Convert WSL path to Windows path if needed
                if capcut_exe.startswith('/mnt/'):
                    # Convert /mnt/c/... to C:\...
                    parts = capcut_exe.split('/')
                    drive = parts[2].upper()
                    path_parts = parts[3:]
                    windows_path = f"{drive}:\\" + "\\".join(path_parts)
                else:
                    windows_path = capcut_exe

                self.log(f"Running on WSL, launching with cmd.exe: {windows_path}")
                subprocess.Popen(['cmd.exe', '/c', 'start', '', windows_path],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            else:
                # On native Windows
                subprocess.Popen([capcut_exe],
                               creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)

            self.log("CapCut launched successfully!")
            self.log("")
            self.log("=" * 60)
            self.log("IMPORTANT: To see your new project in CapCut:")
            self.log("1. Close CapCut completely (including system tray)")
            self.log("2. Reopen CapCut")
            self.log("3. Your project should now appear in the projects list")
            self.log("=" * 60)
        except Exception as e:
            self.log(f"Error launching CapCut: {e}")
            self.log("Please open CapCut manually.")


def main():
    """Command-line interface for the pipeline"""
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]

    # Validate configuration
    errors = config.validate_config()
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease create a .env file based on .env.example")
        sys.exit(1)

    # Run pipeline
    pipeline = ReelAutomationPipeline()

    print("="*60)
    print("REEL AUTOMATION PIPELINE")
    print("="*60)

    try:
        project_path = pipeline.run(video_file)
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"Project created: {project_path}")
        print("\nYou can now open CapCut and find your project with reels ready!")

    except Exception as e:
        print("\n" + "="*60)
        print("PIPELINE FAILED")
        print("="*60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
