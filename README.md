![Animation Preview](https://github.com/hylynyiv/Generative-Design/raw/master/Anima%20Fresnel/PyOpenGLAnim00.gif)


---

# **Anima Fresnel**

Anima Fresnel is a real-time rendering engine written in Python using OpenGL. It allows users to create 3D scenes composed of customizable objects, lights, and cameras using a JSON configuration file. The engine supports physically based rendering (PBR), custom animations, and object arrangement in different patterns (grid, circular, and spiral). It also includes functionality for recording the rendered scenes.

## **Features**
- **Physically Based Rendering (PBR)** for realistic material properties like albedo, metallic, roughness, and ambient occlusion.
- **Support for various 3D shapes**: cubes, spheres, ellipsoids, toruses, and more.
- **Keyframe animations** to animate object transformations such as translation, rotation, and scaling.
- **Customizable lighting setup**, supporting point and directional lights.
- **Scene configuration** through a JSON file for easy setup of objects, lights, and animations.
- **Automatic arrangement** of objects using containers like grid, circular, and spiral patterns.
- **Recording functionality** to capture rendered frames to video.

---

## **Table of Contents**
- [Installation](#installation)
- [Usage](#usage)
  - [Getting Started](#getting-started)
  - [JSON Configuration](#json-configuration)
  - [Recording](#recording)
- [License](#license)

---

## **Installation**

### **Requirements**

Ensure the following dependencies are installed:
- Python 3.6 or higher
- GLFW
- OpenGL
- Pyrr (for matrix and vector operations)
- Numpy

You can install the required dependencies via `pip`:

```bash
pip install glfw pyopengl pyrr numpy
```

### **Optional Requirements for Recording**
For recording functionality, you'll need additional libraries for handling video output:

```bash
pip install imageio[ffmpeg]
```

### **Cloning the Repository**

To get started, clone this repository:

```bash
git clone https://github.com/hylynyiv/Generative-Design.git
cd Generative-Design/Anima\ Fresnel
```

---

## **Usage**

### **Getting Started**

1. **Running the Engine:**
   To start the engine, simply run `main.py`:

   ```bash
   python3 main.py
   ```

   By default, this will open a window and render the scene based on the configuration in `world_config.json`.

2. **Renderer Controls:**
   - The engine initializes using OpenGL and loads your scene configuration from the `world_config.json` file.
   - It then enters a rendering loop where objects, lights, and animations are rendered based on your settings.

---

### **JSON Configuration**

All the elements of your scene (camera, lights, objects, animations) are controlled through the `world_config.json` file. Below is a breakdown of the key components:

- **Camera**: Sets up the position, orientation, and field of view of the camera.
- **Lights**: Defines point or directional lights in the scene.
- **Objects**: Creates different 3D shapes with customizable properties like material settings, movement, and rotation.
- **Containers**: Arranges objects in grid, circular, or spiral patterns for easy scene setup.
- **Animations**: Attach keyframe animations to objects for custom movement.

#### Example Configuration

```json
{
  "scene": {
    "camera": {
      "position": [0.0, 5.0, 10.0],
      "look_at": [0.0, 0.0, 0.0],
      "up_vector": [0.0, 1.0, 0.0],
      "field_of_view": 45.0,
      "near_clip": 0.1,
      "far_clip": 100.0
    },
    "lights": [
      {
        "type": "point",
        "position": [-10.0, 10.0, -10.0],
        "color": [1.0, 1.0, 1.0],
        "intensity": 100.0
      },
      {
        "type": "directional",
        "direction": [1.0, -1.0, 0.0],
        "color": [0.8, 0.8, 0.8],
        "intensity": 50.0
      }
    ],
    "objects": [
      {
        "type": "cube",
        "properties": {
          "albedo": [0.8, 0.3, 0.1],
          "metallic": 0.6,
          "roughness": 0.4,
          "ao": 1.0,
          "rotation_speed": [0.0, 1.0, 0.0],
          "movement_speed": [0.5, 0.0, 0.0]
        }
      },
      {
        "type": "sphere",
        "properties": {
          "albedo": [0.1, 0.8, 0.1],
          "metallic": 0.3,
          "roughness": 0.5,
          "ao": 1.0,
          "rotation_speed": [0.0, 1.0, 0.5],
          "movement_speed": [0.3, 0.3, 0.0]
        },
        "radius": 1.5
      }
    ],
    "animations": [
      {
        "object": "cube",
        "keyframes": [
          {
            "time": 0,
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0]
          },
          {
            "time": 1,
            "position": [2.0, 0.0, 0.0],
            "rotation": [0.0, 45.0, 0.0],
            "scale": [1.0, 1.0, 1.0]
          }
        ]
      }
    ]
  }
}
```

### **Recording**

To enable recording, set the `record` flag in `main.py` to `True`:

```python
record = True
```

This will render the scene offscreen and save frames as a video. The recording parameters such as resolution (`width`, `height`) and `fps` can be configured in `main.py`.

The rendered video is saved in the current directory when recording is complete.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Contributing**

If you find any issues or have feature requests, feel free to open an issue or submit a pull request. Contributions are welcome!

---

### **Additional Notes**

- Ensure your system supports OpenGL with adequate drivers.
- You can add new shapes, containers, and more via extending the `ObjectFactory` and container classes.
- For complex scene setups, use keyframe animations to control object movement and rotation over time.

---
