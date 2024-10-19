import glfw
from OpenGL.GL import *
from pbr_shaders import Shader
from scene import Scene
import numpy as np
from recorder import Recorder
import time

# Define constants for anisotropic filtering
GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT = 0x84FF
GL_TEXTURE_MAX_ANISOTROPY_EXT = 0x84FE


class Renderer:
    def __init__(self, width, height, record=False, fps=30):
        self.width = width
        self.height = height
        self.shader = None
        self.scene = None
        self.fbo = None
        self.hdr_texture = None
        self.recorder = None
        self.record = record
        self.window = None
        self.initialized = False
        self.context = None
        self.fps = fps
        self.frame_time = 1.0 / fps



    def initialize(self):
        try:
            if not glfw.init():
                raise Exception("GLFW initialization failed")

            if self.record:
                # self.width, self.height = 7680, 4320
                self.width, self.height = 2880, 1800
                glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
                self.window = glfw.create_window(self.width, self.height, "Offscreen", None, None)
            else:
                glfw.window_hint(glfw.SAMPLES, 8)
                self.window = glfw.create_window(self.width, self.height, "PBR Scene", None, None)

            if not self.window:
                raise Exception("Failed to create GLFW window")

            glfw.make_context_current(self.window)
            self.context = glfw.get_current_context()

            glEnable(GL_DEPTH_TEST)
            if not self.record:
                glEnable(GL_MULTISAMPLE)

            shader_obj = Shader()
            self.shader = shader_obj.compile()
            if not self.shader:
                raise Exception("Shader compilation failed")

            self.scene = Scene(self.shader, self.width, self.height)
            self.fbo, self.hdr_texture = self.create_framebuffer(self.width, self.height)

            if self.record:
                print(f"Initializing recorder with dimensions: {self.width}x{self.height}")
                self.recorder = Recorder(self.width, self.height, self.fps)

            self.initialized = True
            print("Renderer initialized successfully")
        except Exception as e:
            print(f"Error during initialization: {e}")
            self.cleanup()

    def render(self, objects, delta_time):
        if not self.initialized or not self.context:
            print("Renderer not initialized or no valid context. Skipping render.")
            return

        start_time = time.time()

        glfw.make_context_current(self.window)

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader)
        self.scene.set_camera_and_lighting()

        for obj in objects:
            model_matrix = obj.animate(delta_time)
            self.scene.draw_object(model_matrix, obj)

        if self.record and self.recorder:
            pixels = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_FLOAT)
            image = (np.frombuffer(pixels, dtype=np.float32).reshape(self.height, self.width, 3) * 255).astype(np.uint8)
            image = np.flip(image, axis=0)  # Flip vertically
            self.recorder.capture_frame(image)
            print(f"Captured frame {self.recorder.frame_count}")

        if not self.record:
            glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo)
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
            glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height, GL_COLOR_BUFFER_BIT, GL_NEAREST)
            glfw.swap_buffers(self.window)

        glfw.poll_events()

        end_time = time.time()
        sleep_time = self.frame_time - (end_time - start_time)
        if sleep_time > 0:
            time.sleep(sleep_time)

    def create_framebuffer(self, width, height):
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, width, height, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if glGetString(GL_EXTENSIONS) and b"GL_EXT_texture_filter_anisotropic" in glGetString(GL_EXTENSIONS):
            max_anisotropy = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, min(16.0, max_anisotropy))

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

        rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer is not complete")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return fbo, texture

    def cleanup(self):
        print("\nStarting cleanup process")
        if self.recorder:
            print("Finalizing video...")
            self.recorder.finalize_video()

        if self.initialized and self.context:
            glfw.make_context_current(self.window)
            if self.fbo is not None:
                print(f"Deleting framebuffer: {self.fbo}")
                glDeleteFramebuffers(1, [self.fbo])
            if self.hdr_texture is not None:
                print(f"Deleting texture: {self.hdr_texture}")
                glDeleteTextures(1, [self.hdr_texture])
            if self.shader is not None:
                print(f"Deleting shader program: {self.shader}")
                glDeleteProgram(self.shader)

        if self.window:
            glfw.destroy_window(self.window)

        print("Terminating GLFW")
        glfw.terminate()
        print("Cleanup complete")

    def should_close(self):
        return self.window and glfw.window_should_close(self.window)

    def poll_events(self):
        glfw.poll_events()
