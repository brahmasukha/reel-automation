"""
GUI Application for Reel Automation
User-friendly interface for processing videos into reels
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
from pipeline import ReelAutomationPipeline
import config


class ReelAutomationGUI:
    """Main GUI application for Reel Automation"""

    def __init__(self, root):
        self.root = root
        self.root.title("Reel Automation - AI-Powered Video Editing")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Variables
        self.video_path = tk.StringVar()
        self.is_processing = False
        self.pipeline = None

        # Setup UI
        self._setup_ui()

        # Validate configuration on startup
        self._check_configuration()

    def _setup_ui(self):
        """Setup the user interface"""

        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="Reel Automation",
            font=("Arial", 20, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Turn long videos into viral reels automatically",
            font=("Arial", 10)
        )
        subtitle_label.pack()

        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Video selection section
        video_frame = ttk.LabelFrame(main_frame, text="Select Video", padding="10")
        video_frame.pack(fill=tk.X, pady=(0, 10))

        video_entry = ttk.Entry(video_frame, textvariable=self.video_path, width=60)
        video_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        browse_btn = ttk.Button(video_frame, text="Browse...", command=self._browse_video)
        browse_btn.pack(side=tk.LEFT)

        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.open_capcut_var = tk.BooleanVar(value=True)
        open_capcut_check = ttk.Checkbutton(
            options_frame,
            text="Open CapCut when complete",
            variable=self.open_capcut_var
        )
        open_capcut_check.pack(anchor=tk.W)

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.process_btn = ttk.Button(
            button_frame,
            text="Process Video",
            command=self._process_video,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_processing,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT)

        clear_log_btn = ttk.Button(
            button_frame,
            text="Clear Log",
            command=self._clear_log
        )
        clear_log_btn.pack(side=tk.RIGHT)

        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Progress bar
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(
            status_frame,
            text="Ready to process video",
            font=("Arial", 9)
        )
        self.status_label.pack(anchor=tk.W)

        # Log output
        log_label = ttk.Label(status_frame, text="Log:", font=("Arial", 9, "bold"))
        log_label.pack(anchor=tk.W, pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(
            status_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # Configuration info at bottom
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ai_provider = config.AI_PROVIDER.upper()
        if ai_provider == "OPENAI":
            model_name = config.OPENAI_MODEL
        elif ai_provider == "ANTHROPIC":
            model_name = config.ANTHROPIC_MODEL
        elif ai_provider == "GEMINI":
            model_name = config.GEMINI_MODEL
        else:
            model_name = "Unknown"
        info_text = f"AI Provider: {ai_provider} | Model: {model_name} | Whisper: {config.WHISPER_MODEL}"

        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 8),
            foreground="gray"
        )
        info_label.pack()

    def _check_configuration(self):
        """Check if configuration is valid"""
        errors = config.validate_config()

        if errors:
            self.log_message("ERROR: Configuration issues found:", "error")
            for error in errors:
                self.log_message(f"  - {error}", "error")
            self.log_message("\nPlease create a .env file based on .env.example", "error")
            self.log_message("Add your API keys and configure settings.", "error")
            self.process_btn.config(state=tk.DISABLED)
        else:
            self.log_message("Configuration validated successfully!", "success")

    def _browse_video(self):
        """Open file browser to select video"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=filetypes
        )

        if filename:
            self.video_path.set(filename)
            self.log_message(f"Selected video: {os.path.basename(filename)}", "info")

    def _process_video(self):
        """Start processing the video"""
        video_file = self.video_path.get()

        if not video_file:
            messagebox.showwarning("No Video", "Please select a video file first!")
            return

        if not os.path.exists(video_file):
            messagebox.showerror("File Not Found", f"Video file not found:\n{video_file}")
            return

        # Disable process button, enable cancel
        self.process_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.is_processing = True

        # Clear previous logs
        self._clear_log()
        self.log_message("="*60, "info")
        self.log_message("STARTING REEL AUTOMATION PIPELINE", "info")
        self.log_message("="*60, "info")

        # Run pipeline in separate thread
        thread = threading.Thread(target=self._run_pipeline, args=(video_file,))
        thread.daemon = True
        thread.start()

    def _run_pipeline(self, video_file):
        """Run the pipeline in a separate thread"""
        try:
            # Create pipeline with callbacks
            self.pipeline = ReelAutomationPipeline(
                progress_callback=self._update_progress,
                log_callback=self._log_callback
            )

            # Run the pipeline
            project_path = self.pipeline.run(
                video_file,
                open_capcut=self.open_capcut_var.get()
            )

            # Success
            self.root.after(0, self._processing_complete, project_path)

        except Exception as e:
            # Error
            self.root.after(0, self._processing_error, str(e))

    def _update_progress(self, percentage, status):
        """Update progress bar and status (called from pipeline)"""
        self.root.after(0, lambda: self.progress_var.set(percentage))
        self.root.after(0, lambda: self.status_label.config(text=status))

    def _log_callback(self, message):
        """Log callback from pipeline"""
        self.root.after(0, lambda: self.log_message(message, "info"))

    def _processing_complete(self, project_path):
        """Called when processing completes successfully"""
        self.log_message("="*60, "success")
        self.log_message("PROCESSING COMPLETE!", "success")
        self.log_message("="*60, "success")
        self.log_message(f"Project created at:\n{project_path}", "success")

        self.process_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.is_processing = False

        messagebox.showinfo(
            "Success!",
            "Video processed successfully!\n\nYour reels are ready in CapCut."
        )

    def _processing_error(self, error_msg):
        """Called when processing fails"""
        self.log_message("="*60, "error")
        self.log_message("PROCESSING FAILED", "error")
        self.log_message("="*60, "error")
        self.log_message(f"Error: {error_msg}", "error")

        self.process_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.is_processing = False
        self.progress_var.set(0)

        messagebox.showerror(
            "Processing Failed",
            f"An error occurred:\n\n{error_msg}\n\nCheck the log for details."
        )

    def _cancel_processing(self):
        """Cancel the current processing"""
        if messagebox.askyesno("Cancel Processing", "Are you sure you want to cancel?"):
            self.log_message("CANCELLED BY USER", "warning")
            self.process_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)
            self.is_processing = False
            self.progress_var.set(0)
            # Note: Actual cancellation of pipeline would require more sophisticated threading

    def log_message(self, message, level="info"):
        """Add a message to the log"""
        self.log_text.config(state=tk.NORMAL)

        # Add color tags
        if level == "error":
            tag = "error"
            self.log_text.tag_config(tag, foreground="red")
        elif level == "success":
            tag = "success"
            self.log_text.tag_config(tag, foreground="green")
        elif level == "warning":
            tag = "warning"
            self.log_text.tag_config(tag, foreground="orange")
        else:
            tag = "info"
            self.log_text.tag_config(tag, foreground="black")

        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        """Clear the log output"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)


def main():
    """Main entry point for the GUI application"""
    root = tk.Tk()

    # Set theme (use modern theme if available)
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass  # Fallback to default theme

    app = ReelAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
