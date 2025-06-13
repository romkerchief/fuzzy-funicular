// static/lookup/js/weather_map_init.js
document.addEventListener('DOMContentLoaded', function() {
    const mapElement = document.getElementById('map');

    if (mapElement) {
        const lat = mapElement.dataset.lat;
        const lon = mapElement.dataset.lon;
        const popupName = mapElement.dataset.popupName;
        const popupCountry = mapElement.dataset.popupCountry;

        // Clear the "Loading map..." message
        mapElement.innerHTML = ''; 

        if (lat && lon && lat !== '' && lon !== '') { // Check if lat and lon are valid
            try {
                const latitude = parseFloat(lat);
                const longitude = parseFloat(lon);

                if (isNaN(latitude) || isNaN(longitude)) {
                    console.error('Invalid latitude or longitude for map:', lat, lon);
                    mapElement.innerHTML = '<p class="text-danger">Error: Invalid map coordinates provided.</p>';
                    return;
                }

                var map = L.map(mapElement).setView([latitude, longitude], 10); // Use mapElement directly

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(map);

                let popupText = 'Location'; // Default popup text
                if (popupName && popupCountry) {
                    popupText = `${popupName}, ${popupCountry}`;
                } else if (popupName) {
                    popupText = popupName;
                }

                L.marker([latitude, longitude]).addTo(map)
                    .bindPopup(popupText)
                    .openPopup();

            } catch (e) {
                console.error("Error initializing Leaflet map:", e);
                mapElement.innerHTML = '<p class="text-danger">Map could not be loaded due to an error.</p>';
            }
        } else {
            // This case should ideally be handled by the Django template not rendering the map div 
            // or by the view not providing lat/lon if they are truly unavailable.
            // However, this is a client-side fallback.
            console.warn('Map data (latitude/longitude) not available or incomplete.');
            mapElement.innerHTML = '<p class="text-warning">Map data unavailable to display.</p>';
        }
    } else {
        // console.log('Map element with id "map" not found on this page.');
    }
});