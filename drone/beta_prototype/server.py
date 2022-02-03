from flask import Flask, Response, request
import json
from fly import * 
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# connection_string = "tcp:127.0.0.1:5760" #sim
# connection_string = 'udpin:0.0.0.0:14550' #3dr
connection_string = '/dev/ttyAMA0'

connect_drone(connection_string);

app = Flask(__name__)

@app.route('/status')
def health_and_status():
    resp = Response(json.dumps({
        "battery": getBatt(),
        "lat": getLat(),
        "lng": getLon(),
        "altitude": getAlt()
    }))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/takeoff')
def takeoff():
    arm_and_takeoff()
    resp = Response("At target altitude")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/RTL')
def rtl():
    RTL()
    resp = Response("Returning to land")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/mission_go', methods = ['GET', 'POST', 'OPTIONS'])
def mission_go():

    coords = json.loads(request.args.get('boundingBox'))[:-1] #remove repeated index
    coords = sorted(coords, key=lambda c: (c[1], c[0]))
    coords = coords[:-2] + [coords[-1], coords[-2]]

    mission_exec(coords)
    
    resp = Response("Mission Complete")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
