#!/usr/bin/env python
# #####################################################################################################
# SENDING/RECEIVING APPLICATION THREADS - add your business logic here!
# Note: you can use a single thread, if you prefer, but be carefully when dealing with concurrency.
#######################################################################################################
from socket import MsgFlag
import time, math, threading
import ITS_maps as map
from application.message_handler import *
from application.obu_commands import *
import application.app_config as app_conf
import application.app_config_obu as app_obu_conf

den_txd = threading.Condition()

counter = 0

#-----------------------------------------------------------------------------------------
# Thread: application transmission. In this example user triggers CA and DEN messages. 
#		CA message generation requires the sender identification and the inter-generation time.
#		DEN message generarion requires the sender identification, and all the parameters of the event.
#		Note: the sender is needed if you run multiple instances in the same system to allow the 
#             application to identify the intended recipiient of the user message.
#		TIPS: i) You may want to add more data to the messages, by adding more fields to the dictionary
# 			  ii)  user interface is useful to allow the user to control your system execution.
#-----------------------------------------------------------------------------------------

def obu_application_txd(obd_2_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue, rsu_interface):

    while not start_flag.isSet():
        time.sleep(1)
    if (app_conf.debug_sys):
        print('STATUS: Ready to start - THREAD: obu_application_txd - NODE: {}'.format(obd_2_interface["node_id"]), '\n')

    time.sleep(app_obu_conf.warm_up_time)
    ca_service_txd_queue.put(int(app_rsu_conf.ca_generation_interval))
    if (app_conf.debug_app_ca):
        print('obu_application - CA message triggered with generation interval ', app_obu_conf.ca_generation_interval)

    if (app_conf.debug_app_den):
        print('obu_application_txd - DEN message sent (safety critical): ', safety_critical_event)

#-----------------------------------------------------------------------------------------
# Thread: application reception. In this example it receives CA and DEN messages. 
# 		Incoming messages are send to the user and my_system thread, where the logic of your system must be executed
# 		CA messages have 1-hop transmission and DEN messages may have multiple hops and validity time
#		Note: current version does not support multihop and time validity. 
#		TIPS: i) if you want to add multihop, you need to change the thread structure and add 
#       		the den_service_txd_queue so that the node can relay the DEN message. 
# 				Do not forget to this also at IST_core.py
#-----------------------------------------------------------------------------------------
def obu_application_rxd(obd_2_interface, start_flag, services_rxd_queue, my_system_rxd_queue, rsu_interface):

    while not start_flag.isSet():
        time.sleep (1)
    if (app_conf.debug_sys):
        print('STATUS: Ready to start - THREAD: obu_application_rxd - NODE: {}'.format(obd_2_interface["node_id"]),'\n')

    while True :
        msg_rxd=services_rxd_queue.get()
        
        #print('\n Message received typeeeeeeeeeeeeeeeeeeeeeeeeee: ', msg_rxd['msg_type'])
        if (msg_rxd['msg_type']=="SPAT") and (obd_2_interface['node_id'] != msg_rxd['node']):
            if (app_conf.debug_app_spat):
                print ('\n....>obu_application_rxd - spat messsage received ',msg_rxd)
            my_system_rxd_queue.put(msg_rxd)
        elif (msg_rxd['msg_type']=="CA") and (obd_2_interface['node_id'] != msg_rxd['node']):
            if (app_conf.debug_app_ca):
                print ('\n....>obu_application_rxd - ca messsage received ',msg_rxd)
            my_system_rxd_queue.put(msg_rxd)
        elif (msg_rxd['msg_type']=="DEN") and (obd_2_interface['node_id'] != msg_rxd['node']):
            if (app_conf.debug_app_den):
                print ('\n....>obu_application_rxd - den messsage received ',msg_rxd)
            my_system_rxd_queue.put(msg_rxd)


#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control (test of the functions needed to control your car)
# The car implements a finite state machine. This means that the commands must be executed in the right other.
# Initial state: closed
# closed   - > opened                       opened -> closed | ready:                   ready ->  not_ready | moving   
# not_ready -> stopped | ready| closed      moving -> stopped | not_ready | closed      stopped -> moving not_ready | closed
#-----------------------------------------------------------------------------------------
def obu_system(obd_2_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue, den_service_txd_queue, rsu_interface):
	
    import threading

    def calculate_distance(light_heading, car_x, car_y, light_x, light_y):
        """Calculate Euclidean distance."""
        #Calculate euclidean distance between two points for each direction
        # the result will be positive 
        if light_heading == 'N':
              return light_y - car_y
        elif light_heading == 'S':
             return car_y - light_y
        elif light_heading == 'E':
             return light_x - car_x
        elif light_heading == 'O':
             return car_x - light_x
            

    stopping_distance = 50  # Define stopping distance in meters
    traffic_light_states = {}  # Store the last known state for each intersection
   

    def handle_light_state(intersection_id, signal_state):

        global counter
       
        """Handle traffic light behavior based on the signal state."""
        #print('\n', coordinates['x'], coordinates['y'])
        distance_to_light = calculate_distance(light_heading, coordinates['x'], coordinates['y'], light_x, light_y)
        print(f"** Distance to traffic light from the car = {distance_to_light} m **\n")
        if signal_state == 'red':
            
            if distance_to_light > stopping_distance:
                #print('Coordinates of OBU', coordinates)
                if obd_2_interface['speed'] > 20:
                    print(f"** RED - Slowing down **\n")
                    car_move_slower(movement_control_txd_queue)
                    print (f"** VELOCIDADE = {obd_2_interface['speed']} **\n")
                    counter +=1
                    # print('counter incrementado 111111: ', counter)
                else:
                     print(f"** RED - preparing to stop **\n")
                     if obd_2_interface['speed'] == 0:
                        car_move_forward(movement_control_txd_queue)
                        for i in range(counter):
                            car_move_faster(movement_control_txd_queue)
                        counter = 0
                     else:
                        obd_2_interface['speed'] = 20

                return 0
            else:
                print(f"** RED - Stopping **\n")
                stop_car(movement_control_txd_queue)
                return 1
        elif signal_state == 'yellow':
            print(f"** YELLOW. Preparing to stop **\n")
            if obd_2_interface['speed'] > 40:
                car_move_very_slow(movement_control_txd_queue)
                counter +=3
                # print('counter incrementado 33333333333: ', counter)
            return 0
        
        elif signal_state == 'green':
            print(f"** GREEN - Proceeding forward **\n")
            if obd_2_interface['speed'] == 0:
                car_move_forward(movement_control_txd_queue)
            # print('counter', counter)
            for i in range(counter):
                car_move_faster(movement_control_txd_queue)

            counter = 0  # Reset the counter after handling green

            return 0

    def periodic_check():
        """Periodically check the distance to traffic lights and enforce behavior."""
        flag = 0
        while True:
            for intersection_id, light_info in traffic_light_states.items():
                signal_state, light_x, light_y = light_info
                car_x, car_y, _ = position_read(coordinates)
                distance_to_light = calculate_distance(light_heading, car_x, car_y, light_x, light_y)

                if signal_state == 'red':
                    if handle_light_state(intersection_id, signal_state):
                         #print('Coordinates of OBU', coordinates)
                         flag = 1
                         break
                				 
            time.sleep(0.5)  # Check every 0.5 seconds
            if flag == 1:
                break
            
    # Start periodic checking in a separate thread
    threading.Thread(target=periodic_check, daemon=True).start()

    while not start_flag.isSet():
        time.sleep(1)
    if app_conf.debug_sys:
        print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(obd_2_interface["node_id"]), '\n')

    if obd_2_interface["node_id"] == '8':
        print(f"** AMBULANCIA INICIOU A MARCHA PARA {obd_2_interface['heading']} **\n")
    else:
        print(f"** CARRO INICIOU A MARCHA PARA {obd_2_interface['heading']} **\n")
    # Initialize the car
    open_car(movement_control_txd_queue)
    turn_on_car(movement_control_txd_queue)
    car_move_forward(movement_control_txd_queue)
    
    print("\n")
    traffic_light_coordinates = {key: (value['x'], value['y']) for key, value in map.map.items() if value['type'] == map.rsu_node}

    while True:
        msg_rxd = my_system_rxd_queue.get()
        x = msg_rxd['pos_x']
        y = msg_rxd['pos_y']
        my_x = coordinates['x']
        my_y = coordinates['y']

        distance = calculate_distance(obd_2_interface['heading'], my_x, my_y, x, y)
        
        if obd_2_interface["node_id"] == '8':  # Verifica se é ambulância
            emergency_event = trigger_event(map.obu_node, 1, 'start')  # Event: emergency_vehicle_approaching
            den_service_txd_queue.put(emergency_event)
            print("** EMERGENCY EVENT - DEN sent **\n")
            
        print("** ---------Info about OBU car--------- **\n")
        print(f" OBU coordinates: x = {my_x} y = {my_y}")
        print(f" OBU speed: {obd_2_interface['speed']} \n")
   
        if msg_rxd['msg_type'] == 'SPAT':
            
            intersection = msg_rxd.get('intersection', {})
            intersection_id = intersection.get('intersectionID')
            tls_group = intersection.get('signalGroups', {})
            movement = intersection.get('movement', {})

            aligned = False  # Flag para verificar se encontramos um alinhamento
           
            # Iterar sobre todos os IDs de movimento no semáforo
            for key, value in movement.items():
                light_heading = value.get('direction', 'unknown')
                
                if light_heading == obd_2_interface['heading']:
                    # Entramos no alinhamento correto
                    aligned = True
                    # print(f"ENTREI NO IF -> Minha direção = {obd_2_interface['heading']} e a direção do semáforo = {light_heading}")

                    signal_state = tls_group.get(key, {}).get('state', 'unknown')
                    light_x, light_y = traffic_light_coordinates.get(intersection_id, (None, None))

                    if light_x is None or light_y is None:
                        print(f"Invalid traffic light coordinates for intersection ID {intersection_id}.")
                        continue

                    car_x, car_y, _ = position_read(coordinates)
                    distance_to_light = calculate_distance(light_heading, car_x, car_y, light_x, light_y)

                    if obd_2_interface["node_id"] == '8':
                        print(f"Distance from the emergency vehicle to the traffic light: {distance_to_light}\n" )
                    else:
                        print(f"Distance from a normal vehicle to the traffic light: {distance_to_light}\n" )

                    if distance_to_light > 0 :
                        # Atualizar o estado do semáforo para verificação periódica
                        if obd_2_interface["node_id"] != '8':
                            
                            traffic_light_states[intersection_id] = (signal_state, light_x, light_y)
                            # Tomar ações imediatas com base no estado atual
                            handle_light_state(intersection_id, signal_state)
                    else:
                        print(" ** SEMAFORO ULTRAPASSADO!! ** \n")
                    break  # Não precisamos verificar mais após encontrar alinhamento

            # Caso nenhuma direção esteja alinhada, tratamos como "não alinhado"
            if not aligned:
                print("** Traffic light and car directions are not aligned!!!! **\n")
            
        elif (msg_rxd['msg_type'] == 'CA'):
                
                print("**---------Info about the OTHER car---------**\n")
                print(f"OTHER car coordinates: x = {x} y = {y}")
                print(f"OTHER car speed: {msg_rxd['speed']}\n")
                
                # print(f"Distance between vehicles: {distance}\n" )

                current_speed = obd_2_interface['speed']
              
                if msg_rxd['heading'] == obd_2_interface['heading']:
                    # print('msg_rxd', msg_rxd)
                    if (distance > 0):
                        if (distance <= app_obu_conf.safety_distance) and (distance > app_obu_conf.emergency_distance) and (distance > app_obu_conf.crash_iminent):
                            if (app_conf.debug_app) or (app_conf.debug_obu):
                                print ('\nObu_system: safety: distance ', int(distance), 'safety distance ', app_obu_conf.safety_distance, 'emergency ', app_obu_conf.emergency_distance)               
                            
                            if current_speed > msg_rxd['speed']:
                                car_move_slower(movement_control_txd_queue) 
                            else:
                                car_move_faster(movement_control_txd_queue)

                        elif (distance > app_obu_conf.safety_distance and current_speed <= msg_rxd['speed']):
                            car_move_faster(movement_control_txd_queue)
                            
                        elif (distance <= app_obu_conf.emergency_distance) and (distance > app_obu_conf.crash_iminent) and (distance < app_obu_conf.safety_distance):
                            if (app_conf.debug_app) or (app_conf.debug_obu):
                                print ('\nObu_system: emergency: distance ', int(distance), 'safety distance ', app_obu_conf.safety_distance, 'emergency ', app_obu_conf.emergency_distance)
                            car_move_very_slow(movement_control_txd_queue)

                        elif (distance <= app_obu_conf.crash_iminent) and (distance < app_obu_conf.emergency_distance) and (distance < app_obu_conf.safety_distance):
                            if app_conf.debug_app or app_conf.debug_obu:
                                print('distance', int(distance), 'safety distance', app_obu_conf.safety_distance, 'emergency', app_obu_conf.emergency_distance)
                            # print ('Obu_system: ominent crash distance ', int(distance), 'safety distance ', app_obu_conf.safety_distance, 'emergency ', app_obu_conf.emergency_distance)
                            stop_car(movement_control_txd_queue)
                        
                            with den_txd:
                                den_txd.notify() 
                                print("** SAFETY CRITICAL WARNING EVENT - DEN sent **\n")
                            safety_critical_event = trigger_event(map.obu_node, 0, 'start')  # Índice 0: safety_critical_warning
                            den_service_txd_queue.put(safety_critical_event)
                    else:
                        print('** The car sending messages is behind me **\n')
                else:
                    print('**The car sending messages is not in the same direction as me **\n')

                
        elif (msg_rxd['msg_type']=='DEN'):
           
            msg_x, msg_y = msg_rxd['pos_x'], msg_rxd['pos_y']
            my_x, my_y = coordinates['x'], coordinates['y']
            current_heading = obd_2_interface['heading']

            if (app_conf.debug_app) or (app_conf.debug_obu):
                print ('\nObu_system: other vehicle detected iminent crash: distance ', int(distance), 'safety distance ', app_obu_conf.safety_distance, 'emergency ', app_obu_conf.emergency_distance)
            if (msg_rxd['node_type'] == obd_2_interface['type'] and (msg_rxd['node'] == '8' or obd_2_interface['node_id'] == '8')):
                
                event = msg_rxd.get('event', {})

                if (event['event_type']=='safety_critical_warning'):
                    car_move_very_fast(movement_control_txd_queue)
                elif (event['event_type']=='emergency_vehicle_approaching'):
                    car_move_faster(movement_control_txd_queue)

            elif (msg_rxd['node_type']==obd_2_interface['type'] and (msg_rxd['node'] != '8' and obd_2_interface['node_id'] != '8')):
               
                # Check alignment and determine direction
                if current_heading in ['N', 'S']:
                    # Check if cars are aligned on the x-axis
                    if my_x == msg_x:
                        if (current_heading == 'N' and my_y > msg_y) or (current_heading == 'S' and my_y < msg_y):
                            print("Cars are moving in the same direction", current_heading)
                            if distance < 0:  # You are the front car 
                                car_move_forward(movement_control_txd_queue)
                                print('** The car stopped because a DEN message indicates a car ahead **\n')
                        else:
                            print("** Cars are moving in opposite directions **\n")
                    else:
                        print("** Cars are not aligned (North-South). **\n")
                elif current_heading in ['E', 'O']:
                    # Check if cars are aligned on the y-axis
                    if my_y == msg_y:
                        if (current_heading == 'E' and my_x < msg_x) or (current_heading == 'O' and my_x > msg_x):
                            print("** Cars are moving in the same direction **\n", current_heading)
                            if distance > 0:  # You are behind the other car
                                stop_car(movement_control_txd_queue)
                                print('** The car stopped because a DEN message indicates a car ahead **\n')
                        else:
                            print("** Cars are moving in opposite directions **\n")
                    else:
                        print("** Cars are not aligned (East-West). **\n")
