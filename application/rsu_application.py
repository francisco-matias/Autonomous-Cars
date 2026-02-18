#!/usr/bin/env python
# #####################################################################################################
# SENDING/RECEIVING APPLICATION THREADS - add your business logic here!
# Note: you can use a single thread, if you prefer, but be carefully when dealing with concurrency.
#######################################################################################################
from socket import MsgFlag
import time, threading
from application.message_handler import *
import application.app_config as app_conf
import application.app_config_rsu as app_rsu_conf
from application.rsu_commands import *
import ITS_maps as maps

status_update = threading.Condition()
ambulancia = 0

def calculate_distance2(heading, car_x, car_y, light_x, light_y):
        """Calculate Euclidean distance."""
        #Calculate euclidean distance between two points for each direction
        # the result will be positive 
        if heading == 'N':
              return light_y - car_y
        elif heading == 'S':
             return car_y - light_y
        elif heading == 'E':
             return light_x - car_x
        elif heading == 'O':
             return car_x - light_x
        


#-----------------------------------------------------------------------------------------
# Thread: rsu application transmission. In this example user triggers CA and DEN messages. 
#   to be completed, in case RSU sends messages
#        my_system_rxd_queue to send commands/messages to rsu_system
#        ca_service_txd_queue to send CA messages
#        den_service_txd_queue to send DEN messages
#-----------------------------------------------------------------------------------------
def rsu_application_txd(rsu_interface, start_flag,  my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue, spat_service_txd_queue, ivim_service_txd_queue):


     while not start_flag.isSet():
          time.sleep (1)
     if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     
     time.sleep(app_rsu_conf.warm_up_time)

     
     while True:
          #wait for notification of tls status alteration to tramsit a spat message
          with status_update:
              status_update.wait() 
          spat=spat_generation(rsu_interface)
          spat_service_txd_queue.put(spat)
          
          ivim_description = ['vehicle']

          ivim_event = trigger_situation('start')
          for i in range(len(ivim_description)):
               ivim_details = ivim_containers_creation(rsu_interface, ivim_description[i])
               ivim_event.update (ivim_details)
               # if (app_conf.debug_app_ivim):
               #      print ('\nrsu_application_txd - IVIM message send ', ivim_event)
          ivim_service_txd_queue.put(ivim_event)
          # time.sleep(2)

def process_v2v_message(message, rsu_interface, my_system_rxd_queue):
    # Exemplo de processamento de mensagem V2V
    if 'car_id' in message and 'data' in message:
        print(f"Recebida mensagem V2V do carro {message['car_id']} com dados {message['data']}")
        # Pode retransmitir a mensagem ou tomar ações baseadas nos dados
        my_system_rxd_queue.put(message)  # Encaminhar para processamento adicional


# def retransmit_v2v_message(message, retransmit_queue):
#     # Modificar a mensagem conforme necessário
#     retransmit_queue.put(message)  # Retransmitir a mensagem para outras OBUs através da RSU

#-----------------------------------------------------------------------------------------
# Thread: rsu application reception. In this example it does not send ot receive messages
#   to be completed, in case RSU receives messages
#   use: services_rxd_queue to receive messages
#        my_system_rxd_queue to send commands/messages to rsu_system
#-----------------------------------------------------------------------------------------
import queue  # Certifique-se de usar a biblioteca correta

def restore_traffic_lights(tls_group, movement):
    """
    Restaura os semáforos ao funcionamento normal.
    """
    first_lane_tls = dict(list(tls_group.items())[:2])  # Grupo 1: Norte e Sul
    second_lane_tls = dict(list(tls_group.items())[-2:])  # Grupo 2: Leste e Oeste

    # Alternar ciclos: Grupo 1 verde, Grupo 2 vermelho
    for tls_id, tls_data in first_lane_tls.items():
        tls_data['state'] = 'green'  # Configura como verde
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - GREEN ** \n")
    
    for tls_id, tls_data in second_lane_tls.items():
        tls_data['state'] = 'red'  # Configura como vermelho
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - RED ** \n")
    print("-------------------------------------------------------\n")

    time.sleep(app_rsu_conf.tls_timing)  # Temporização antes da transição

    for tls_id, tls_data in first_lane_tls.items():
        tls_data['state'] = 'yellow'  # Configura como amarelo
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - YELLOW ** \n")

    for tls_id, tls_data in second_lane_tls.items():
        tls_data['state'] = 'green'  # Configura como verde
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - GREEN ** \n")
    print("-------------------------------------------------------\n")

    time.sleep(app_rsu_conf.tls_timing)

    for tls_id, tls_data in first_lane_tls.items():
        tls_data['state'] = 'red'  # Configura como vermelho
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - RED ** \n")

    for tls_id, tls_data in second_lane_tls.items():
        tls_data['state'] = 'yellow'  # Configura como amarelo
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - YELLOW ** \n")
    print("-------------------------------------------------------\n")

    time.sleep(app_rsu_conf.tls_timing)

    for tls_id, tls_data in second_lane_tls.items():
        tls_data['state'] = 'red'  # Configura como vermelho
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - RED ** \n")

    for tls_id, tls_data in first_lane_tls.items():
        tls_data['state'] = 'green'  # Configura como verde
        direction = movement.get(tls_id, {}).get("direction", "Unknown")
        # print(f"** Direction: {direction} - GREEN ** \n")
    print("-------------------------------------------------------\n")

def rsu_application_rxd(rsu_interface, start_flag, services_rxd_queue, my_system_rxd_queue, rsu_control_txd_queue):
    while not start_flag.isSet():
        time.sleep(1)
    if app_conf.debug_sys:
        print('STATUS: Ready to start - THREAD: rsu_application_rxd - NODE: {}'.format(rsu_interface["node_id"]), '\n')
    
    intersection_id = "4"  # ID do semáforo
    light_x = int(maps.map[intersection_id]['x'])  # Coordenada X convertida para inteiro
    light_y = int(maps.map[intersection_id]['y'])
    global ambulancia
    passed_lights = 0
    count = 1
    while True:
        # Obter mensagem da fila
        msg_rxd = services_rxd_queue.get()  # Timeout evita travar indefinidamente
        
        if app_conf.debug_app_den:
            print(f"Message received in RSU: {msg_rxd}")
        # Verificar se a mensagem é do tipo "DEN"

        if msg_rxd.get("msg_type") == "DEN":
            
            event = msg_rxd.get("event", {})
            
            # Verificar se o evento é do tipo "emergency_vehicle_approaching"
            if event.get('event_type') == 'emergency_vehicle_approaching':
                heading = msg_rxd.get('heading', None)
                car_x = int(msg_rxd.get('pos_x', 0))  # Converte para inteiro, padrão 0 caso a chave não exista
                car_y = int(msg_rxd.get('pos_y', 0))  # Converte para inteiro, padrão 0 caso a chave não exista

                distance_to_light = calculate_distance2(heading, car_x, car_y, light_x, light_y)
                if (distance_to_light > 0 and distance_to_light < 450):
                        ambulancia = 1
                        if heading:
                            print("-------------------------------------------------------\n")
                            update_traffic_light_priority(rsu_interface, msg_rxd)

                            if heading in ["S", "N"]:  # Ambulância vindo do sul ou norte
                                relevant_directions = ["S", "N"]
                                irrelevant_directions = ["E", "O"]
                            elif heading in ["E", "O"]:  # Ambulância vindo do leste ou oeste
                                relevant_directions = ["E", "O"]
                                irrelevant_directions = ["S", "N"]
                            else:
                                print(f"Unknown direction '{heading}' in DEN message event.")
                                continue

                            # Atualizar o estado dos semáforos
                            for id, signal in rsu_interface.get("tls_group", {}).items():
                                movement = maps.map[rsu_interface["node_id"]]["movement"]
                                signal_direction = movement.get(id, {}).get("direction", "Unknown")

                                # Relevantes -> Verde
                                if signal_direction in relevant_directions:
                                    green_tls(rsu_control_txd_queue, signal_direction, ambulancia)
                                    sem_id(rsu_control_txd_queue, id)
                                    # print(f"** Direction: {signal_direction} - GREEN - priority ** \n")

                                # Irrelevantes -> Amarelo (depois Vermelho com delay)
                                elif signal_direction in irrelevant_directions:
                                    if count <=2:
                                        yellow_tls(rsu_control_txd_queue, signal_direction, ambulancia)
                                        sem_id(rsu_control_txd_queue, id)
                                        count += 1
                                    # print(f"** Direction: {signal_direction} - YELLOW - priority ** \n")
                                    time.sleep(2)  # Delay para troca para vermelho
                                    red_tls(rsu_control_txd_queue, signal_direction, ambulancia)
                                    sem_id(rsu_control_txd_queue, id)
                                    # print(f"** Direction: {signal_direction} - RED - priority ** \n")
                                else:
                                    print(f"Traffic light {id} has an unknown direction: {signal_direction}")
                            print("-------------------------------------------------------\n")    
                elif distance_to_light < 0:
                    
                    passed_lights += 1
                    if passed_lights == 1:
                        print(" ** AMBULÂNCIA PASSOU O SEMÁFORO!! ** \n")
                        print("** Restaurando funcionamento normal dos semáforos!! ** \n")
                        ambulancia = 0
                        
                        # Estado inicial: relevant_directions ficam amarelos
                        for id, signal in rsu_interface.get("tls_group", {}).items():
                            movement = maps.map[rsu_interface["node_id"]]["movement"]
                            signal_direction = movement.get(id, {}).get("direction", "Unknown")
                            
                            # Relevant directions -> Amarelo
                            if signal_direction in relevant_directions:
                                yellow_tls(rsu_control_txd_queue, signal_direction, ambulancia)
                                sem_id(rsu_control_txd_queue, id)
                                # print(f"** Direction: {signal_direction} - YELLOW (Restaurando ciclo) ** \n")
                        
                        # Aguarda transição de amarelo para vermelho
                        time.sleep(2)

                        # Estado inicial: relevant_directions ficam vermelhos, outros ficam verdes
                        for id, signal in rsu_interface.get("tls_group", {}).items():
                            signal_direction = movement.get(id, {}).get("direction", "Unknown")
                            
                            if signal_direction in relevant_directions:
                                red_tls(rsu_control_txd_queue, signal_direction, ambulancia)
                                sem_id(rsu_control_txd_queue, id)
                                # print(f"** Direction: {signal_direction} - RED (Restaurando ciclo) ** \n")
                            elif signal_direction in irrelevant_directions:
                                green_tls(rsu_control_txd_queue, signal_direction, ambulancia)
                                sem_id(rsu_control_txd_queue, id)
                                # print(f"** Direction: {signal_direction} - GREEN (Restaurando ciclo) ** \n")
                        ambulancia = 2

                        break
                       
#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control (test of the functions needed to control your car)
# The car implements a finite state machine. This means that the commands must be executed in the right other.
# Initial state: closed
# closed   - > opened                       opened -> closed | ready:                   ready ->  not_ready | moving   
# not_ready -> stopped | ready| closed      moving -> stopped | not_ready | closed      stopped -> moving not_ready | closed
#-----------------------------------------------------------------------------------------
def rsu_system(rsu_interface, start_flag, coordinates, my_system_rxd_queue, rsu_control_txd_queue):
    
     while not start_flag.isSet():
         time.sleep (1)
     if (app_conf.debug_sys):
         print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     time.sleep (app_rsu_conf.warm_up_time)
     global ambulancia
     #init rsu
     print("** SEMAFORO A INICIAR **\n")
     start_rsu(rsu_control_txd_queue)
     turn_on(rsu_control_txd_queue)
     
     
     #init intersection variables
     #tls_groups: dictionary containing all the tls of the intersection
     #num_tls: number of tls of the intersection
     #keys: IDs of the tls of the intersection
     tls_group = maps.map[rsu_interface["node_id"]]['tls_groups']
     #Give me print of the initial state
    #  print("Ver o estado inicial",tls_group)
     movement = maps.map[rsu_interface["node_id"]]['movement']
     #print do movement
    #  print("Ver o movimento",movement)
     num_tls = maps.map[rsu_interface["node_id"]]['num_tls']
     keys = list(tls_group.keys())


     #initial value used to guarantee the while execution
     data = 's'
     count = 0
     count2 = 0
     while (data != 'x'):
          #print tls status
        #   print("tls status: ", tls_group) 
          # case 1: intersection with 1 tls - used to control a road with a single lane.
          if num_tls == 1:
               single_tls (tls_group, rsu_control_txd_queue) 
          # case 2: intersection with 2 tls - used to control a road with two lanes.
          elif num_tls == 2: 
               key_s1 = keys[0]
               key_s2 = keys[1] 
               same_state = False
               #case 2.1 - tls controls two lanes of the same road, one in each direction. The 2 tls share the same status.
               #case 2.w - tls controls two lanes of the different roads. The 2 tls do not share the same status.
               if (tls_group[key_s1]['state']==tls_group[key_s2]['state']):
                    same_state = True     
               if (same_state):
                    single_lane_tls(tls_group, rsu_control_txd_queue, movement)
               else:
                    multiple_lane_tls(tls_group, rsu_control_txd_queue)
          # case 2: intersection with 4 tls - used to control two roads with two lanes each.
          elif num_tls == 4:
               if ambulancia == 0:
                    # print("entrei no junction_tls\n")
                    junction_tls (tls_group, rsu_control_txd_queue, movement, count, ambulancia)
          # Notify the new tls status to trigger spat message transmission
          with status_update:
               status_update.notify()
          time.sleep(app_rsu_conf.tls_timing)
     #cancel RSU
          if ambulancia == 2 and count2 == 0:
            count2 = 1
            turn_off(rsu_control_txd_queue)
            exit_rsu(rsu_control_txd_queue)
            



