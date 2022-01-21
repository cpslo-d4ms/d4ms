import React, {Component, useRef} from 'react';
import { loadModules } from 'esri-loader';
import { Button } from '@material-ui/core'
import axios from 'axios'
// REFRESH RATE IN mHZ
const refreshRate = 300

// LAT LONG OF INITIAL MAP POSITION (EFR)
const mapPosition = [35.329285, -120.752466]

export default class MyMap extends Component {
    state = {
        boundingBox: null
    }

    vehicleAttributes = ['battery', 'altitude']

    constructor(props) {
        super(props);
        this.container = React.createRef();
        this.status_updater = setInterval(() => {
            axios.get("http://127.0.0.1:5000/status").then(({data}) => {
                this.setState({vehicle: data})
                // this.vehicleLocation.setLatitude(data.lat)
                this.vehicleLocation = new this.Point({
                    longitude: data.lng,
                    latitude: data.lat,
                });

                // Create a symbol for drawing the point
                const textSymbol = {
                    type: "text", // autocasts as new TextSymbol()
                    color: "#7A003C",
                    text: "\ue61d", // esri-icon-map-pin
                    font: {
                        // autocasts as new Font()
                        size: 36,
                        family: "CalciteWebCoreIcons"
                    }
                };

                  // Create a graphic and add the geometry and symbol to it
                const vehicleGraphic = new this.Graphic({
                    geometry: this.vehicleLocation,
                    symbol: textSymbol
                });
                this.vehicle_layer.removeAll()
                this.vehicle_layer.add(vehicleGraphic)

            }).catch(console.log)
        }, refreshRate)
    }

    render() {
        return <div>
                <div style={{ height: '100vh' }} ref={this.container} />
                <div style={{
                    position: 'absolute',
                    top: '5vh',
                    left: '10vw',
                    opacity: .7,
                    backgroundColor: 'rgba(0, 0, 0, 0.6)',
                    borderRadius: '5px'
                }}>
                    {this.state.vehicle ? <div>
                            {this.vehicleAttributes.map((a, i) => <div key={a} style={{
                                width: '20vw',
                                float: 'left',
                                fontSize: '0.5em'
                            }}>
                                <p> {a} </p>
                                <p> {this.state.vehicle[a]} </p>
                            </div>)}
                        </div> :
                        'waiting for vehicle to connect'}
                </div>
                <div style={{
                    position: 'absolute',
                    bottom: '10px',
                    left: '10px'
                }}>
                    <Button variant="contained" onClick={() => axios.get("http://127.0.0.1:5000/takeoff").catch(console.log)}>TAKEOFF</Button>
                    <Button variant="contained" onClick={() => {
                            axios.get("http://127.0.0.1:5000/mission_go", {
                                params: {
                                    boundingBox: JSON.stringify(this.state.boundingBox)
                                }
                            })
                            .then(console.log)
                            .catch(console.log)
                        }}>
                        Mission Start
                    </Button>
                    <Button variant="contained" onClick={() => axios.get("http://127.0.0.1:5000/RTL").then(console.log)}>RTL</Button>
                </div>
            </div>
    }

    componentDidMount() {
        // load and create map module and insert into ref
        loadModules(
            [
                "esri/views/MapView",
                "esri/layers/GraphicsLayer",
                "esri/Map",
                "esri/widgets/Sketch",
                "esri/Graphic",
                "esri/geometry/support/webMercatorUtils",
                "esri/geometry/Point"
            ],
            {
                css: "https://js.arcgis.com/4.13/esri/themes/light/main.css"
            }
        ).then(([MapView, GraphicsLayer, Map, Sketch, Graphic, webMercatorUtils, Point]) => {
            this.Point = Point
            this.Graphic = Graphic

            const layer = new GraphicsLayer();
            this.vehicle_layer = new GraphicsLayer();
            const map = new Map({
                basemap: "satellite",
                layers: [layer, this.vehicle_layer]
            });

            // and we show that map in a container
            this.view = new MapView({
                map: map,
                zoom: 18,
                center: [-120.751908, 35.328674],
                // use the ref as a container
                container: this.container.current
            });

            const sketch = new Sketch({
                layer: layer,
                view: this.view,
                availableCreateTools: ["rectangle"]
            });

            sketch.on("create", (event) => {
            // check if the create event's state has changed to complete indicating
            // the graphic create operation is completed.
                if (event.state === "complete") {
                    sketch.availableCreateTools = []

                    this.view.ui.remove(sketch, "top-right");
                    sketch.cancel()
                    if(!this.state.boundingBox) {
                        this.setState({
                            boundingBox: event.graphic.geometry.rings[0].map(r => webMercatorUtils.xyToLngLat(...r))
                            // SEND TO BACKEND
                        })
                    }
                }
            })
            // TODO: ON UPDATE SHAPE UPDATE POLYGON TO SEND TO BACKEND

            this.view.ui.add(sketch, "top-right");
        });
    }
}
