
let userLocation = null;
// Initialize the platform object with your HERE API key
const platform = new H.service.Platform({
    'apikey': 'OywB5dZJhueuop5qQb-gCIESDdExRxg1IgjrYtjgWiQ' 
});

const defaultLayers = platform.createDefaultLayers();

const map = new H.Map(
    document.getElementById('mapContainer'),
    defaultLayers.vector.normal.map,
    {
        zoom: 10,
        center: { lat: 35.783371, lng: -78.810053 } 
    }
);

const ui = H.ui.UI.createDefault(map, defaultLayers);
const mapEvents = new H.mapevents.MapEvents(map);
const behavior = new H.mapevents.Behavior(mapEvents);
let routeGroup = new H.map.Group();
let markerGroup = new H.map.Group();
map.addObject(routeGroup);
map.addObject(markerGroup);


// Function to fetch data from the backend
async function fetchData(latitude, longitude) {
    try {
        const response = await fetch('http://localhost:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude
            })
        });

        if (!response.ok) {
            alert('No charging stations found.');
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (!data.top_stations || data.top_stations.length === 0) {
            alert('No charging stations found.');
            return;
        }

        // Display multiple stations
        displayStations(data.top_stations);

        // Center the map on the user location
        userLocation = {
            lat: data.top_stations[0].user_location[0],
            lng: data.top_stations[0].user_location[1]
        };
        map.setCenter(userLocation);

        // Add marker for user location
        const userMarker = new H.map.Marker(userLocation);
        map.addObject(userMarker);
        markerGroup.addObject(userMarker);

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Function to display the stations in tiles
function displayStations(stations) {
    console.log('Displaying stations:', stations); // Debugging line
    const container = document.getElementById('stationContainer');
    container.innerHTML = '';

    stations.forEach(station => {
        const tile = document.createElement('div');
        tile.className = 'station-tile';
        tile.innerHTML = `
            <h3>${station.station_name}</h3>
            <p>Distance: ${station.distance_km.toFixed(2)} km</p>
            <p>Predicted Energy: ${station.predicted_energy_kwh.toFixed(2)} kWh</p>
            <button onclick="showDirections(${station.station_location[0]}, ${station.station_location[1]})">Get Directions</button>
        `;
        container.appendChild(tile);
    });
}

// Function to show directions to the selected station
async function showDirections(lat, lng) {
    if (!userLocation) {
        console.error("User  location is not set.");
        return;
    }
    await displayRoute(userLocation, { lat, lng });
}

// Function to display the route between two points
// async function displayRoute(start, end) {
//     const apiKey = "OywB5dZJhueuop5qQb-gCIESDdExRxg1IgjrYtjgWiQ";
//     const routingServiceUrl = `https://router.hereapi.com/v8/routes?transportMode=car&origin=${start.lat},${start.lng}&destination=${end.lat},${end.lng}&return=polyline&apikey=${apiKey}`;

//     try {
//         const response = await fetch(routingServiceUrl);
//         const data = await response.json();

//         console.log("Route Data:", data); // Debugging to check response

//         if (!data.routes || data.routes.length === 0 || !data.routes[0].sections) {
//             console.error("No valid routes found");
//             return;
//         }

//         // Extract polyline
//         const routePolyline = data.routes[0].sections[0].polyline;

//         // Decode polyline to LineString
//         const lineString = H.geo.LineString.fromFlexiblePolyline(routePolyline);

//         // Create a polyline object
//         const routeShape = new H.map.Polyline(lineString, {
//             style: { strokeColor: "blue", lineWidth: 5 }
//         });

//         // Add polyline to the map
//         map.addObject(routeShape);

//         // Adjust map view to fit the route
//         map.getViewModel().setLookAtData({ bounds: routeShape.getBoundingBox() });

//     } catch (error) {
//         console.error("Error fetching route:", error);
//     }
// }
async function displayRoute(start, end) {
    // Clear previous route
    routeGroup.removeAll();

    const apiKey = "OywB5dZJhueuop5qQb-gCIESDdExRxg1IgjrYtjgWiQ";
    const routingServiceUrl = `https://router.hereapi.com/v8/routes?transportMode=car&origin=${start.lat},${start.lng}&destination=${end.lat},${end.lng}&return=polyline&apikey=${apiKey}`;

    try {
        const response = await fetch(routingServiceUrl);
        const data = await response.json();

        if (!data.routes || data.routes.length === 0 || !data.routes[0].sections) {
            console.error("No valid routes found");
            return;
        }

        // Extract and decode polyline
        const routePolyline = data.routes[0].sections[0].polyline;
        const lineString = H.geo.LineString.fromFlexiblePolyline(routePolyline);

        // Create polyline object
        const routeShape = new H.map.Polyline(lineString, {
            style: { strokeColor: "blue", lineWidth: 5 }
        });

        // Add route to the group
        routeGroup.addObject(routeShape);

        // Adjust view
        map.getViewModel().setLookAtData({ bounds: routeShape.getBoundingBox() });

    } catch (error) {
        console.error("Error fetching route:", error);
    }
}


// Event listener for the submit button
document.getElementById('submitButton').onclick = function() {
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);

    if (!isNaN(latitude) && !isNaN(longitude)) {
        markerGroup.removeAll();
        fetchData(latitude, longitude);
    } else {
        alert('Please enter valid latitude and longitude values.');
    }
};