import numpy as np

class Light:
    def __init__(self, position=None, direction=None, color=(1.0, 1.0, 1.0), intensity=1.0, light_type="point"):
        """
        Initialize a light source.
        :param position: vec3 position of the light (for point lights).
        :param direction: vec3 direction of the light (for directional lights).
        :param color: vec3 color of the light.
        :param intensity: Brightness of the light.
        :param light_type: Type of light ('point', 'directional').
        """
        self.position = position
        self.direction = direction
        self.color = np.array(color, dtype=np.float32)
        self.intensity = intensity
        self.type = light_type  # Could be 'point' or 'directional'


    def is_directional(self):
        return self.light_type == 'directional'

    def set_position(self, new_position):
        self.position = np.array(new_position, dtype=np.float32)

    def set_color(self, new_color):
        self.color = np.array(new_color, dtype=np.float32)
