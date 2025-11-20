// Map Interactive Features - Using Python Backend for Logic
// This file handles frontend interactions only. Backend logic is in Django views.

let map;
let markers = [];
let currentMarker = null;
let mapConfig = {};

// Initialize the map by fetching config from Python backend
async function initMap() {
    try {
        // Fetch configuration from Python backend
        const configResponse = await fetch('/HomeScreen/api/map-config/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!configResponse.ok) {
            throw new Error(`API error: ${configResponse.status}`);
        }
        
        mapConfig = await configResponse.json();
    } catch (error) {
        console.warn('API config fetch failed, using defaults:', error);
        // Fallback configuration
        mapConfig = {
            'default_coords': {
                'lat': 10.8231,
                'lon': 106.6797
            },
            'default_zoom': 12,
            'cities': [
                {'name': 'Ho Chi Minh City', 'lat': 10.8231, 'lon': 106.6797, 'emoji': '🏠'},
                {'name': 'Hanoi', 'lat': 21.0285, 'lon': 105.8542, 'emoji': '🏯'},
                {'name': 'Can Tho', 'lat': 10.3157, 'lon': 103.8484, 'emoji': '🌴'},
            ],
            'map_tiles': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'leaflet_cdn': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
        };
    }
    
    try {
        // Create map container
        const mapContainer = document.getElementById('map');
        
        if (!mapContainer) {
            console.error('Map container not found');
            return;
        }

        // Initialize using Leaflet
        const coords = mapConfig.default_coords;
        map = L.map('map').setView([coords.lat, coords.lon], mapConfig.default_zoom);

        // Add OpenStreetMap tiles
        L.tileLayer(mapConfig.map_tiles, {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
        }).addTo(map);

        // Add interaction events
        map.on('click', onMapClick);
        map.on('move', onMapMove);
        map.on('zoom', onMapZoom);

        // Add a default marker
        addMarker(coords.lat, coords.lon, 'Home Location');

        // Update coordinates display
        updateCoordinatesDisplay();
        
        // Load saved markers from database
        loadSavedMarkers();

        console.log('Map initialized successfully');
    } catch (error) {
        console.error('Error initializing map:', error);
    }
}

// Handle map click to add markers
function onMapClick(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    
    console.log(`Map clicked at: ${lat}, ${lon}`);
    
    // Add marker at click location
    addMarker(lat, lon, 'Clicked Location');
    
    // Get location details from Python backend
    getLocationDetailsFromPython(lat, lon);
    
    // Save marker to database
    saveMarkerToDatabase(lat, lon, 'Clicked Location');
    
    // Update coordinates display
    updateCoordinatesDisplay();
}

// Add a marker to the map
function addMarker(lat, lon, title) {
    const marker = L.marker([lat, lon]).addTo(map);
    
    // Create popup with location info
    const popup = L.popup()
        .setLatLng([lat, lon])
        .setContent(`
            <div style="padding: 10px;">
                <strong>${title}</strong><br>
                Latitude: ${lat.toFixed(6)}<br>
                Longitude: ${lon.toFixed(6)}<br>
                <button onclick="copyCoordinates(${lat}, ${lon})" style="margin-top: 8px; padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    Copy Coords
                </button>
            </div>
        `);
    
    marker.bindPopup(popup);
    marker.on('click', () => {
        currentMarker = marker;
        updateCoordinatesDisplay(lat, lon);
    });
    
    markers.push({
        marker: marker,
        lat: lat,
        lon: lon,
        title: title
    });
    
    return marker;
}

// Get location details from Python backend API
async function getLocationDetailsFromPython(lat, lon) {
    try {
        showLoadingState(true);
        
        const response = await fetch('/HomeScreen/api/reverse-geocode/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lat: lat,
                lon: lon
            })
        });
        
        const data = await response.json();
        showLoadingState(false);
        
        if (data.success) {
            displayLocationInfo(lat, lon, {
                address: data.address,
                city: data.city,
                country: data.country,
                postcode: data.postcode || 'N/A'
            });
            
            // Update the database marker with full location info
            updateMarkerWithLocationInfo(lat, lon, data.address, data.city, data.country, data.postcode);
        } else {
            console.error('Error from backend:', data.error);
        }
    } catch (error) {
        showLoadingState(false);
        console.error('Error fetching location details:', error);
    }
}

// Update the most recent marker with location details
async function updateMarkerWithLocationInfo(lat, lon, address, city, country, postcode) {
    // Find the marker that matches these coordinates (most recent)
    const marker = markers[markers.length - 1];
    if (marker && Math.abs(marker.lat - lat) < 0.001 && Math.abs(marker.lon - lon) < 0.001) {
        // Delete old marker record and save new one with full details
        await saveMarkerToDatabase(lat, lon, 'Location: ' + (address || city || country), address, city, country, postcode);
    }
}

// Display location information
function displayLocationInfo(lat, lon, info) {
    const infoPanel = document.getElementById('location-info');
    if (infoPanel) {
        infoPanel.innerHTML = `
            <h4>📍 Location Information</h4>
            <p><strong>Address:</strong> ${info.address}</p>
            <p><strong>Coordinates:</strong> ${lat.toFixed(6)}, ${lon.toFixed(6)}</p>
            ${info.city ? `<p><strong>City:</strong> ${info.city}</p>` : ''}
            ${info.country ? `<p><strong>Country:</strong> ${info.country}</p>` : ''}
            ${info.postcode ? `<p><strong>Postcode:</strong> ${info.postcode}</p>` : ''}
        `;
    }
}

// Update coordinates display
function updateCoordinatesDisplay(lat, lon) {
    const coordsElement = document.getElementById('coordinates');
    if (coordsElement) {
        if (lat && lon) {
            coordsElement.innerHTML = `
                <div class="coord-item">
                    <div class="coord-label">Latitude</div>
                    <div class="coord-value">${lat.toFixed(8)}</div>
                </div>
                <div class="coord-item">
                    <div class="coord-label">Longitude</div>
                    <div class="coord-value">${lon.toFixed(8)}</div>
                </div>
                <div class="coord-item">
                    <div class="coord-label">Zoom Level</div>
                    <div class="coord-value">${map.getZoom()}</div>
                </div>
                <div class="coord-item">
                    <div class="coord-label">Markers</div>
                    <div class="coord-value">${markers.length}</div>
                </div>
            `;
        } else {
            const center = map.getCenter();
            coordsElement.innerHTML = `
                <div class="coord-item">
                    <div class="coord-label">Center Latitude</div>
                    <div class="coord-value">${center.lat.toFixed(8)}</div>
                </div>
                <div class="coord-item">
                    <div class="coord-label">Center Longitude</div>
                    <div class="coord-value">${center.lng.toFixed(8)}</div>
                </div>
                <div class="coord-item">
                    <div class="coord-label">Zoom Level</div>
                    <div class="coord-value">${map.getZoom()}</div>
                </div>
                <div class="coord-item">
                    <div class="coord-label">Markers</div>
                    <div class="coord-value">${markers.length}</div>
                </div>
            `;
        }
    }
}

// Handle map move
function onMapMove(e) {
    updateCoordinatesDisplay();
}

// Handle map zoom
function onMapZoom(e) {
    updateCoordinatesDisplay();
}

// Search for a location using Python backend
async function searchLocation() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput || !searchInput.value.trim()) {
        alert('Please enter a location to search');
        return;
    }

    const query = searchInput.value.trim();
    
    try {
        showLoadingState(true);
        
        const response = await fetch('/HomeScreen/api/search-location/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query
            })
        });
        
        const data = await response.json();
        showLoadingState(false);
        
        if (data.success && data.results.length > 0) {
            const result = data.results[0];
            
            // Center map on result
            map.setView([result.lat, result.lon], 14);
            addMarker(result.lat, result.lon, query);
            
            // Display location info
            displayLocationInfo(result.lat, result.lon, {
                address: result.address || result.name,
                city: result.city || 'N/A',
                country: result.country || 'N/A'
            });
        } else {
            alert(data.error || 'Location not found. Try a different search.');
        }
    } catch (error) {
        showLoadingState(false);
        console.error('Search error:', error);
        alert('Error searching for location');
    }
}

// Calculate distance between two markers
async function calculateDistance(lat2, lon2) {
    if (markers.length < 1) {
        alert('Please add another marker first');
        return;
    }
    
    if (!currentMarker && markers.length > 0) {
        const firstMarker = markers[0];
        lat2 = firstMarker.lat;
        lon2 = firstMarker.lon;
    }
    
    // Get first marker coordinates
    const firstMarker = markers[0];
    const lat1 = firstMarker.lat;
    const lon1 = firstMarker.lon;
    
    try {
        const response = await fetch('/HomeScreen/api/calculate-distance/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lat1: lat1,
                lon1: lon1,
                lat2: lat2,
                lon2: lon2
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Distance: ${data.distance_km} km (${data.distance_miles} miles)`);
        }
    } catch (error) {
        console.error('Distance calculation error:', error);
    }
}

// Clear all markers
function clearMarkers() {
    markers.forEach(item => {
        map.removeLayer(item.marker);
    });
    markers = [];
    currentMarker = null;
    updateCoordinatesDisplay();
    
    const infoPanel = document.getElementById('location-info');
    if (infoPanel) {
        infoPanel.innerHTML = '';
    }
}

// Copy coordinates to clipboard
function copyCoordinates(lat, lon) {
    const coords = `${lat.toFixed(8)}, ${lon.toFixed(8)}`;
    navigator.clipboard.writeText(coords).then(() => {
        alert('Coordinates copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Center map on current location
function centerOnLocation() {
    if (navigator.geolocation) {
        showLoadingState(true);
        navigator.geolocation.getCurrentPosition(
            (position) => {
                showLoadingState(false);
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                
                map.setView([lat, lon], 14);
                addMarker(lat, lon, 'Your Location');
                getLocationDetailsFromPython(lat, lon);
            },
            (error) => {
                showLoadingState(false);
                console.error('Geolocation error:', error);
                alert('Unable to get your current location');
            }
        );
    } else {
        alert('Geolocation is not supported by your browser');
    }
}

// Show/hide loading state
function showLoadingState(show) {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }
}

// Navigate to preset city
function navigateToCity(cityName) {
    const city = mapConfig.cities.find(c => c.name === cityName);
    if (city) {
        map.setView([city.lat, city.lon], 12);
        addMarker(city.lat, city.lon, city.name);
    }
}

// Save marker to database
async function saveMarkerToDatabase(lat, lon, title, address = '', city = '', country = '', postcode = '') {
    try {
        const response = await fetch('/HomeScreen/api/save-marker/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                latitude: lat,
                longitude: lon,
                address: address,
                city: city,
                country: country,
                postcode: postcode
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Marker saved to database:', data.marker);
        } else {
            console.error('Error saving marker:', data.error);
        }
    } catch (error) {
        console.error('Error saving marker to database:', error);
    }
}

// Load all saved markers from database
async function loadSavedMarkers() {
    try {
        const response = await fetch('/HomeScreen/api/get-markers/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            data.markers.forEach(marker => {
                addMarker(marker.latitude, marker.longitude, marker.title);
            });
            console.log(`Loaded ${data.count} markers from database`);
        }
    } catch (error) {
        console.error('Error loading markers from database:', error);
    }
}

// Delete marker from database
async function deleteMarkerFromDatabase(markerId) {
    try {
        const response = await fetch('/HomeScreen/api/delete-marker/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                marker_id: markerId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Marker deleted from database');
        }
    } catch (error) {
        console.error('Error deleting marker:', error);
    }
}

// Initialize map when DOM is ready
document.addEventListener('DOMContentLoaded', initMap);

// Export functions for global access
window.initMap = initMap;
window.searchLocation = searchLocation;
window.clearMarkers = clearMarkers;
window.copyCoordinates = copyCoordinates;
window.centerOnLocation = centerOnLocation;
window.calculateDistance = calculateDistance;
window.navigateToCity = navigateToCity;
window.saveMarkerToDatabase = saveMarkerToDatabase;
window.loadSavedMarkers = loadSavedMarkers;
window.deleteMarkerFromDatabase = deleteMarkerFromDatabase;

