#!/usr/bin/env python

#################################################
## RSU | OBU | AU
#################################################

#------------------------------------------------
# node type
#------------------------------------------------
rsu_node = 1
obu_node = 2
au_node = 3

#------------------------------------------------
# Node sub_types
#------------------------------------------------
# RSU : 'tls' | 'toll' | 'park_entry' | <other...>
rsu_sub_type = 'tls'
# OBU : 'car' | 'truck' | 'police' | 'emergency' | 'bus' | 'bike' | <other...>
obu_sub_type1 = 'car'
obu_sub_type2 = 'emergency'

#################################################
## PHYSICAL PROPERTIES
#################################################
#------------------------------------------------
# Antennas range
#------------------------------------------------
rsu_range = 4000
obu_range = 3000
au_range = 1000



#################################################
## MAP - 
#################################################
#------------------------------------------------
# Road network
# ------------------------------------------------
#road_net = {
#    'h_road': {'h1': {'x_in': int(-size_x / 2), 'y_in': 0, 'x_out': int(size_x / 2), 'y_out': 0},
#               'h2': {'x_in': int(-size_x / 2), 'y_in': int(size_y / 4), 'x_out': int(size_x / 2), 'y_out': int(size_y / 4)},
#    },
#    'v_road': {'v1': {'x_in': 0, 'y_in': int(-size_y / 2), 'x_out': 0, 'y_out': int(size_y / 2)},
#              'v2': {'x_in': 0, 'y_in': int(-size_y / 4), 'x_out': 0, 'y_out': int(size_y / 4)}
#    }
#}

#------------------------------------------------
# Virtual map
# ------------------------------------------------
map = {"1":{'type': rsu_node, 'sub_type': rsu_sub_type, 'x':1000, 'y':0,  'status': 'inactive', 'num_tls': 1,
             "tls_groups": {
                1: {"state": "red", "start": 0, "end": 1}
             },
            "movement": {
                1: {"direction": "S", "pedestrian_detection": False}
            }
        },
        "2":{'type': rsu_node, 'sub_type': rsu_sub_type, 'x':0, 'y':600,  'status': 'inactive', 'num_tls': 2,
             "tls_groups": {
                1: {"state": "red", "start": 0, "end": 1}, 
                2: {"state": "green","start": 0, "end": 1}
             },
            "movement": {
                1: {"direction": "S", "pedestrian_detection": True}, 
                2: {"direction": "N", "pedestrian_detection": True}
            }
        },
        "3":{'type': rsu_node,  'sub_type': rsu_sub_type, 'x':-600, 'y':0,  'status': 'inactive', 'num_tls':2,
             "tls_groups": {
                1: {"state": "red", "start": 0, "end": 1}, 
                2: {"state": "red","start": 0, "end": 1}
             },
            "movement": {
                1: {"direction": "E", "pedestrian_detection": True}, 
                2: {"direction": "O", "pedestrian_detection": True}
            }
        },
        "4":{'type': rsu_node,  'sub_type': rsu_sub_type, 'x':1000, 'y':0,  'status': 'inactive', 'num_tls':4,
             "tls_groups": {
                1: {"state": "red",  "start": 0, "end": 1}, 
                2: {"state": "red",  "start": 0, "end": 1},
                3: {"state": "yellow", "start": 0, "end": 1}, 
                4: {"state": "yellow", "start": 0, "end": 1}
             },
            "movement": {
                1: {"direction": "E", "pedestrian_detection": False}, 
                2: {"direction": "O", "pedestrian_detection": False},
                3: {"direction": "N", "pedestrian_detection": False}, 
                4: {"direction": "S", "pedestrian_detection": False}
            }
        },
       "5":{'type':  obu_node,  'sub_type': obu_sub_type1, 'x': 1000,  'y': 300,    'speed':30,   'direction':'f',  'heading':'S',  'status': 'inactive'},
       "6":{'type':  obu_node,  'sub_type': obu_sub_type1, 'x': 100,  'y':  0,    'speed': 50,   'direction':'f',  'heading':'E',  'status': 'inactive'},
       "7":{'type':  obu_node,  'sub_type': obu_sub_type1, 'x':   1000,  'y':1000,    'speed':100,   'direction':'f',  'heading':'S',  'status': 'inactive'},
       "8":{'type':  obu_node,  'sub_type': obu_sub_type2, 'x': 1000,  'y':   1000,    'speed':100,   'direction':'f',  'heading':'S',  'status': 'inactive', 'plus_info': 'emergency on'},
       "9":{'type':  obu_node,  'sub_type': obu_sub_type1, 'x':  700,  'y':   25,    'speed':50,   'direction':'f',  'heading':'O',  'status': 'inactive'},
       "10":{'type': obu_node,  'sub_type': obu_sub_type1, 'x':-1000,   'y': -25,    'speed':100,   'direction':'f',  'heading':'E',  'status': 'inactive'}}


#################################################
## VISUALIZATION DASHBOARD
#################################################
visual = 0
size_x = 8000
size_y = 8000

def print_tls_directions(map_data):
    print("----------------- MAPA ----------------- \n")
    for node_id, node_data in map_data.items():
        if node_data['type'] == rsu_node:  # Filtra apenas os nós do tipo RSU
            
            print(f"RSU Node ID: {node_id}")
            tls_groups = node_data.get("tls_groups", {})
            movements = node_data.get("movement", {})
            
            for tls_id, tls_data in tls_groups.items():
                direction = movements.get(tls_id, {}).get("direction", "Unknown")
                print(f"  TLS ID: {tls_id} - State: {tls_data['state']} - Direction: {direction}")
            print("-" * 40)

# Chamando a função para o mapa fornecido
print_tls_directions(map)
