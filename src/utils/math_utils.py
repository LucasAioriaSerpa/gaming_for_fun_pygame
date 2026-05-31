
def normalize_vector(dx: float, dy: float) -> tuple[float, float]:
    if dx != 0 and dy != 0: return dx * 0.7071, dy * 0.7071
    return dx, dy
