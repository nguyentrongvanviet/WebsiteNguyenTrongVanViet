# Interactive Map Integration Guide

## Overview
Your website now has a fully functional interactive map built with:
- **Leaflet.js** - Free, open-source mapping library
- **Geoapify API** - For location search and reverse geocoding (optional)
- **Django** - Backend framework

## Features Implemented

### 1. Interactive Map Display
- Full-screen responsive map centered on Ho Chi Minh City
- Click anywhere on the map to add markers
- Smooth zoom and pan controls
- Beautiful popup information on marker click

### 2. Location Search
- Search for locations by name (e.g., "Paris", "Tokyo", "New York")
- Auto-focus and center map on search results
- Reverse geocoding to get address from coordinates

### 3. Quick Navigation Buttons
- Ho Chi Minh City
- Hanoi
- Can Tho
- Use My Location (browser geolocation)

### 4. Real-time Coordinate Display
- Shows current map center coordinates
- Displays latitude and longitude with 8 decimal precision
- Shows current zoom level
- Counts total markers on map

### 5. Location Information Panel
- Displays full address
- Shows city and country
- Includes postal code
- Updates dynamically when markers are clicked

## File Structure

```
HomeScreen/
├── static/
│   ├── css/
│   │   └── map.css           # Styling for map and controls
│   └── js/
│       └── map.js            # Interactive map functionality
└── templates/
    └── Welcome.html          # Main template with map
```

## Getting Started

### 1. Obtain a Geoapify API Key (Optional but Recommended)

To enable full features like location search and reverse geocoding:

1. Go to https://myprojects.geoapify.com/
2. Sign up for a free account
3. Create a new project
4. Copy your API key
5. In `HomeScreen/static/js/map.js`, find line with:
   ```javascript
   const GEOAPIFY_API_KEY = 'YOUR_API_KEY';
   ```
6. Replace `'YOUR_API_KEY'` with your actual API key

### 2. Run Your Django Server

```bash
# Navigate to project directory
cd v:\WebSiteNguyenTrongVanViet

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### 3. Access the Map

Navigate to: `http://localhost:8000/Welcome/`

## User Interactions

### Adding Markers
- **Click anywhere on the map** → Marker appears with popup
- Popup shows coordinates and address (if API key configured)
- Button to copy coordinates to clipboard

### Searching Locations
1. Type location name in search box
2. Click "Search" button
3. Map centers on first search result
4. Marker added automatically

### Navigation
- Use preset buttons for quick access to Vietnamese cities
- Use mouse to pan the map
- Scroll wheel to zoom in/out

### Clearing Map
- Click "Clear All Markers" to remove all markers
- Returns to default view

## Customization

### Change Default Location
Edit `map.js`:
```javascript
const DEFAULT_COORDS = { lat: 10.8231, lon: 106.6797 }; // Your coordinates
const DEFAULT_ZOOM = 12; // Zoom level (1-19)
```

### Modify Map Appearance
Edit `map.css` to customize:
- Colors (#667eea is primary color)
- Button styles
- Coordinate display layout
- Responsive breakpoints

### Add More Quick Navigation Buttons
In `Welcome.html`, duplicate and modify:
```html
<button class="map-btn" onclick="map.setView([LAT, LON], 12)">📍 City Name</button>
```
Replace LAT and LON with desired coordinates

## API Endpoints Used

### Geoapify Reverse Geocoding
```
GET https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={apiKey}
```
Converts coordinates to address

### Geoapify Forward Geocoding
```
GET https://api.geoapify.com/v1/geocode/search?text={query}&apiKey={apiKey}
```
Converts address/place name to coordinates

## Browser Requirements

- Modern browser with ES6 support
- Cookie/localStorage support
- For "Use My Location": HTTPS or localhost

## Troubleshooting

### Map doesn't load
- Check browser console for errors (F12)
- Verify Django static files are served correctly
- Ensure Leaflet CDN is accessible

### Search doesn't work
- Confirm Geoapify API key is correct
- Check API key hasn't expired or hit rate limit
- Verify internet connection

### Location permission denied
- Allow browser permission when prompted
- Try HTTPS connection
- Use manual search instead

## Future Enhancements

Consider adding:
1. **Route Planning** - Use Geoapify routing API
2. **Distance Calculation** - Between markers
3. **Marker Clustering** - For many markers
4. **Heat Maps** - Visualize marker density
5. **Database Storage** - Save markers to Django models
6. **Share Locations** - Generate shareable links
7. **Multiple Map Layers** - Satellite, terrain views
8. **Drawing Tools** - Draw shapes on map

## Security Notes

- Keep Geoapify API key safe in production
- Consider using Django environment variables for API keys
- Implement rate limiting on location search
- Validate all user inputs server-side if storing data

## Resources

- Leaflet Documentation: https://leafletjs.com/
- Geoapify API Docs: https://www.geoapify.com/
- OpenStreetMap: https://www.openstreetmap.org/
- Django Static Files: https://docs.djangoproject.com/en/5.2/howto/static-files/

---

**Created:** November 2025
**Built by:** GitHub Copilot
**License:** Open Source
