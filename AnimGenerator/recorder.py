import os
import imageio
import numpy as np
import datetime
import threading
import time
import subprocess

class Recorder:
    def __init__(self, width, height, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_count = 0
        self.frames_dir = 'frames'
        self.ensure_directory(self.frames_dir)

    def ensure_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def capture_frame(self, image):
        frame_path = os.path.join(self.frames_dir, f'frame_{self.frame_count:06d}.png')
        imageio.imwrite(frame_path, image)
        print(f"Saved frame {self.frame_count}")
        self.frame_count += 1

    def finalize_video(self):
        if self.frame_count == 0:
            print("No frames were captured. Cannot create video.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"output_{timestamp}.mp4"

        # Use ffmpeg to combine frames into a video
        ffmpeg_command = [
            'ffmpeg',
            '-framerate', str(self.fps),
            '-i', os.path.join(self.frames_dir, 'frame_%06d.png'),
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-vf', f'fps={self.fps},scale={self.width}:{self.height}',
            '-pix_fmt', 'yuv420p',
            output_filename
        ]

        print(f"Running ffmpeg command: {' '.join(ffmpeg_command)}")

        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"Video saved as {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating video: {e}")

        # Optionally, clean up frame images
        for file in os.listdir(self.frames_dir):
            os.remove(os.path.join(self.frames_dir, file))
        os.rmdir(self.frames_dir)
