from OpenGL.GL import *
import pyrr
import numpy as np

class Scene:
    def __init__(self, shader, width, height):
        self.shader = shader
        self.width = width
        self.height = height
        self.lights = []

        # Set the projection matrix (static for the scene)
        # self.projection = pyrr.matrix44.create_perspective_projection(45, width / height, 0.1, 50, dtype=np.float32)
        self.projection = pyrr.matrix44.create_perspective_projection(
            fovy=40.0, aspect=width/height, near=0.1, far=100.0, dtype=np.float32
        )

        # Use the shader program
        glUseProgram(self.shader)

        # Retrieve uniform locations
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.view_loc = glGetUniformLocation(self.shader, "view")
        self.projection_loc = glGetUniformLocation(self.shader, "projection")

        # Set up projection matrix
        projection = pyrr.matrix44.create_perspective_projection_matrix(45.0, width / height, 0.1, 100.0)
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, projection)

        # Add location for normal matrix
        self.normal_matrix_loc = glGetUniformLocation(self.shader, "normalMatrix")

    def calculate_normal_matrix(self, model_matrix):
        """Calculate the normal matrix from the model matrix"""
        # Extract the 3x3 rotation/scale part of the model matrix
        normal_matrix = np.array([
            [model_matrix[0][0], model_matrix[0][1], model_matrix[0][2]],
            [model_matrix[1][0], model_matrix[1][1], model_matrix[1][2]],
            [model_matrix[2][0], model_matrix[2][1], model_matrix[2][2]]
        ], dtype=np.float32)

        # Calculate the inverse transpose
        # For a rigid body transformation (rotation only),
        # the inverse transpose is the same as the original 3x3 matrix
        # For non-uniform scaling, we need to actually calculate the inverse transpose
        try:
            normal_matrix = np.transpose(np.linalg.inv(normal_matrix))
        except np.linalg.LinAlgError:
            # If matrix is not invertible, fall back to original matrix
            pass

        return normal_matrix

    def add_light(self, light):
        self.lights.append(light)

    def set_camera_and_lighting(self):
        camera_pos = pyrr.vector3.create(0, 0, 25)  # Move camera further back
        target = pyrr.vector3.create(0, 0, 0)
        up = pyrr.vector3.create(0, 1, 0)
        view = pyrr.matrix44.create_look_at(camera_pos, target, up, dtype=np.float32)

        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, self.projection)
        glUniform3fv(glGetUniformLocation(self.shader, "viewPos"), 1, camera_pos)

        # print(f"Number of lights: {len(self.lights)}")
        for i, light in enumerate(self.lights):
            # print(f"Light {i}: position = {light.position}, color = {light.color}, intensity = {light.intensity}")
            glUniform3fv(glGetUniformLocation(self.shader, f"lightPos[{i}]"), 1, light.position)
            glUniform3fv(glGetUniformLocation(self.shader, f"lightColor[{i}]"), 1, light.color * light.intensity)

        glUniform1i(glGetUniformLocation(self.shader, "numLights"), len(self.lights))


    def draw_object(self, model_matrix, obj):
        # Set the model matrix
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, model_matrix)

        # Calculate and set the normal matrix
        normal_matrix = self.calculate_normal_matrix(model_matrix)
        glUniformMatrix3fv(self.normal_matrix_loc, 1, GL_FALSE, normal_matrix)

        # Set material properties
        glUniform3fv(glGetUniformLocation(self.shader, "albedo"), 1, obj.albedo)
        glUniform1f(glGetUniformLocation(self.shader, "metallic"), obj.metallic)
        glUniform1f(glGetUniformLocation(self.shader, "roughness"), obj.roughness)
        glUniform1f(glGetUniformLocation(self.shader, "ao"), obj.ao)

        # Draw the object
        obj.draw(self.shader)
