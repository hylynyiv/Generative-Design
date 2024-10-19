![AnimGenerator]([path_to_image_in_repo](https://github.com/hylynyiv/Generative-Design/blob/master/AnimGenerator/PyOpenGLAnim00.gif))


# PyOpenGL 3D Animation Kit

This project is a customizable 3D animation kit built using **PyOpenGL** and **GLFW**. It supports procedural generation of various 3D objects such as cubes, spheres, icosahedrons, and pyramids with **physically based rendering (PBR) shaders** for realistic lighting and material effects. The scene includes multiple light sources, object animations, and dynamic camera views, offering flexibility to create visually appealing animations.

### Features

- **Multiple 3D Object Types**: Supports various shapes like cubes, pyramids, spheres, and icosahedrons.
- **Physically Based Rendering (PBR)**: Realistic lighting effects including specular highlights, metallic and roughness properties.
- **Dynamic Animation**: Objects rotate, translate, and scale with customizable speed and direction.
- **Multi-Light Support**: Configurable light sources for enhanced visual dynamics.
- **Framebuffer Rendering**: Uses HDR framebuffer for high-quality output.
- **Modular Structure**: Easy-to-extend architecture for new objects and effects.

### Requirements

- Python 3.x
- PyOpenGL
- GLFW
- Numpy
- Pyrr

You can install the required dependencies using:

```bash
pip install pyopengl glfw numpy pyrr
```

### Usage

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. **Run the program:**

```bash
python main.py
```

This will open a window displaying randomly generated objects rotating and moving in a 3D space with dynamic lighting. The camera is fixed, and the objects move around within the scene.

3. **Customization:**

- To change the number of objects, their shapes, or behaviors, modify the `elements_quantity`, `movement_speed`, and `rotation_speed` variables in `main.py`.
- New objects can be created by editing or extending the `objects.py` file.
- Lights can be modified in the `main.py` file by adjusting their position, color, and intensity.
