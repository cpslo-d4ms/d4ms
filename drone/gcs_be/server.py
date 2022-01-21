from flask import Flask, Response, request
from dronekit import connect, VehicleMode, time, LocationGlobalRelative, Command, mavutil
import json, math
from fly import arm_and_takeoff, RTL
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# connection_string = "tcp:127.0.0.1:5760" #sim
connection_string = 'udpin:0.0.0.0:14550' #3dr

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (connection_string,))
try:
    vehicle = connect(connection_string, wait_ready=True)
except OSError:
    connection_string = 'udpin:0.0.0.0:14551'
    vehicle = connect(connection_string, wait_ready=True)
print('Connected!')

vehicle.parameters['RTL_ALT'] = 1000.0
vehicle.parameters['RTL_LOIT_TIME'] = 0.0

app = Flask(__name__)

@app.route('/status')
def health_and_status():
    resp = Response(json.dumps({
        "battery": vehicle.battery.level,
        "lat": vehicle.location.global_relative_frame.lat,
        "lng": vehicle.location.global_relative_frame.lon,
        "altitude": vehicle.location.global_relative_frame.alt
    }))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/takeoff')
def takeoff():
    arm_and_takeoff(vehicle, 10)
    resp = Response("At target altitude")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/RTL')
def rtl():
    RTL(vehicle)
    resp = Response("Returning to land")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# distance between raster sweeps (METERS)
dist = 20

# altitude of waypoints (METERS)
alt = 10

@app.route('/mission_go', methods = ['GET', 'POST', 'OPTIONS'])
def mission_go():
    global dist, alt

    dist = dist / 111111 #convert to degrees, flat earth aprox

    coords = json.loads(request.args.get('boundingBox'))[:-1] #remove repeated index

    coords = sorted(coords, key=lambda c: (c[1], c[0]))
    coords = coords[:-2] + [coords[-1], coords[-2]]

    try:
        theta_offset = math.atan((coords[0][1] - coords[1][1]) / (coords[0][0] - coords[1][0]))
        theta_offset = math.radians(theta_offset)

        rect_height = math.sqrt(
            (coords[2][1] - coords[1][1]) ** 2 +
            (coords[2][0] - coords[1][0]) ** 2
        )
        passes = math.ceil(rect_height / (2 * dist))

    except ZeroDivisionError as e:
        print(e)
        return 'failure'

    # Call clear() on Vehicle.commands and upload the command to the vehicle.
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    cmds.clear()

    points = []

    # add three points per loop, starting from bottom right, bottom left, shift left up
    for i in range(passes):
        # bottom left point
        lng = coords[0][0] + math.sin(theta_offset) * dist * 2 * i
        lat = coords[0][1] + math.cos(theta_offset) * dist * 2 * i

        cmd = Command(0,0,0, # unused
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame of reference
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, # waypoint command
            0, 0, 0, 0, 0, 0, # ignored
            lat, lng, alt) # lat, lng, alt

        cmds.add(cmd)

        # bottom right
        lng = coords[1][0] + math.sin(theta_offset) * dist * i * 2
        lat = coords[1][1] + math.cos(theta_offset) * dist * i * 2

        cmd = Command(0,0,0, # unused
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame of reference
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, # waypoint command
            0, 0, 0, 0, 0, 0, # ignored
            lat, lng, alt) # lat, lng, alt

        cmds.add(cmd)

        #right shifted up

                # bottom right
        lng = coords[1][0] + math.sin(theta_offset) * dist * (2 * i + 1)
        lat = coords[1][1] + math.cos(theta_offset) * dist * (2 * i + 1)

        cmd = Command(0,0,0, # unused
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame of reference
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, # waypoint command
            0, 0, 0, 0, 0, 0, # ignored
            lat, lng, alt) # lat, lng, alt

        cmds.add(cmd)

        # left shifted up
        lng = coords[0][0] + math.sin(theta_offset) * dist * (2 * i + 1)
        lat = coords[0][1] + math.cos(theta_offset) * dist * (2 * i + 1)

        cmd = Command(0,0,0, # unused
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame of reference
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, # waypoint command
            0, 0, 0, 0, 0, 0, # ignored
            lat, lng, alt) # lat, lng, alt

        cmds.add(cmd)

    #finally add RTL
    rtl_cmd = Command(0,0,0, # unused
    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame of reference
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, # waypoint command
    0, 0, 0, 0, 0, 0, 0, 0, 0)

    cmds.add(cmd)
    cmds.upload()

    time.sleep(2)
    vehicle.mode = VehicleMode("AUTO")

    print("Commands uploaded successfully")
    resp = Response("Mission Complete")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == "__main__":
    # print(health_and_status())
    # go_to_route()
    # takeoff()

    # time.sleep(10)
    # goto()
    mission_go()
    # point2 = LocationGlobalRelative(35.328964, -120.752950, 20)
    # vehicle.simple_goto(point2, groundspeed=10)