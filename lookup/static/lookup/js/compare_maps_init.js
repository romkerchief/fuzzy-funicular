// static/lookup/js/compare_maps_init.js
document.addEventListener('DOMContentLoaded', function() {
    function initializeMap(mapId, latVal, lonVal, popupName, popupCountry, defaultLocationName) {
        const mapElement = document.getElementById(mapId);

        if (mapElement) {
            // Clear "Loading map..." message or any previous content
            mapElement.innerHTML = ''; 

            if (latVal && lonVal && latVal !== '' && lonVal !== '') {
                try {
                    const latitude = parseFloat(latVal);
                    const longitude = parseFloat(lonVal);

                    if (isNaN(latitude) || isNaN(longitude)) {
                        console.error(`Invalid latitude or longitude for map ${mapId}:`, latVal, lonVal);
                        mapElement.innerHTML = `<p class="text-danger">Error: Invalid map coordinates for ${defaultLocationName}.</p>`;
                        return;
                    }

                    const map = L.map(mapElement).setView([latitude, longitude], 10);

                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '&copy; OpenStreetMap contributors'
                    }).addTo(map);

                    let popupText = defaultLocationName || 'Location';
                    if (popupName && popupCountry) {
                        popupText = `${popupName}, ${popupCountry}`;
                    } else if (popupName) {
                        popupText = popupName;
                    }

                    L.marker([latitude, longitude]).addTo(map)
                        .bindPopup(popupText)
                        .openPopup();

                } catch (e) {
                    console.error(`Error initializing Leaflet map ${mapId}:`, e);
                    mapElement.innerHTML = `<p class="text-danger">Map for ${defaultLocationName} could not be loaded due to an error.</p>`;
                }
            } else {
                console.warn(`Map data (latitude/longitude) not available for ${mapId}.`);
                mapElement.innerHTML = `<p class="text-warning">Map data unavailable for ${defaultLocationName}.</p>`;
            }
        } else {
            // console.log(`Map element with id "${mapId}" not found on this page.`);
        }
    }

    // Initialize Map 1
    const map1Element = document.getElementById('map1');
    if (map1Element) {
        initializeMap(
            'map1',
            map1Element.dataset.lat,
            map1Element.dataset.lon,
            map1Element.dataset.popupName,
            map1Element.dataset.popupCountry,
            "First Location" // Default name if specific name unavailable
        );
    }

    // Initialize Map 2
    const map2Element = document.getElementById('map2');
    if (map2Element) {
        initializeMap(
            'map2',
            map2Element.dataset.lat,
            map2Element.dataset.lon,
            map2Element.dataset.popupName,
            map2Element.dataset.popupCountry,
            "Second Location" // Default name
        );
    }
});