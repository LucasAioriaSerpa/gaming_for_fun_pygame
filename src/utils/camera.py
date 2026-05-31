
class Camera:
    def __init__(self, internal_width: int, internal_height: int):
        self.x      = 0.0
        self.y      = 0.0
        self.width  = internal_width
        self.height = internal_height
        
    def follow(self, target_x: float, target_y: float):
        self.x += (target_x - self.x - self.width // 2) / 10
        self.y += (target_y - self.y - self.height // 2) / 10
