import os
import queue
import re
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

try:
    import imageio_ffmpeg
    def get_ffmpeg():
        return imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    def get_ffmpeg():
        return "ffmpeg"

# ── constants ─────────────────────────────────────────────────────────────────

FRAME_PATTERN = re.compile(r"^(\d{3,})\.(png|jpg|jpeg)$", re.IGNORECASE)
FPS_OPTIONS = ["12", "24", "25", "30", "60"]
DEFAULT_FPS = "24"
POLL_MS = 100

# ── frame detection ───────────────────────────────────────────────────────────

def detect_frames(folder):
    matches = []
    for name in os.listdir(folder):
        m = FRAME_PATTERN.match(name)
        if m:
            matches.append((int(m.group(1)), len(m.group(1)), m.group(2).lower()))

    if not matches:
        raise ValueError("No frames detected in this folder")

    matches.sort(key=lambda x: x[0])
    first_num, digit_count, ext = matches[0]
    last_num = matches[-1][0]
    total = len(matches)

    pattern = f"%0{digit_count}d.{ext}"
    expected = last_num - first_num + 1
    warning = f"  ⚠ {expected - total} missing" if total != expected else ""
    label = (
        f"Frames {first_num:0{digit_count}d}–{last_num:0{digit_count}d}"
        f"  ({total} frames, {pattern}){warning}"
    )
    return pattern, first_num, total, label

# ── compilation ───────────────────────────────────────────────────────────────

def compile_video(folder, pattern, start, total, fps, output_path, progress_q):
    ffmpeg = get_ffmpeg()
    cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-start_number", str(start),
        "-i", os.path.join(folder, pattern),
        "-frames:v", str(total),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "slow",
        output_path,
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        frame_re = re.compile(r"frame=\s*(\d+)")
        for line in proc.stdout:
            m = frame_re.search(line)
            if m:
                progress_q.put(("progress", int(m.group(1))))
        proc.wait()
        if proc.returncode == 0:
            progress_q.put(("done", None))
        else:
            progress_q.put(("error", f"ffmpeg exited with code {proc.returncode}"))
    except Exception as exc:
        progress_q.put(("error", str(exc)))

# ── application ───────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Frame Compiler")
        self.geometry("580x390")
        self.resizable(False, False)

        self._frame_info = None
        self._output_path = tk.StringVar()
        self._input_path = tk.StringVar()
        self._fps_var = tk.StringVar(value=DEFAULT_FPS)
        self._progress_q = queue.Queue()

        self._build_ui()
        self._update_compile_btn()
        self.lift()
        self.after(100, self._activate)

    def _activate(self):
        try:
            subprocess.run(
                ["osascript", "-e",
                 f'tell application "System Events" to set frontmost of every process whose unix id is {os.getpid()} to true'],
                capture_output=True,
            )
        except Exception:
            pass

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Input folder
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=0, column=0, padx=14, pady=(14, 6), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(input_frame, text="Input Folder", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )
        self._input_entry = ctk.CTkEntry(
            input_frame, textvariable=self._input_path, placeholder_text="Select a folder…"
        )
        self._input_entry.grid(row=1, column=0, padx=(12, 6), pady=(0, 4), sticky="ew")
        ctk.CTkButton(input_frame, text="Browse…", width=90, command=self._browse_input).grid(
            row=1, column=1, padx=(0, 12), pady=(0, 4)
        )
        self._detect_label = ctk.CTkLabel(
            input_frame, text="No folder selected", text_color="gray", anchor="w"
        )
        self._detect_label.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="w")

        # Settings
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, padx=14, pady=6, sticky="ew")

        ctk.CTkLabel(settings_frame, text="Settings", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        fps_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        fps_row.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")
        ctk.CTkLabel(fps_row, text="Frame Rate (fps):").pack(side="left")
        ctk.CTkOptionMenu(fps_row, variable=self._fps_var, values=FPS_OPTIONS, width=80).pack(
            side="left", padx=(10, 0)
        )

        # Output file
        output_frame = ctk.CTkFrame(self)
        output_frame.grid(row=2, column=0, padx=14, pady=6, sticky="ew")
        output_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(output_frame, text="Output File", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )
        ctk.CTkEntry(output_frame, textvariable=self._output_path, placeholder_text="Choose save location…").grid(
            row=1, column=0, padx=(12, 6), pady=(0, 10), sticky="ew"
        )
        ctk.CTkButton(output_frame, text="Save As…", width=90, command=self._browse_output).grid(
            row=1, column=1, padx=(0, 12), pady=(0, 10)
        )

        # Action buttons
        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.grid(row=3, column=0, padx=14, pady=4, sticky="ew")
        action_row.grid_columnconfigure(0, weight=1)

        self._compile_btn = ctk.CTkButton(
            action_row, text="Compile Video", command=self._start_compile, state="disabled"
        )
        self._compile_btn.grid(row=0, column=0, sticky="w")

        self._open_btn = ctk.CTkButton(
            action_row, text="Open Output", command=self._open_output,
            state="disabled", fg_color="gray", hover_color="#555555"
        )
        self._open_btn.grid(row=0, column=1, sticky="e")

        # Progress
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.grid(row=4, column=0, padx=14, pady=(4, 14), sticky="ew")
        prog_frame.grid_columnconfigure(0, weight=1)

        self._progress = ctk.CTkProgressBar(prog_frame)
        self._progress.set(0)
        self._progress.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self._status_label = ctk.CTkLabel(prog_frame, text="Ready", text_color="gray", anchor="w")
        self._status_label.grid(row=1, column=0, sticky="w")

    # ── browse ────────────────────────────────────────────────────────────────

    def _browse_input(self):
        folder = filedialog.askdirectory(title="Select frames folder")
        if not folder:
            return
        self._input_path.set(folder)
        self._run_detect(folder)
        self._update_compile_btn()

    def _browse_output(self):
        folder = self._input_path.get()
        initial_name = os.path.basename(folder) + ".mp4" if folder else "output.mp4"
        clips_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "clips",
        )
        initial_dir = clips_dir if os.path.isdir(clips_dir) else os.path.expanduser("~")
        path = filedialog.asksaveasfilename(
            title="Save output video",
            initialdir=initial_dir,
            initialfile=initial_name,
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4"), ("All files", "*.*")],
        )
        if path:
            self._output_path.set(path)
            self._update_compile_btn()

    # ── detection ─────────────────────────────────────────────────────────────

    def _run_detect(self, folder):
        try:
            pattern, start, total, label = detect_frames(folder)
            self._frame_info = (pattern, start, total)
            self._detect_label.configure(text=label, text_color="black")
        except ValueError as e:
            self._frame_info = None
            self._detect_label.configure(text=str(e), text_color="red")

    # ── compile ───────────────────────────────────────────────────────────────

    def _update_compile_btn(self):
        state = "normal" if (self._frame_info and self._output_path.get()) else "disabled"
        self._compile_btn.configure(state=state)

    def _start_compile(self):
        if not self._frame_info:
            return
        pattern, start, total = self._frame_info
        self._compile_btn.configure(state="disabled")
        self._open_btn.configure(state="disabled")
        self._progress.set(0)
        self._status_label.configure(text="Starting…", text_color="black")

        thread = threading.Thread(
            target=compile_video,
            args=(
                self._input_path.get(), pattern, start, total,
                self._fps_var.get(), self._output_path.get(), self._progress_q,
            ),
            daemon=True,
        )
        thread.start()
        self.after(POLL_MS, self._poll_progress)

    def _poll_progress(self):
        try:
            while True:
                kind, value = self._progress_q.get_nowait()
                if kind == "progress":
                    total = self._frame_info[2] if self._frame_info else 1
                    self._progress.set(value / total if total else 0)
                    pct = int(value / total * 100) if total else 0
                    self._status_label.configure(
                        text=f"Encoding frame {value} of {total}…  ({pct}%)",
                        text_color="black",
                    )
                elif kind == "done":
                    self._progress.set(1)
                    self._status_label.configure(text="Done.", text_color="green")
                    self._compile_btn.configure(state="normal")
                    self._open_btn.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
                    return
                elif kind == "error":
                    self._status_label.configure(text=f"Error: {value}", text_color="red")
                    self._compile_btn.configure(state="normal")
                    return
        except queue.Empty:
            pass
        self.after(POLL_MS, self._poll_progress)

    # ── preview ───────────────────────────────────────────────────────────────

    def _open_output(self):
        path = self._output_path.get()
        if not path or not os.path.isfile(path):
            return
        subprocess.run(["open", path])

# ── entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
