#!/usr/bin/env python
# #####################################################################################################
# rsu_control comamnds: output test only with: single pin (led) and set of pind (traffic light)
#   Note: modifications required, for complex traffic light systems (with more than one semaphore)
#######################################################################################################
import application.app_config as app_conf

def start_rsu(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: start_rsu')

    rsu_control_msg="s"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def exit_rsu(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: exit_rsu')
    rsu_control_msg="x"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def turn_on(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: turn_on \n')
    rsu_control_msg="1"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def turn_off(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: turn_off')
    rsu_control_msg="0"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def green_tls(rsu_control_txd_queue, direction, emergency):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        # print ('rsu_application: green_tls')
        if emergency == 1 or emergency == 2:
            print (f'** Direction - {direction} - rsu_application: GREEN due to priority **\n')
        else:
            print (f'** Direction - {direction} - rsu_application: GREEN **\n')
    rsu_control_msg="green"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def yellow_tls(rsu_control_txd_queue, direction, emergency):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        # print ('rsu_application: yellow_tls')
        if emergency == 1 or emergency == 2:
            print (f'** Direction - {direction} - rsu_application: YELLOW due to priority **\n')
        else:
            print (f'** Direction - {direction} - rsu_application: YELLOW **\n')

    rsu_control_msg="yellow" 
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def red_tls(rsu_control_txd_queue, direction, emergency):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        if emergency == 1 or emergency == 2:
            print (f'** Direction - {direction} - rsu_application: RED due to priority **\n')
        else:
            print (f'** Direction - {direction} - rsu_application: RED **\n')
        
    rsu_control_msg="red" 
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def intersection_update(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: intersection_state updated')
    rsu_control_msg="ok" 
    rsu_control_txd_queue.put(rsu_control_msg)
    return    

def sem_id(rsu_control_txd_queue, data):
    # if (app_conf.debug_app) or (app_conf.debug_rsu):
    #     print ('rsu_application: sem_id' , data)
    rsu_control_msg=data
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def single_tls (tls, rsu_control_txd_queue):
    
    state = next(iter(tls.values()))['state']
    key = next(iter(tls))
    
    if (state=='green'):
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key)
    elif (state=='yellow'):
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key)
    elif (state=='red'):
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key)


def multiple_lane_tls(lane_tls, rsu_control_txd_queue):
    keys = list(lane_tls.keys())
    key_s1 = keys[0]
    key_s2 = keys[1]
    if (lane_tls[key_s1]['state']=='green'):
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)
    elif (lane_tls[key_s1]['state']=='yellow'):
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)
    elif (lane_tls[key_s1]['state']=='red'):
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)

    

def single_lane_tls(lane_tls, rsu_control_txd_queue, movement, emergency):
    keys = list(lane_tls.keys())
    key_s1 = keys[0]
    key_s2 = keys[1]

    # Semáforo 1
    direction_s1 = movement.get(key_s1, {}).get("direction", "Unknown")
    # Semáforo 2
    direction_s2 = movement.get(key_s2, {}).get("direction", "Unknown")

    if (lane_tls[key_s1]['state'] == 'green'):
        # print(f"** Direction: {direction_s1} - GREEN **\n")
        
        yellow_tls(rsu_control_txd_queue, direction_s1, emergency)
        sem_id(rsu_control_txd_queue, key_s1)

        # print(f"** Direction: {direction_s2} - GREEN **\n")
        yellow_tls(rsu_control_txd_queue, direction_s2, emergency)
        sem_id(rsu_control_txd_queue, key_s2)
        
    elif (lane_tls[key_s1]['state'] == 'yellow'):
        # print(f"** Direction: {direction_s1} - YELLOW **\n")
        red_tls(rsu_control_txd_queue, direction_s1, emergency)
        sem_id(rsu_control_txd_queue, key_s1)

        # print(f"** Direction: {direction_s2} - YELLOW **\n")
        red_tls(rsu_control_txd_queue, direction_s2, emergency)
        sem_id(rsu_control_txd_queue, key_s2)
        
    elif (lane_tls[key_s1]['state'] == 'red'):
        # print(f"** Direction: {direction_s1} - RED **\n")
        green_tls(rsu_control_txd_queue, direction_s1, emergency)
        sem_id(rsu_control_txd_queue, key_s1)

        # print(f"** Direction: {direction_s2} - RED **\n")
        green_tls(rsu_control_txd_queue, direction_s2, emergency)
        sem_id(rsu_control_txd_queue, key_s2)
        

def junction_tls(tls_group, rsu_control_txd_queue, movement, count, emergency):
    first_lane_tls = dict(list(tls_group.items())[:2])
    second_lane_tls = dict(list(tls_group.items())[-2:])
    state = next(iter(first_lane_tls.values()))["state"]
    
    if state == 'green':
        # print("[JUNCTION] First lane group is green.")
        print("-------------------------------------------------------\n")
        single_lane_tls(first_lane_tls, rsu_control_txd_queue, movement, emergency)
        single_lane_tls(second_lane_tls, rsu_control_txd_queue, movement, emergency )
        print("-------------------------------------------------------\n")
        
    else:
        # print("[JUNCTION] Second lane group is green.")
        print("-------------------------------------------------------\n")
        single_lane_tls(second_lane_tls, rsu_control_txd_queue, movement, emergency)
        single_lane_tls(first_lane_tls, rsu_control_txd_queue, movement, emergency)
        print("-------------------------------------------------------\n")
        


     