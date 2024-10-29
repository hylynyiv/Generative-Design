import numpy as np

from objects import ObjectProperties

class Container:
    def __init__(self, objects, spacing=(1.0, 1.0, 1.0), material_override=None):
        """
        Container superclass to manage objects.

        :param objects: List of object instances inside the container.
        :param spacing: Tuple indicating the space between objects (for grid-like patterns).
        :param material_override: Optional ObjectProperties instance or dict that overrides individual object materials.
        """
        self.objects = objects
        self.spacing = spacing

        # Convert material_override from dict to ObjectProperties if needed
        if isinstance(material_override, dict):
            self.material_override = ObjectProperties(
                albedo=tuple(material_override.get("albedo", [1.0, 1.0, 1.0])),
                metallic=material_override.get("metallic", 0.0),
                roughness=material_override.get("roughness", 0.5),
                ao=material_override.get("ao", 1.0)
            )
        else:
            self.material_override = material_override

        # Apply material override to all objects if provided
        self.apply_material_override()

    def apply_material_override(self):
        """Apply material override to each object in the container if defined."""
        if self.material_override:
            for obj in self.objects:
                obj.properties.albedo = self.material_override.albedo
                obj.properties.metallic = self.material_override.metallic
                obj.properties.roughness = self.material_override.roughness
                obj.properties.ao = self.material_override.ao


    def arrange_objects(self):
        """Arrange objects in space according to the container's layout. Must be implemented by subclasses."""
        raise NotImplementedError

    def draw(self, shader):
        """Draw all objects in the container."""
        for obj in self.objects:
            obj.draw(shader)

    def animate(self, delta_time):
        """Animate all objects in the container."""
        for obj in self.objects:
            obj.animate(delta_time)


class GridContainer(Container):
    def __init__(self, objects, rows, columns, spacing=(2.0, 2.0, 0.0), material_override=None):
        """
        GridContainer for arranging objects in a grid pattern.

        :param rows: Number of rows in the grid.
        :param columns: Number of columns in the grid.
        """
        super().__init__(objects, spacing, material_override)
        self.rows = rows
        self.columns = columns
        self.arrange_objects()

    def arrange_objects(self):
        """Arrange objects in a grid pattern."""
        index = 0
        for row in range(self.rows):
            for col in range(self.columns):
                if index >= len(self.objects):
                    return
                obj = self.objects[index]
                obj.position = np.array([col * self.spacing[0], row * self.spacing[1], 0.0], dtype=np.float32)
                index += 1

class CircularContainer(Container):
    def __init__(self, objects, radius, material_override=None):
        """
        CircularContainer for arranging objects in a circular pattern.

        :param radius: Radius of the circle.
        """
        super().__init__(objects, material_override=material_override)
        self.radius = radius
        self.arrange_objects()

    def arrange_objects(self):
        """Arrange objects in a circular pattern."""
        num_objects = len(self.objects)  # Use the length of objects, not an external num_objects parameter.
        for i, obj in enumerate(self.objects):
            angle = 2 * np.pi * i / num_objects
            x = self.radius * np.cos(angle)
            y = self.radius * np.sin(angle)
            obj.position = np.array([x, y, 0.0])

class SpiralContainer(Container):
    def __init__(self, objects, radius_start, radius_end, spiral_turns, material_override=None):
        """
        SpiralContainer for arranging objects in a spiral pattern.

        :param radius_start: Starting radius of the spiral.
        :param radius_end: Ending radius of the spiral.
        :param spiral_turns: Number of turns in the spiral.
        """
        super().__init__(objects, material_override=material_override)
        self.radius_start = radius_start
        self.radius_end = radius_end
        self.spiral_turns = spiral_turns
        self.arrange_objects()

    def arrange_objects(self):
        """Arrange objects in a spiral pattern."""
        num_objects = len(self.objects)  # Use the actual number of objects passed to the container.
        radius_range = self.radius_end - self.radius_start
        for i, obj in enumerate(self.objects):
            t = i / (num_objects - 1)  # Parameter t from 0 to 1
            angle = 2 * np.pi * self.spiral_turns * t
            radius = self.radius_start + t * radius_range
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            obj.position = np.array([x, y, 0.0])
