import glfw
import numpy as np
from render import Renderer
from genesis import Genesis
import signal
import sys
import traceback


fps = 30
width = 2880
height = 1800
record = False

renderer = None

def signal_handler(sig, frame):
    print("\nInterrupt received, stopping gracefully...")
    global renderer
    if renderer:
        renderer.cleanup()
    sys.exit(0)

def main():
    global renderer
    renderer = Renderer(width, height, record=record, fps=fps)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        renderer.initialize()
        if not renderer.initialized:
            print("Renderer initialization failed. Exiting.")
            return

        # Main render loop
        frame_count = 0
        max_frames = 300 if record else float('inf')  # Only limit frames if recording

        while not renderer.should_close():
            print("Starting Frame Loop.")
            renderer.render(1.0 / fps)  # Pass the frame time

            # Handle recording
            if record:
                frame_count += 1
                progress = (frame_count / max_frames) * 100
                print(f"\rProgress: {progress:.2f}% ({frame_count}/{max_frames} frames)", end="", flush=True)
                if frame_count >= max_frames:
                    print("\nRendering complete!")
                    break

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        renderer.cleanup()

if __name__ == "__main__":
    main()
