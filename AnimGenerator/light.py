import numpy as np

class Light:
    def __init__(self, position, color, intensity=1.0, light_type='point'):
        """
        Initialize a light source.
        :param position: vec3 position of the light.
        :param color: vec3 color of the light (RGB).
        :param intensity: Intensity/brightness of the light.
        :param light_type: 'point', 'directional', or 'spot' (default is 'point').
        """
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.intensity = intensity
        self.light_type = light_type  # Could be 'point', 'directional', or 'spot'
