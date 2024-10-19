import numpy as np
from OpenGL.GL import *
import pyrr

class BaseObject3D:
    def __init__(self, vertices, indices, texture=None, rotation_speed=(0, 0, 0), movement_speed=(0, 0, 0), scale_speed=(0, 0, 0)):
        self.vertices = vertices
        self.indices = indices
        self.vbo = None
        self.ebo = None
        self.vao = None  # Initialize VAO attribute
        self.texture = texture  # Assuming you have a texture associated with the object
        self.rotation_speed = rotation_speed  # Rotation speed along x, y, z axes
        self.movement_speed = movement_speed  # Translation speed along x, y, z axes
        self.scale_speed = scale_speed  # Speed for dynamic scaling along x, y, z axes
        self.position = np.random.rand(3) * 10.0 - 5.0  # Initial random position within bounds
        self.scale = np.array([1.0, 1.0, 1.0], dtype=np.float32)  # Initial scale
        self.rotation = np.array([0.0, 0.0, 0.0], dtype=np.float32)  # Initialize rotation
        self.bounds = np.array([10.0, 10.0, 10.0], dtype=np.float32)  # Virtual box boundaries
        self.init_buffers()

    def init_buffers(self):
        # # Generate VBO and EBO
        # self.vbo = glGenBuffers(1)
        # self.ebo = glGenBuffers(1)
        #
        # # Bind and set the vertex buffer data
        # glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        #
        # # Bind and set the element buffer data
        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        # glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        #
        # # Unbind buffers
        # glBindBuffer(GL_ARRAY_BUFFER, 0)
        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

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
        """
        Apply the object's rotation, translation, and scaling over time.
        delta_time: The time that has passed since the last frame.
        """
        # Update the object's current rotation angles by adding rotation speed
        self.rotation += delta_time * self.rotation_speed

        # Apply rotation over time
        # Apply rotation based on accumulated rotation
        rotation_matrix = pyrr.matrix44.create_from_eulers([
            self.rotation[0],
            self.rotation[1],
            self.rotation[2]
        ], dtype=np.float32)

        # Update movement and ensure objects bounce within the bounds
        new_position = self.position + delta_time * np.array(self.movement_speed)

        # Reverse movement direction if outside bounds and clamp position within bounds
        for i in range(3):
            if abs(new_position[i]) > self.bounds[i]:
                self.movement_speed[i] *= -1  # Reverse direction
                new_position[i] = np.clip(new_position[i], -self.bounds[i], self.bounds[i])

        # Update the object's position
        self.position = new_position
        # print(f"Object Position: {self.position}")


        # Apply translation (move object)
        translation_matrix = pyrr.matrix44.create_from_translation(self.position, dtype=np.float32)

        # Apply scaling over time
        scaling_matrix = pyrr.matrix44.create_from_scale(self.scale + delta_time * np.array(self.scale_speed), dtype=np.float32)

        # Combine transformations (Scale -> Rotate -> Translate)
        transformation_matrix = pyrr.matrix44.multiply(rotation_matrix, scaling_matrix)
        transformation_matrix = pyrr.matrix44.multiply(transformation_matrix, translation_matrix)

        return transformation_matrix


    def cleanup(self):
        # Clean up buffers
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteBuffers(1, [self.ebo])

class PolyhedralObject(BaseObject3D):
    def __init__(self, shape_type, albedo, metallic, roughness, ao, rotation_speed=(0, 0, 0), movement_speed=(0, 0, 0), scale_speed=(0, 0, 0)):
        self.shape_type = shape_type
        vertices, normals, indices = self.generate_geometry()
        if vertices is None or normals is None or indices is None:
            raise ValueError(f"Shape type '{self.shape_type}' is not supported")

        print(f"Vertices shape: {vertices.shape}, Normals shape: {normals.shape}")

        # Ensure vertices and normals have the same shape
        if vertices.shape != normals.shape:
            raise ValueError(f"Vertices and normals must have the same shape. Vertices: {vertices.shape}, Normals: {normals.shape}")

        # Combine vertices and normals
        combined_data = np.hstack([vertices, normals])

        super().__init__(combined_data, indices, texture=None, rotation_speed=rotation_speed, movement_speed=movement_speed, scale_speed=scale_speed)

        self.albedo = albedo
        self.metallic = metallic
        self.roughness = roughness
        self.ao = ao
        self.init_buffers()

    def generate_geometry(self):
        if self.shape_type == "cube":
            return self.create_cube()
        elif self.shape_type == "pyramid":
            return self.create_pyramid()
        elif self.shape_type == "icosahedron":
            return self.create_icosahedron()
        return None, None, None

    def create_cube(self):
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

    def create_pyramid(self):
        vertices = np.array([
            # Base
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5, -0.5,  0.5,
            -0.5, -0.5,  0.5,
            # Apex (repeated for each side)
             0.0,  0.5,  0.0,
             0.0,  0.5,  0.0,
             0.0,  0.5,  0.0,
             0.0,  0.5,  0.0
        ], dtype=np.float32)

        normals = np.array([
            # Base
             0.0, -1.0,  0.0,
             0.0, -1.0,  0.0,
             0.0, -1.0,  0.0,
             0.0, -1.0,  0.0,
            # Sides (normalized)
             0.8944,  0.4472,  0.0,    # Front
            -0.8944,  0.4472,  0.0,    # Back
             0.0,     0.4472,  0.8944, # Right
             0.0,     0.4472, -0.8944  # Left
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,  # Base
            0, 4, 1,  # Front face
            1, 5, 2,  # Right face
            2, 6, 3,  # Back face
            3, 7, 0   # Left face
        ], dtype=np.uint32)

        return vertices.reshape(-1, 3), normals.reshape(-1, 3), indices

    def create_icosahedron(self):
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

class SmoothObject(BaseObject3D):
    def __init__(self, shape_type, radius=1.0, lat_steps=50, lon_steps=50, albedo=(1.0, 1.0, 1.0), metallic=0.0, roughness=0.5, ao=1.0, rotation_speed=(0, 0, 0), movement_speed=(0, 0, 0), scale_speed=(0, 0, 0)):
        self.radius = radius
        vertices, normals, indices = self.generate_geometry(lat_steps, lon_steps)

        # Combine vertices and normals
        combined_data = np.hstack([vertices, normals])

        super().__init__(combined_data, indices, texture=None, rotation_speed=rotation_speed, movement_speed=movement_speed, scale_speed=scale_speed)

        self.albedo = albedo
        self.metallic = metallic
        self.roughness = roughness
        self.ao = ao
        self.init_buffers()

    def generate_geometry(self, lat_steps, lon_steps):
        vertices = []
        normals = []
        indices = []
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
                vertices.append([self.radius * x, self.radius * y, self.radius * z])
                normals.append([x, y, z])  # For a sphere, normals are just normalized position vectors
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        for i in range(lat_steps):
            for j in range(lon_steps):
                first = i * (lon_steps + 1) + j
                second = first + lon_steps + 1
                indices.extend([first, second, first + 1, second, second + 1, first + 1])
        indices = np.array(indices, dtype=np.uint32)
        return vertices, normals, indices
