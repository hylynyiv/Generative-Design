import glfw
import numpy as np
from objects import PolyhedralObject, SmoothObject
from light import Light
from render import Renderer
import signal
import sys

fps = 30
frame_time = 1.0 / fps

elements_quantity = 65
movement_speed = 5
rotation_speed = 1

#Screen Size
width = 2880
height = 1800

# Flag to enable/disable recording
record = True
renderer = None

def signal_handler(sig, frame):
    print("\nInterrupt received, stopping gracefully...")
    global renderer
    if renderer:
        renderer.cleanup()
    sys.exit(0)


def create_random_object():
    shape_type = np.random.choice(["icosahedron", "cube", "sphere", "pyramid"])
    metallic = np.random.uniform(0.6, 1.0)
    roughness = np.random.uniform(0.0, 0.6)
    # Add random scaling factor (between 0.5 and 2.0) to preserve variety in object sizes
    scale = np.random.uniform(0.5, 2.0, size=3)

    if shape_type == "sphere":
        obj = SmoothObject(
            shape_type=shape_type,
            radius=np.random.uniform(0.5, 1.5),
            lat_steps=50,
            lon_steps=50,
            albedo=np.random.rand(3),
            metallic=metallic,
            roughness=roughness,
            ao=1.0,
            rotation_speed=np.random.rand(3) * rotation_speed,
            movement_speed=(np.random.rand(3) - 0.5) * movement_speed,
            scale_speed=np.random.rand(3) * 0.1  # Optional dynamic scaling speed

        )
    else:
        obj = PolyhedralObject(
            shape_type=shape_type,
            albedo=np.random.rand(3),
            metallic=metallic,
            roughness=roughness,
            ao=1.0,
            rotation_speed=np.random.rand(3) * rotation_speed,
            movement_speed=(np.random.rand(3) - 0.5) * movement_speed,
            scale_speed=np.random.rand(3) * 0.4  # Optional dynamic scaling speed

        )

    obj.position = np.random.uniform(-5, 5, 3)
    print(f"Created {shape_type} object with position {obj.position}, metallic {metallic}, roughness {roughness}")
    return obj

def main():
    global renderer
    renderer = Renderer(width, height, record=record, fps=fps)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        renderer.initialize()
        if not renderer.initialized:
            print("Renderer initialization failed. Exiting.")
            return

        # Create lights
        lights = [
            Light(position=[-10.0, 10.0, -10.0], color=[1.0, 1.0, 1.0], intensity=100),
            Light(position=[10.0, 10.0, -10.0], color=[1.0, 1.0, 1.0], intensity=100),
            Light(position=[-10.0, -10.0, 10.0], color=[1.0, 1.0, 1.0], intensity=100),
            Light(position=[10.0, -10.0, 10.0], color=[1.0, 1.0, 1.0], intensity=100)
        ]
        for light in lights:
            renderer.scene.add_light(light)

        # Create objects
        objects = [create_random_object() for _ in range(65)]  # Assuming 65 is your elements_quantity

        # Main render loop
        frame_count = 0
        max_frames = 300  # 10 seconds at 30 fps

        while not renderer.should_close() and frame_count < max_frames:
            renderer.render(objects, 1.0 / fps)  # Pass the frame time
            frame_count += 1
            # if frame_count % 10 == 0:
            #     print(f"Rendered frame {frame_count}")

            # Progress indicator
            progress = (frame_count / max_frames) * 100
            print(f"\rProgress: {progress:.2f}% ({frame_count}/{max_frames} frames)", end="", flush=True)

        print("\nRendering complete!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        renderer.cleanup()

if __name__ == "__main__":
    main()
