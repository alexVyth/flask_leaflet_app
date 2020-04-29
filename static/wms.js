var map = L.map('mapid', {
    center: [0, 0],
    zoom: 2
});
map._fadeAnimated = false

var baseLayers = {
Temperature: L.tileLayer.wms('http://localhost:8080/geoserver/geo/ows', {
    className: 'temp',
    layers: 'annual_temp',
    format: 'image/png',
    version: '1.3.0',
    attribution: 'Averaged Annual Temperature Data in °C &copy; <a href="https://power.larc.nasa.gov/data-access-viewer/">NASA Prediction Of Worldwide Energy Resources</a>'
}),
Humidity: L.tileLayer.wms('http://localhost:8080/geoserver/geo/ows', {
    className: 'hum',
    layers: 'annual_hum',
    format: 'image/png',
    version: '1.3.0',
    attribution: 'Averaged Annual Relative Humidity Data &copy; <a href="https://power.larc.nasa.gov/data-access-viewer/">NASA Prediction Of Worldwide Energy Resources</a>'
}),
Precipitation: L.tileLayer.wms('http://localhost:8080/geoserver/geo/ows', {
    className: 'prec',
    layers: 'annual_prec',
    format: 'image/png',
    version: '1.3.0',
    attribution: 'Averaged Annual Precipitation Data in mm &copy; <a href="https://power.larc.nasa.gov/data-access-viewer/">NASA Prediction Of Worldwide Energy Resources</a>'
})
};

var overlayMaps = {
Countries: L.tileLayer.wms('http://localhost:8080/geoserver/geo/ows', {
    layers: 'countries',
    format: 'image/png',
    version: '1.3.0',
    transparent: true,
    attribution: 'Countries Data &copy; <a href="https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/countries">eurostat</a>'
})
};
L.control.layers(baseLayers,overlayMaps).addTo(map);

baseLayers.Temperature.addTo(map);
L.wmsLegend("http://localhost:8080/geoserver/wms?REQUEST=GetLegendGraphic&VERSION=1.3.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=annual_temp");

var popup = L.popup();

function onMapClick(e) {
    popup
        .setLatLng(e.latlng)
        .setContent(e.latlng.toString())
        .openOn(map);
}

map.on('click', onMapClick);

function checkBaseMap() {
    $('.leaflet-control-wms-legend').remove();
    if (document.getElementsByClassName('temp').length > 0) {
        L.wmsLegend("http://localhost:8080/geoserver/wms?REQUEST=GetLegendGraphic&VERSION=1.3.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=annual_temp");
    } 

    if (document.getElementsByClassName('hum').length > 0)  {
        L.wmsLegend("http://localhost:8080/geoserver/wms?REQUEST=GetLegendGraphic&VERSION=1.3.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=annual_hum");
    }

    if (document.getElementsByClassName('prec').length > 0) {
        L.wmsLegend("http://localhost:8080/geoserver/wms?REQUEST=GetLegendGraphic&VERSION=1.3.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=annual_prec");
    }
}
map.on('baselayerchange', checkBaseMap);

updateMap = function( {value} ){
    var s = value + "";
    if (s.length < 2) s = "0" + s;
    time = "2000-" + s + "-01";

    if (document.getElementsByClassName('temp').length > 0) {
        baseLayers.Temperature.setParams({"time": time, "layers": "temp"});
    }
    if (document.getElementsByClassName('hum').length > 0) {
        baseLayers.Humidity.setParams({"time": time, "layers": "hum"});
    }
    if (document.getElementsByClassName('prec').length > 0) {
        baseLayers.Precipitation.setParams({"time": time, "layers": "prec"});
    }
}

if (mapType == 'monthly') {
    L.control.timelineSlider({
                    timelineItems: ["January", "February", "March", "April", "May", "June", "Jule", "August", "September", "October", "November", "December"],
                    changeMap: updateMap })
                .addTo(map); 
}
