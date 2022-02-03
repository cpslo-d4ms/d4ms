import time
from dronekit import *
import math

targetAltitude = 10

def connect_drone(connection_string):
    global vehicle
    vehicle = connect(connection_string, wait_ready=True, baud=921600)
    print('Connected!')
    vehicle.parameters['RTL_ALT'] = 1000.0
    vehicle.parameters['RTL_LOIT_TIME'] = 0.0

def RTL():
    vehicle.mode = VehicleMode("RTL")
    while not vehicle.mode.name=='RTL':
        print(" Getting ready to RTL...")
        time.sleep(1)

# def go_to(vehicle, waypoint):

def arm_and_takeoff():
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(targetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= targetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def set_target_altitude(altitude):
    targetAltitude = altitude

def getBatt():
    return vehicle.battery.level

def getLat():
    return vehicle.location.global_relative_frame.lat

def getLon():
    return vehicle.location.global_relative_frame.lon

def getAlt():
    return vehicle.location.global_relative_frame.alt

def mission_exec(coords):
    dist = 20 / 111111
    
    try:
        theta_offset = math.atan((coords[0][1] - coords[1][1]) / (coords[0][0] - coords[1][0]))
        theta_offset = math.radians(theta_offset)

        rect_height = math.sqrt(
            (coords[2][1] - coords[1][1]) ** 2 +
            (coords[2][0] - coords[1][0]) ** 2
        )
        passes = math.ceil(rect_height / (2 *dist))

    except ZeroDivisionError as e:
        print(e)
        return 'failure'

    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    cmds.clear()

    points = []

    for i in range(passes):
        lng = coords[0][0] + math.sin(theta_offset) * dist * 2 * i
        lat = coords[0][1] + math.cos(theta_offset) * dist * 2 * i

        cmd = Command(0,0,0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0,0,0,0,0,0,
            lat, lng, targetAltitude)

        cmds.add(cmd)

        lng = coords[1][0] + math.sin(theta_offset) * dist * i * 2
        lat = coords[1][1] + math.cos(theta_offset) * dist * i * 2

        cmd = Command(0,0,0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0,0,0,0,0,0,
            lat, lng, targetAltitude)

        cmds.add(cmd)

        lng = coords[1][0] + math.sin(theta_offset) * dist * (2 * i + 1)
        lat = coords[1][1] + math.cos(theta_offset) * dist * (2 * i + 1)

        cmd = Command(0,0,0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0,0,0,0,0,0,
            lat, lng, targetAltitude)

        cmds.add(cmd)

        lng = coords[0][0] + math.sin(theta_offset) * dist * (2 * i + 1)
        lat = coords[0][1] + math.cos(theta_offset) * dist * (2 * i + 1)

        cmd = Command(0,0,0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0,0,0,0,0,0,
            lat, lng, targetAltitude)

        cmds.add(cmd)


    cmds.upload()

    time.sleep(2)
    vehicle.mode = VehicleMode("AUTO")

    print("Commands uploaded successfullly")

