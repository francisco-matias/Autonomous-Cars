#!/usr/bin/env python
# #####################################################################################################
# APP CONFIGURATION PARAMETERS -
#######################################################################################################
max_latency = 10000

#------------------------------------------------------------------------------------------
#include here any specific configuration of the application
#------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Car control
#-----------------------------------------------------------------------------------------
#definir aqui a informacao necessaria à configuracao duma OBU
warm_up_time = 10

# Por exemplo: parametros do movimento. 
movement_update_time = 1

ca_generation_interval = 5
crash_iminent = 100
emergency_distance = 200
safety_distance = 500

# example of DEN message configuration. 
# Definition of the first event (position 0 of the array)

safety_critical = 0
# DEN message - Event type
event_type = ["safety_critical_warning"]
# DEN message - Event status (start | update | stop)
status = ['start']
#if event_status == 'start':
#DEN message - repetition interval (0 if single event)
rep_interval = [0]
# DEN message - Maximum hop number
n_hops = [8]
#DEN message - ROI x coordinates (0 if none)
roi_x  = [0]
#DEN message - ROI y coordinates (0 if none)
roi_y  = [0]
#DEN message - ROI y coordinates (0 if none)
latency = [max_latency]


# -----------------------------------------------------------------------------------------
# Add new event for emergency vehicles
# -----------------------------------------------------------------------------------------

# Define index for the new event
emergency_vehicle_approaching = 1

# Add event properties
event_type.append("emergency_vehicle_approaching")
status.append('start')
rep_interval.append(0)  # No repetition
n_hops.append(8)  # Max hops allowed
roi_x.append(0)  # Region of Interest X-axis (not implemented yet)
roi_y.append(0)  # Region of Interest Y-axis (not implemented yet)
latency.append(max_latency)  # Maximum latency


# IMPORTANT TIP: roi, latency are not implemented but can be added.
# To create a new event, name it and assign the next integer to refer to te event position in the array. 
# Example: new_event = 1
# Add an element to each vector with the descritpion of the event.
# Example: New event, with periodic transmission (100), 8 hops dissemination, and a roi, in x axis up to 1000 units distance
# event_type = ["SAFETY CRITICAL WARNING"]["NEW EVENT"]
# event_status = ['start']['start']
# rep_interval = [0][100]   
# n_hops = [1][8]
# roi_x  = [0][1000]
# roi_y  = [0][0]
# latency = [max_latency][max_latency]

# IMPORTANT TIP: update messages are not implemented but can be added.
# To create an update event, name it and assign the next integer to refer to te event position in the array. 
# Example: update_event = 2
# Add an element to each vector with the descritpion of the event.
# Example: New event, with periodic transmission (100), 8 hops dissemination, and a roi, in x axis up to 1000 units distance
# event_type = ["SAFETY CRITICAL WARNING"]["NEW EVENT"]["UPDATE EVENT"]
# event_status = ['start']['start']['update']
# rep_interval = [0][100][-1]   
# n_hops = [1][8][-1] 
# roi_x  = [0][1000][-1] 
# roi_y  = [0][0][-1] 
# latency = [max_latency][max_latency][-1] 
