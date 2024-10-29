from OpenGL.GL import *
import pyrr
import numpy as np
from OpenGL.GL import glGetError, GL_NO_ERROR

class Scene:
    def __init__(self, shader, width, height):
        self.shader = shader
        self.width = width
        self.height = height
        self.camera = None
        self.lights = []
        self.objects = []

        glUseProgram(self.shader)

        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.view_loc = glGetUniformLocation(self.shader, "view")
        self.projection_loc = glGetUniformLocation(self.shader, "projection")
        self.normal_matrix_loc = glGetUniformLocation(self.shader, "normalMatrix")

    def setup_scene(self, genesis):
        scene_data = genesis.get_elements()
        print(scene_data)
        self.camera = scene_data["camera"]
        self.lights = scene_data["lights"]
        self.objects = scene_data["objects"]

        self.update_projection_matrix()

    def update_projection_matrix(self):
        if self.camera:
            self.projection = pyrr.matrix44.create_perspective_projection(
                fovy=self.camera.field_of_view,
                aspect=self.width / self.height,
                near=self.camera.near_clip,
                far=self.camera.far_clip,
                dtype=np.float32
            )
            glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, self.projection)


    def calculate_normal_matrix(self, model_matrix):
        # Extract the upper-left 3x3 part of the model matrix (the rotational part)
        normal_matrix = np.array(model_matrix[:3, :3], dtype=np.float32)

        # Calculate the transpose of the inverse of the normal matrix
        normal_matrix = np.linalg.inv(normal_matrix).T

        return normal_matrix


    def set_camera_and_lighting(self):
        print(f"Camera: {self.camera}")  # Check if camera is initialized
        if self.camera:
            print(f"Camera position: {self.camera.position}, look_at: {self.camera.look_at}, up_vector: {self.camera.up_vector}")
        else:
            print("Camera not initialized")

        print(f"Lights: {self.lights}")  # Check if lights are initialized
        glUseProgram(self.shader)

        # Camera view matrix
        if self.camera:
            view = pyrr.matrix44.create_look_at(
                eye=self.camera.position,
                target=self.camera.look_at,
                up=self.camera.up_vector,
                dtype=np.float32
            )
            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, view)
            check_gl_errors()
            glUniform3fv(glGetUniformLocation(self.shader, "viewPos"), 1, self.camera.position)
            check_gl_errors()
        else:
            print("Camera not set correctly")

        # Ensure the projection matrix is set
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, self.projection)
        check_gl_errors()

        # Lighting setup
        for i, light in enumerate(self.lights):
            if light.type == 'point':
                # Point light uses position
                print(f"Point Light {i}: position = {light.position}, color = {light.color}, intensity = {light.intensity}")
                glUniform3fv(glGetUniformLocation(self.shader, f"lightPos[{i}]"), 1, light.position)
            elif light.type == 'directional':
                # Directional light uses direction
                print(f"Directional Light {i}: direction = {light.direction}, color = {light.color}, intensity = {light.intensity}")
                glUniform3fv(glGetUniformLocation(self.shader, f"lightDir[{i}]"), 1, light.direction)
            check_gl_errors()
            glUniform3fv(glGetUniformLocation(self.shader, f"lightColor[{i}]"), 1, light.color * light.intensity)
            check_gl_errors()

        glUniform1i(glGetUniformLocation(self.shader, "numLights"), len(self.lights))
        check_gl_errors()

        print(f"Amount Lights: {len(self.lights)}")


    def draw_objects(self, delta_time):
        print(f"Drawing {len(self.objects)} objects...")  # Log the number of objects
        for i, obj in enumerate(self.objects):
            print(f"Drawing object {i}: {obj}")  # Log each object

            # Animation and model matrix update
            model_matrix = obj.animate(delta_time)
            print(f"Object {i} model matrix: {model_matrix}")  # Log the model matrix

            glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, model_matrix)
            check_gl_errors()  # Check for any OpenGL errors

            # Normal matrix calculation and upload
            normal_matrix = self.calculate_normal_matrix(model_matrix)
            print(f"Object {i} normal matrix: {normal_matrix}")  # Log the normal matrix

            glUniformMatrix3fv(self.normal_matrix_loc, 1, GL_FALSE, normal_matrix)
            check_gl_errors()

            # Set material properties uniforms
            print(f"Object {i} properties: Albedo = {obj.properties.albedo}, Metallic = {obj.properties.metallic}, Roughness = {obj.properties.roughness}, AO = {obj.properties.ao}")  # Log object properties

            glUniform3fv(glGetUniformLocation(self.shader, "albedo"), 1, obj.properties.albedo)
            check_gl_errors()
            glUniform1f(glGetUniformLocation(self.shader, "metallic"), obj.properties.metallic)
            check_gl_errors()
            glUniform1f(glGetUniformLocation(self.shader, "roughness"), obj.properties.roughness)
            check_gl_errors()
            glUniform1f(glGetUniformLocation(self.shader, "ao"), obj.properties.ao)
            check_gl_errors()

            # Draw the object
            print(f"Rendering object {i}...")  # Log rendering step
            obj.draw(self.shader)
            check_gl_errors()  # Check for any OpenGL errors during drawing

        print("Finished drawing objects.")


def check_gl_errors():
    err = glGetError()
    if err != GL_NO_ERROR:
        print(f"OpenGL error: {err}")
