#!/usr/bin/python

import sys
import json
import random
import heapq
import queue

if (sys.version_info > (3, 0)):
    print("Python 3.X detected")
    import socketserver as ss
else:
    print("Python 2.X detected")
    import SocketServer as ss

class NetworkHandler(ss.StreamRequestHandler):
    def handle(self):
        game = Game()

        while True:
            data = self.rfile.readline().decode() # reads until '\n' encountered
            json_data = json.loads(str(data))
            # uncomment the following line to see pretty-printed data
            #print(json.dumps(json_data, indent=4, sort_keys=True))
            game.update(json_data)
#            game.update_map(json_data)
            print("Turn " + str(json_data["turn"]) + " complete")
            #response = game.get_random_move(json_data).encode()
            response = game.get_commands().encode()
            self.wfile.write(response)

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

class Map:

    def __init__(self):
        self.width = -1
        self.height = -1
        self.resources = {}

    def create_map(self, map_width, map_height):
        self.width = map_width * 2 
        self.height = map_height * 2 
        # Initialize map with unknown for all tiles
        self.grid = [[-2 for x in range(self.width)] for y in range(self.height)]

    def neighbors(self, position):
        (x, y) = position
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
        if (x + y) % 2 == 0: results.reverse() # aesthetics
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results

    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    # A* Path finding from start to goal. Returns an array of directions to get there. 
    def path(self, start, goal):
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
                # Check if neighbor position is passable
                if (self.grid[next[0]][next[1]] != -1):
                    continue
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            direction = self.get_direction(current, came_from[current])
            path.append(current)
        path.append(start)
        path.reverse()
        return path

    def get_direction(self, start, goal):
        if (start[0] == goal[0]):
            if (goal[1] > start[0]):
                return "S"
            else:
                return "N"
        else:
            if (goal[0] > start[0]):
                return "E"
            else:
                return "W"

    def add_tile(self, tilex, tiley, blocked, resource, enemies):
        state = -2
        if( enemies != [] ):
            state = -4
        elif( resource != -1 ):
            state = resource
            self.resources[resource] = (tilex, tiley)
        elif( blocked == True ):
            state = -3
        else:
            # Passable
            state = -1
        self.grid[tilex + self.width // 2][tiley + self.height // 2] = state

    def print_map_data(self):
        print("Map width: " + str(self.width))
        print("Map height: " + str(self.height))
        for y in range(self.height):
            for x in range(self.width) :
               print("[" + str(self.grid[x][y]) + "] ", end='')
            print()
    
    def get_resources(self):
        return self.resources 


class Game:
    def __init__(self):
        self.units = set() # set of unique unit ids
        self.directions = ['N', 'S', 'E', 'W']
        self.map = Map()
        self.first_turn = True
        self.workers = set() # set of unique worker ids
        self.worker_info = {}
        self.commands = queue.Queue()
        self.nearest_id = -1

    def update(self, json_data):
        self.update_map(json_data)
        self.move_workers(json_data)
        self.create_units(json_data)
    
    def get_random_move(self, json_data):
        units = set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] != 'base'])
        self.units |= units # add any additional ids we encounter
        unit = random.choice(tuple(self.units))
        direction = random.choice(self.directions)
        move = 'MOVE'
        command = {"commands": [{"command": move, "unit": unit, "dir": direction}]}
        response = json.dumps(command, separators=(',',':')) + '\n'
        return response
    
    def update_map(self, json_data):
        if( self.first_turn ):
            self.map.create_map(json_data["game_info"]["map_width"], json_data["game_info"]["map_height"])
            self.first_turn = False
        for update_tile in json_data["tile_updates"]:
            if( update_tile["visible"] ):
                resource_id = -1
                if( update_tile["resources"] != None ):
                    resource_id = update_tile["resources"]["id"]
                self.map.add_tile(update_tile["x"], update_tile["y"], update_tile["blocked"], resource_id, update_tile["units"])
        #self.map.print_map_data()        

    def get_nearest_resource(self):
        resources = self.map.get_resources()
        nearest = -1
        for resource in resources:
            next_dist = len(self.map.path( (0, 0), resources[resource] ))
            if (nearest == -1) or (next_dist < nearest):
                nearest = next_dist
                self.nearest_id = resource

    def move_workers(self, json_data):
        # get list of resources (from map)
        resources = self.map.get_resources()

        # get list of workers (from json) 
        workers = set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] == 'worker'])
        print("\n\n\n\n\n\n\n")
        print("Workers: ", workers)

        self.workers |= workers # add any additional ids we encounter
        
        # if worker is assigned to a resource, send it to that resource

        for worker in self.workers:
            #worker is a tuple (assignment, returning)
            if worker not in self.worker_info:
                worker_info[worker] = (False, self.map.path( (worker[x], worker[y]), resources[self.nearest_id]))  # (target_resource, returning_to_base, path)
            (returning, path) = worker_info[worker]
            if( not returning ):
                # send worker to resource
                next_dir = path.pop(0)
                if (len(path) == 0):
                    # Gather
                    self.commands.push('command: "GATHER", unit: { worker }, dir: { next_dir }')
                    # Update list to return 
                    new_path = self.map.path( (worker[x], worker[y]), (0, 0) )
                    worker_info[worker] = (True, new_path)
                else:
                    # Move 
                    self.commands.push('command: "MOVE", unit: { worker }, dir: { next_dir }')

        # otherwise, check if there is a resource that the worker is nearby that doesn't have a worker assigned to it
        # if not, explore

    def create_units(self, json_data):
        # get list of existing units, and count their types
        num_workers = len(set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] == 'worker']))
        num_tanks = len(set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] == 'tank']))
        num_scouts = len(set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] == 'worker']))
        
        # get queue of units to create
        create_queue = Queue()
        while (num_workers < 6):
            create_queue.push("worker")
            num_workers += 1
        while (num_scouts < 2):
            create_queue.push("scout")
            num_scouts += 1
        while (num_tanks < 3):
            create_queue.push("tank")
            num_tanks += 1
        while (num_workers < 9):
            create_queue.push("worker")
            num_workers += 1
            
        # send that queue to the server
        self.commands.push("command: \"CREATE\", type: \"" + create_queue.pop() + "\"")
            
    def get_commands(self):
        commands = []
        while(not(self.commands.empty())):
            commands.append({commands.pop()})
        command = {"commands": commands}
        response = json.dumps(command, separators=(',',':')) + '\n'
        return response

if __name__ == "__main__":
    port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 9090
    host = '127.0.0.1'

    server = ss.TCPServer((host, port), NetworkHandler)
    print("listening on {}:{}".format(host, port))
    server.serve_forever()
