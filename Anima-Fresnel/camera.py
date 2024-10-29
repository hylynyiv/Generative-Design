# import pyrr
#
# class Camera:
#     def __init__(self, position, target, up, fov=45.0, aspect_ratio=16/9, near_clip=0.1, far_clip=100.0):
#         self.position = pyrr.Vector3(position)
#         self.target = pyrr.Vector3(target)
#         self.up = pyrr.Vector3(up)
#         self.fov = fov
#         self.aspect_ratio = aspect_ratio
#         self.near_clip = near_clip
#         self.far_clip = far_clip
#
#     def get_view_matrix(self):
#         return pyrr.matrix44.create_look_at(self.position, self.target, self.up)
#
#     def get_projection_matrix(self):
#         return pyrr.matrix44.create_perspective_projection(self.fov, self.aspect_ratio, self.near_clip, self.far_clip)

class Camera:
    def __init__(self, position, look_at, up_vector, field_of_view, near_clip, far_clip):
        self.position = position
        self.look_at = look_at
        self.up_vector = up_vector
        self.field_of_view = field_of_view
        self.near_clip = near_clip
        self.far_clip = far_clip

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(
            eye=self.position, target=self.look_at, up=self.up_vector, dtype=np.float32
        )
