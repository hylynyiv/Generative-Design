import json
from objects import ObjectFactory, ObjectProperties
from container import GridContainer, CircularContainer, SpiralContainer
from light import Light
from camera import Camera
import numpy as np

class Genesis:
    def __init__(self, config_file):
        self.config_file = config_file
        self.elements = {
            "camera": None,
            "lights": [],
            "objects": []
        }

    def load(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        # Load the camera
        if "camera" in config["scene"]:
            self.elements["camera"] = self.create_camera(config["scene"]["camera"])

        # Load lights
        for light_config in config["scene"].get("lights", []):
            self.elements["lights"].append(self.create_light(light_config))

        # Load individual objects
        for obj_config in config["scene"].get("objects", []):
            obj = self.create_object(obj_config)
            self.elements["objects"].append(obj)

        # Load containers
        if "grid_container" in config["scene"]:
            self.elements["objects"].extend(self.create_container(config["scene"]["grid_container"], GridContainer))

        if "circular_container" in config["scene"]:
            self.elements["objects"].extend(self.create_container(config["scene"]["circular_container"], CircularContainer))

        if "spiral_container" in config["scene"]:
            self.elements["objects"].extend(self.create_container(config["scene"]["spiral_container"], SpiralContainer))

        # Handle animations (if needed, to attach to objects)
        if "animations" in config["scene"]:
            self.apply_animations(config["scene"]["animations"])

    def create_camera(self, config):
        return Camera(
            position=config["position"],
            look_at=config["look_at"],
            up_vector=config["up_vector"],
            field_of_view=config["field_of_view"],
            near_clip=config["near_clip"],
            far_clip=config["far_clip"]
        )

    def create_light(self, config):
        light_type = config["type"]
        if light_type == "point":
            return Light(position=np.array(config["position"], dtype=np.float32), color=np.array(config["color"], dtype=np.float32), intensity=config["intensity"], light_type="point")
        elif light_type == "directional":
            return Light(direction=np.array(config["direction"], dtype=np.float32), color=np.array(config["color"], dtype=np.float32), intensity=config["intensity"], light_type="directional")


    def create_object(self, config):
        properties = ObjectProperties(
            albedo=tuple(config["properties"].get("albedo", (1.0, 1.0, 1.0))),
            metallic=config["properties"].get("metallic", 0.0),
            roughness=config["properties"].get("roughness", 0.5),
            ao=config["properties"].get("ao", 1.0),
            rotation_speed=tuple(config["properties"].get("rotation_speed", (0.0, 0.0, 0.0))),
            movement_speed=tuple(config["properties"].get("movement_speed", (0.0, 0.0, 0.0))),
            scale_speed=tuple(config["properties"].get("scale_speed", (0.0, 0.0, 0.0))),
            bounds=config["properties"].get("bounds")
        )

        texture_maps = config.get("texture_maps", {})

        # Generate a unique name for the object or take it from the config if present
        name = config.get("name", f"{config['type']}_{len(self.elements['objects'])}")

        # Extract shape-specific parameters like radius, lat_steps, etc.
        shape_specific_params = {}
        if "radius" in config:
            shape_specific_params["radius"] = config["radius"]
        if "lat_steps" in config:
            shape_specific_params["lat_steps"] = config["lat_steps"]
        if "lon_steps" in config:
            shape_specific_params["lon_steps"] = config["lon_steps"]
        # Add more shape-specific parameters as needed

        # Use the factory to create the object
        obj = ObjectFactory.create_object(
            shape_type=config["type"],
            properties=properties,
            **shape_specific_params,
            **texture_maps  # If textures are provided
        )

        # Assign the name to the object
        obj.name = name

        # Return the created object
        return obj


    def create_container(self, config, container_class):
        # Extract material override if present
        material_override = config.get("material_override")

        # List of objects defined within the container
        objects = [self.create_object(obj_config) for obj_config in config["objects"]]

        # Create a copy of the config and remove unwanted keys like 'pattern' and 'objects'
        config_copy = {k: v for k, v in config.items() if k not in ["material_override", "objects", "num_objects", "pattern"]}

        # Instantiate the container class (GridContainer, CircularContainer, SpiralContainer)
        container = container_class(
            objects=objects,
            material_override=material_override,
            **config_copy  # Pass remaining config (columns, rows, radius, etc.)
        )

        return container.objects  # Return the arranged objects



    def apply_animations(self, animations_config):
        """Attach animations to objects from the animation config."""
        for animation_config in animations_config:
            obj_name = animation_config["object"]
            keyframes = animation_config["keyframes"]

            # Find the object in the scene and attach the animation (pseudo-code)
            for obj in self.elements["objects"]:
                if obj.name == obj_name:
                    obj.attach_animation(keyframes)

    def get_elements(self):
        return self.elements
