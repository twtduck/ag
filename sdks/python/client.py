#!/usr/bin/python

import sys
import json
import random

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
            print(json.dumps(json_data, indent=4, sort_keys=True))
            game.get_calc_move(json_data)
            print("Turn " + str(json_data["turn"]) + " complete")
            response = game.get_random_move(json_data).encode()
            self.wfile.write(response)

class Map:

    def __init__(self):
        self.width = -1
        self.height = -1
    def create_map(self, map_width, map_height):
        self.width = map_width * 2 
        self.height = map_height * 2 
        # Initialize map with unknown for all tiles
        self.grid = [[-2 for x in range(self.width)] for y in range(self.height)]


    def add_tile(self, tilex, tiley, blocked, resource, enemies):
        state = -2
        if( enemies != [] ):
            state = -4
        elif( resource != -1 ):
            state = resource
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


class Game:
    def __init__(self):
        self.units = set() # set of unique unit ids
        self.directions = ['N', 'S', 'E', 'W']
        self.map = Map()
        self.first_turn = True

    def get_random_move(self, json_data):
        units = set([unit['id'] for unit in json_data['unit_updates'] if unit['type'] != 'base'])
        self.units |= units # add any additional ids we encounter
        unit = random.choice(tuple(self.units))
        direction = random.choice(self.directions)
        move = 'MOVE'
        command = {"commands": [{"command": move, "unit": unit, "dir": direction}]}
        response = json.dumps(command, separators=(',',':')) + '\n'
        return response
    
    def get_calc_move(self, json_data):
        if( self.first_turn ):
            self.map.create_map(json_data["game_info"]["map_width"], json_data["game_info"]["map_height"])
            self.first_turn = False
        for update_tile in json_data["tile_updates"]:
            if( update_tile["visible"] ):
                resource_id = -1
                if( update_tile["resources"] != None ):
                    resource_id = update_tile["resources"]["id"]
                self.map.add_tile(update_tile["x"], update_tile["y"], update_tile["blocked"], resource_id, update_tile["units"])
        self.map.print_map_data()


    

if __name__ == "__main__":
    port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 9090
    host = '127.0.0.1'

    server = ss.TCPServer((host, port), NetworkHandler)
    print("listening on {}:{}".format(host, port))
    server.serve_forever()
