

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


class Worker:
    def __init__(self, id, x, y, health, resource, t_location):
        self.id = 
        self.position = {x: x, y: y}
        self.health = health
        self.resource = resource     # Number of resources carried
        self.target_resource = -1    # ID of target resource
        self.target_location = t_location # Location of target
        self.path_to_target = []     # Path to target resource
