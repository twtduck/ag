

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

    def update_path():
        frontier = PriorityQueue()
        frontier.put(self.position, 0)
        came_from[self.position] = None
        cost_so_far[self.position] = 0

        while not frontier.empty():
            current = frontier.get()

            if (current == self.target_location):
                break

            for next in 
        
    def a_star_search(graph, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == goal:
                break
            
            for next in graph.neighbors(current):
                new_cost = cost_so_far[current] + graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        return came_from, cost_so_far