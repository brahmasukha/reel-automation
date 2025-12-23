import whisper
import sys
import os
import datetime

# Add local directory to PATH so whisper can find our local ffmpeg
os.environ["PATH"] += os.pathsep + os.getcwd()

def transcribe_video(video_path):
    print(f"Loading Whisper model... (This may take a moment)")
    model = whisper.load_model("base")
    
    print(f"Transcribing {video_path}...")
    result = model.transcribe(video_path)
    
    # Save as readable text with timestamps
    output_path = video_path + ".transcript.txt"
    
    with open(output_path, "w") as f:
        f.write(f"Transcription for: {os.path.basename(video_path)}\n")
        f.write("-" * 50 + "\n\n")
        
        for segment in result["segments"]:
            start = str(datetime.timedelta(seconds=int(segment["start"])))
            end = str(datetime.timedelta(seconds=int(segment["end"])))
            text = segment["text"].strip()
            f.write(f"[{start} -> {end}] {text}\n")
            
    print(f"Transcription saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe.py <video_file>")
        sys.exit(1)
        
    video_file = sys.argv[1]
    if not os.path.exists(video_file):
        print(f"Error: File {video_file} not found.")
        sys.exit(1)
        
    transcribe_video(video_file)
