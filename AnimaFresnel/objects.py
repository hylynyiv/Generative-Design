from abc import ABC, abstractmethod
import numpy as np
from OpenGL.GL import *
import pyrr
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class ObjectProperties:
    albedo: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    metallic: float = 0.0
    roughness: float = 0.5
    ao: float = 1.0
    rotation_speed: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    movement_speed: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale_speed: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounds: Optional[np.ndarray] = None

class GeometryGenerator:
    @staticmethod
    def create_cube():
        vertices = np.array([
            # Front face
            -0.5, -0.5,  0.5,
             0.5, -0.5,  0.5,
             0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5,
            # Back face
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5,  0.5, -0.5,
            -0.5,  0.5, -0.5,
        ], dtype=np.float32)

        normals = np.array([
            # Front face
             0.0,  0.0,  1.0,
             0.0,  0.0,  1.0,
             0.0,  0.0,  1.0,
             0.0,  0.0,  1.0,
            # Back face
             0.0,  0.0, -1.0,
             0.0,  0.0, -1.0,
             0.0,  0.0, -1.0,
             0.0,  0.0, -1.0,
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,  # Front face
            4, 5, 6, 6, 7, 4,  # Back face
            0, 4, 7, 7, 3, 0,  # Left face
            1, 5, 6, 6, 2, 1,  # Right face
            3, 2, 6, 6, 7, 3,  # Top face
            0, 1, 5, 5, 4, 0   # Bottom face
        ], dtype=np.uint32)

        return vertices.reshape(-1, 3), normals.reshape(-1, 3), indices

    @staticmethod
    def create_pyramid():
        vertices = np.array([
            # Base
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5, -0.5,  0.5,
            -0.5, -0.5,  0.5,
            # Apex
             0.0,  0.5,  0.0
        ], dtype=np.float32)

        normals = np.array([
            # Base
             0.0, -1.0,  0.0,
             0.0, -1.0,  0.0,
             0.0, -1.0,  0.0,
             0.0, -1.0,  0.0,
            # Sides (averaged normal for triangle faces)
             0.0,  1.0,  1.0,
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,  # Base
            0, 4, 1,            # Front face
            1, 4, 2,            # Right face
            2, 4, 3,            # Back face
            3, 4, 0             # Left face
        ], dtype=np.uint32)

        return vertices.reshape(-1, 3), normals.reshape(-1, 3), indices

    @staticmethod
    def create_icosahedron():
        phi = (1 + np.sqrt(5)) / 2
        vertices = np.array([
            [-1,  phi, 0], [ 1,  phi, 0], [-1, -phi, 0], [ 1, -phi, 0],
            [0, -1,  phi], [0,  1,  phi], [0, -1, -phi], [0,  1, -phi],
            [ phi, 0, -1], [ phi, 0,  1], [-phi, 0, -1], [-phi, 0,  1]
        ], dtype=np.float32) / np.sqrt(1 + phi**2)

        indices = np.array([
            0, 11,  5,    0,  5,  1,    0,  1,  7,    0,  7, 10,    0, 10, 11,
            1,  5,  9,    5, 11,  4,   11, 10,  2,   10,  7,  6,    7,  1,  8,
            3,  9,  4,    3,  4,  2,    3,  2,  6,    3,  6,  8,    3,  8,  9,
            4,  9,  5,    2,  4, 11,    6,  2, 10,    8,  6,  7,    9,  8,  1
        ], dtype=np.uint32)

        normals = vertices / np.linalg.norm(vertices, axis=1)[:, np.newaxis]

        return vertices, normals, indices

    @staticmethod
    def create_sphere(radius, lat_steps, lon_steps):
        vertices, normals, indices = [], [], []
        for i in range(lat_steps + 1):
            theta = np.pi * i / lat_steps
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            for j in range(lon_steps + 1):
                phi = 2 * np.pi * j / lon_steps
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)
                x = cos_phi * sin_theta
                y = cos_theta
                z = sin_phi * sin_theta
                vertices.append([radius * x, radius * y, radius * z])
                normals.append([x, y, z])  # Normals are just the normalized position vectors
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        for i in range(lat_steps):
            for j in range(lon_steps):
                first = i * (lon_steps + 1) + j
                second = first + lon_steps + 1
                indices.extend([first, second, first + 1, second, second + 1, first + 1])
        indices = np.array(indices, dtype=np.uint32)
        return vertices, normals, indices

    @staticmethod
    def create_ellipsoid(radius_x, radius_y, radius_z, lat_steps, lon_steps):
        vertices, normals, indices = [], [], []
        for i in range(lat_steps + 1):
            theta = np.pi * i / lat_steps
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            for j in range(lon_steps + 1):
                phi = 2 * np.pi * j / lon_steps
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)
                x = cos_phi * sin_theta * radius_x
                y = cos_theta * radius_y
                z = sin_phi * sin_theta * radius_z
                vertices.append([x, y, z])
                normals.append([x / radius_x, y / radius_y, z / radius_z])  # Normals are proportional to the ellipsoid
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        for i in range(lat_steps):
            for j in range(lon_steps):
                first = i * (lon_steps + 1) + j
                second = first + lon_steps + 1
                indices.extend([first, second, first + 1, second, second + 1, first + 1])
        indices = np.array(indices, dtype=np.uint32)
        return vertices, normals, indices

    @staticmethod
    def create_cylinder(radius, height, lat_steps):
        vertices, normals, indices = [], [], []
        for i in range(lat_steps + 1):
            theta = 2 * np.pi * i / lat_steps
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            for j in [0, 1]:
                y = (j - 0.5) * height  # Top and bottom
                vertices.append([radius * cos_theta, y, radius * sin_theta])
                normals.append([cos_theta, 0, sin_theta])
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        for i in range(lat_steps):
            first = 2 * i
            second = first + 2
            indices.extend([first, second, first + 1, second, second + 1, first + 1])
        indices = np.array(indices, dtype=np.uint32)
        return vertices, normals, indices

    @staticmethod
    def create_torus(outer_radius, inner_radius, radial_steps, tube_steps):
        vertices, normals, indices = [], [], []
        for i in range(radial_steps):
            theta = 2 * np.pi * i / radial_steps
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            for j in range(tube_steps):
                phi = 2 * np.pi * j / tube_steps
                cos_phi = np.cos(phi)
                sin_phi = np.sin(phi)
                x = (outer_radius + inner_radius * cos_theta) * cos_phi
                y = (outer_radius + inner_radius * cos_theta) * sin_phi
                z = inner_radius * sin_theta
                vertices.append([x, y, z])
                normals.append([cos_theta * cos_phi, cos_theta * sin_phi, sin_theta])
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        for i in range(radial_steps):
            for j in range(tube_steps):
                first = i * tube_steps + j
                second = ((i + 1) % radial_steps) * tube_steps + j
                indices.extend([first, second, first + 1, second, second + 1, first + 1])
        indices = np.array(indices, dtype=np.uint32)
        return vertices, normals, indices

    @staticmethod
    def create_curved_plane(lat_steps, lon_steps, curvature, concave=True):
        vertices, normals, indices = [], [], []
        sign = -1 if concave else 1
        for i in range(lat_steps + 1):
            theta = np.pi * i / lat_steps
            for j in range(lon_steps + 1):
                phi = 2 * np.pi * j / lon_steps
                x = np.cos(phi) * np.sin(theta)
                y = np.sin(sign * curvature * theta)
                z = np.sin(phi) * np.sin(theta)
                vertices.append([x, y, z])
                normals.append([x, y, z])  # Normals are proportional to the shape
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        for i in range(lat_steps):
            for j in range(lon_steps):
                first = i * (lon_steps + 1) + j
                second = first + lon_steps + 1
                indices.extend([first, second, first + 1, second, second + 1, first + 1])
        indices = np.array(indices, dtype=np.uint32)
        return vertices, normals, indices



class Object3D(ABC):
    def __init__(self, vertices, indices, properties: ObjectProperties, name=None):
        self.vertices = vertices
        self.indices = indices
        self.properties = properties
        self.vbo = None
        self.ebo = None
        self.position = np.random.rand(3) * 10.0 - 5.0
        self.scale = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.rotation = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.init_buffers()

    def init_buffers(self):
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # Unbind buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def draw(self, shader):
        # Bind the object's VBO and EBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"Error binding VBO: {error}")
            return  # Exit the draw function if there’s an error

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"Error binding EBO: {error}")
            return  # Exit if there’s an error

        # Query attribute locations from the shader
        posAttrib = glGetAttribLocation(shader, "aPos")
        normalAttrib = glGetAttribLocation(shader, "aNormal")

        # Set up vertex attribute pointers
        glVertexAttribPointer(posAttrib, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(posAttrib)

        glVertexAttribPointer(normalAttrib, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(normalAttrib)

        # Draw the object using indices
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        # Disable vertex attribute arrays after drawing
        glDisableVertexAttribArray(normalAttrib)
        glDisableVertexAttribArray(posAttrib)

        # Unbind buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"Error setting vertex attributes: {error}")

    def animate(self, delta_time):
        # Apply rotation based on rotation speed
        print(f"Object rotation before: {self.rotation}")
        self.rotation += delta_time * np.array(self.properties.rotation_speed)
        print(f"Object rotation after: {self.rotation}")

        # Apply translation (movement)
        print(f"Object position before: {self.position}")
        self.position += delta_time * np.array(self.properties.movement_speed)
        print(f"Object position after: {self.position}")

        # Apply scaling if necessary (if scaling is changing over time)
        self.scale += delta_time * np.array(self.properties.scale_speed)

        # Create transformation matrices
        rotation_matrix = pyrr.matrix44.create_from_eulers(self.rotation, dtype=np.float32)
        translation_matrix = pyrr.matrix44.create_from_translation(self.position, dtype=np.float32)
        scaling_matrix = pyrr.matrix44.create_from_scale(self.scale, dtype=np.float32)

        # Combine transformations: Scale -> Rotate -> Translate
        model_matrix = pyrr.matrix44.multiply(rotation_matrix, scaling_matrix)
        model_matrix = pyrr.matrix44.multiply(model_matrix, translation_matrix)

        return model_matrix



    def cleanup(self):
        glDeleteBuffers(1, [self.vbo])
        glDeleteBuffers(1, [self.ebo])

class PolyhedralObject(Object3D):
    def __init__(self, shape_type: str, properties: ObjectProperties, name=None):
        if shape_type == 'cube':
            vertices, normals, indices = GeometryGenerator.create_cube()
        elif shape_type == 'pyramid':
            vertices, normals, indices = GeometryGenerator.create_pyramid()
        elif shape_type == 'icosahedron':
            vertices, normals, indices = GeometryGenerator.create_icosahedron()
        else:
            raise ValueError(f"Unsupported shape type: {shape_type}")

        combined_data = np.hstack([vertices, normals])
        super().__init__(combined_data, indices, properties, name)


class SmoothObject(Object3D):
    def __init__(self, shape_type: str, properties: ObjectProperties, **kwargs):
        if shape_type == 'sphere':
            vertices, normals, indices = GeometryGenerator.create_sphere(
                kwargs.get('radius', 1.0),
                kwargs.get('lat_steps', 50),
                kwargs.get('lon_steps', 50)
            )
        elif shape_type == 'torus':
            vertices, normals, indices = GeometryGenerator.create_torus(
                kwargs.get('outer_radius', 1.5),
                kwargs.get('inner_radius', 0.5),
                kwargs.get('radial_steps', 40),
                kwargs.get('tube_steps', 20)
            )
        elif shape_type == 'ellipsoid':
            vertices, normals, indices = GeometryGenerator.create_ellipsoid(
                kwargs.get('radius_x', 1.0),
                kwargs.get('radius_y', 0.7),
                kwargs.get('radius_z', 1.5),
                kwargs.get('lat_steps', 40),
                kwargs.get('lon_steps', 40)
            )
        elif shape_type == 'cylinder':
            vertices, normals, indices = GeometryGenerator.create_cylinder(
                kwargs.get('radius', 1.0),
                kwargs.get('height', 2.0),
                kwargs.get('lat_steps', 50)
            )
        elif shape_type == 'convex_plane':
            vertices, normals, indices = GeometryGenerator.create_curved_plane(
                radius=kwargs.get('radius', 1.0),
                lat_steps=kwargs.get('lat_steps', 50),
                lon_steps=kwargs.get('lon_steps', 50),
                curvature_direction='convex'
            )
        elif shape_type == 'concave_plane':
            vertices, normals, indices = GeometryGenerator.create_curved_plane(
                radius=kwargs.get('radius', 1.0),
                lat_steps=kwargs.get('lat_steps', 50),
                lon_steps=kwargs.get('lon_steps', 50),
                curvature_direction='concave'
            )
        else:
            raise ValueError(f"Unsupported shape type: {shape_type}")

        combined_data = np.hstack([vertices, normals])
        super().__init__(combined_data, indices, properties, kwargs.get('name'))


class ObjectFactory:
    @staticmethod
    def create_object(shape_type: str, properties: ObjectProperties, **kwargs) -> Object3D:
        if not isinstance(kwargs, dict):
            raise TypeError(f"Expected a dictionary for kwargs, but got {type(kwargs).__name__}")

        if shape_type in ['cube', 'pyramid', 'icosahedron']:
            return PolyhedralObject(shape_type, properties)
        elif shape_type in ['sphere', 'ellipsoid', 'torus', 'cylinder', 'convex_plane', 'concave_plane']:
            return SmoothObject(shape_type, properties, **kwargs)
        else:
            raise ValueError(f"Unsupported shape type: {shape_type}")

# Usage example:
# properties = ObjectProperties(albedo=(1.0, 0.0, 0.0), metallic=0.5, roughness=0.2)
# cube = ObjectFactory.create_object('cube', properties)
# sphere = ObjectFactory.create_object('sphere', properties, radius=1.0, lat_steps=50, lon_steps=50)
