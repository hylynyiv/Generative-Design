import glfw
import numpy as np
from objects import PolyhedralObject, SmoothObject
from light import Light
from render import Renderer

elements_quantity = 65
movement_speed = 5
rotation_speed = 1


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
    width, height = 2880, 1800
    renderer = Renderer(width, height)

    try:
        renderer.initialize()

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
        objects = [create_random_object() for _ in range(elements_quantity)]

        # Main render loop
        last_time = glfw.get_time()
        while not renderer.should_close():
            current_time = glfw.get_time()
            delta_time = current_time - last_time
            last_time = current_time

            renderer.render(objects, delta_time)
            renderer.poll_events()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        renderer.cleanup()

if __name__ == "__main__":
    main()
