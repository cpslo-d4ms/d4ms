
<h1 align="center">Autonomous UAV Survey of Morro Bay Eel Grass</h1>

<p align="center">
  <a href="#setup">Setup</a> &#xa0; | &#xa0;
  <a href="#misssion-flow">Mission Flow</a> &#xa0; | &#xa0;
  <a href="#future-development-areas">Development Areas</a> &#xa0; | &#xa0;
  <a href="#known-bugs">Known Bugs</a> &#xa0;
</p>

<br>

## Setup

To use the GCS, both the front end and back end will need to be configured on the desired computer.

Front end:
- install NPM 7.X.X
```bash
cd gcs_fe
npm install #installs dependencies
npm start #starts front end on localhosts (http://localhost:3000)
```
Back end:
- install python 3.4^
```bash
cd gcs_be
pip install -r requirements.txt # install dependencies as needed
export FLASK_APP=server.py # instructs flask where to run server, needs to be run every time
flask run
```

Simulator (to simulate mission without physical vehicle)

- view [instructions for setting up simulator](https://ardupilot.org/dev/docs/SITL-setup-landingpage.html#sitl-setup-landingpage) (Linux instructions work on Mac)

- modify `ardupilot/Tools/autotest/locations.txt` to include your target location name=lat,lng,alt,heading. Ex:
- ```
    EFR=35.329285,-120.752466,0,0
    ```
- ```bash
    sim_vehicle.py -v ArduCopter -L EFR #start the simulator
    ```

## Misssion Flow

Prerequisites
- Install both front and back ends of GCS
- Follow safety regulations provided in requirements
- 3dr SOLO is powered on and has no errors

Mission instructions
- Connect to a phone hotspot
- Start GCS front end, make sure the ROI is loaded in the map (this will cache the map)
- Boot 3DR Solo and remote
- Connect to SOLOLINK wifi (password sololink)
- Start GCS back end and await "connection successful" message, the vehicle should now appear in the front end UI
- Click the rectangle tool at the top right of the screen and draw your ROI
- Click "take off" and await completion
- Select "Mission Init" and await completion
- Select "RTL"

## 3DR SOLO Debugging
This will require the SidePilot app (IOS), or alternative for android. Console logs are vieable through this, as well as calibrations as needed.

THE SOLOLINK APP WILL NOT WORK!!!

Currently the vehicle is running OpenSolo 4.0, which is set as the golden version (factory default)
https://github.com/OpenSolo/OpenSolo/wiki#INSTALL_OPEN_SOLO_4

## Future Development Areas

- post processing and data collection
- allow user to manipulate ROI after drawing (Map.js:157)
- Add geofencing in addition to ROI to enforce a no-fly-zone
- Add config file to easily update parameters such as waypoint fidelity, airspeed, altitude, and distance between raster sweeps

## Known bugs

- After drawing ROI, tools will disapear as intended, however the current selected tool remains selected. Pressing escape immediately after drawing will prevent drawing further rectangles
