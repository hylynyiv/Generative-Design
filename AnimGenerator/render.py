import glfw
from OpenGL.GL import *
from pbr_shaders import Shader
from scene import Scene
import numpy as np

# Define constants for anisotropic filtering
GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT = 0x84FF
GL_TEXTURE_MAX_ANISOTROPY_EXT = 0x84FE

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.shader = None
        self.scene = None
        self.fbo = None
        self.hdr_texture = None

    def initialize(self):
        # Initialize GLFW and create window
        if not glfw.init():
            raise Exception("GLFW initialization failed")

        glfw.window_hint(glfw.SAMPLES, 8)  # Enable MSAA
        self.window = glfw.create_window(self.width, self.height, "PBR Scene", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(self.window)

        # Enable OpenGL features
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)

        # Compile shaders
        shader_obj = Shader()
        self.shader = shader_obj.compile()
        if not self.shader:
            raise Exception("Shader compilation failed")

        # Create Scene
        self.scene = Scene(self.shader, self.width, self.height)

        # Create framebuffer for HDR rendering
        self.fbo, self.hdr_texture = self.create_framebuffer()

    def create_framebuffer(self):
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

        # Create HDR color buffer texture
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, self.width, self.height, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Apply anisotropic filtering if available
        if glGetString(GL_EXTENSIONS) and b"GL_EXT_texture_filter_anisotropic" in glGetString(GL_EXTENSIONS):
            max_anisotropy = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, min(16.0, max_anisotropy))

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

        # Create and attach depth buffer
        rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer is not complete")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return fbo, texture

    def render(self, objects, delta_time):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader)
        self.scene.set_camera_and_lighting()

        for obj in objects:
            model_matrix = obj.animate(delta_time)
            self.scene.draw_object(model_matrix, obj)


        # Blit to default framebuffer and apply tone mapping
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_COLOR_BUFFER_BIT, GL_NEAREST)

        glfw.swap_buffers(self.window)

    def cleanup(self):
        glDeleteFramebuffers(1, [self.fbo])
        glDeleteTextures(1, [self.hdr_texture])
        glDeleteProgram(self.shader)
        glfw.terminate()

    def should_close(self):
        return glfw.window_should_close(self.window)

    def poll_events(self):

        glfw.poll_events()
