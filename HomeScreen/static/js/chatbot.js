// Chatbot functionality
let chatHistory = [];

document.addEventListener('DOMContentLoaded', function() {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    
    // Toggle chat window
    chatToggleBtn.addEventListener('click', function() {
        if (chatWindow.style.display === 'none') {
            chatWindow.style.display = 'flex';
            chatToggleBtn.style.display = 'none';
            chatInput.focus();
        }
    });
    
    // Close chat window
    chatCloseBtn.addEventListener('click', function() {
        chatWindow.style.display = 'none';
        chatToggleBtn.style.display = 'flex';
    });
    
    // Send message on button click
    chatSendBtn.addEventListener('click', sendMessage);
    
    // Send message on Enter key
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Send to backend
    processUserInput(message);
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    if (sender === 'bot' && message.includes('\n')) {
        // Handle multiline bot messages
        const lines = message.split('\n');
        for (const line of lines) {
            if (line.trim()) {
                const p = document.createElement('p');
                
                // Handle lists
                if (line.trim().startsWith('•') || line.trim().match(/^\d+\./)) {
                    p.innerHTML = line;
                    p.style.margin = '2px 0';
                } else if (line.includes('📍') || line.includes('🗺️') || line.includes('📏') || line.includes('⏱️')) {
                    // Handle emoji lines
                    p.innerHTML = line;
                    p.style.fontWeight = 'bold';
                } else {
                    p.textContent = line;
                }
                
                messageDiv.appendChild(p);
            }
        }
    } else {
        const p = document.createElement('p');
        p.textContent = message;
        messageDiv.appendChild(p);
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    chatHistory.push({
        role: sender === 'user' ? 'user' : 'assistant',
        content: message
    });
}

function showLoadingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message bot-message';
    loadingDiv.id = 'loading-indicator';
    loadingDiv.innerHTML = '<div class="loading-indicator"><div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div></div>';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingIndicator() {
    const loadingDiv = document.getElementById('loading-indicator');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

async function processUserInput(userMessage) {
    try {
        // Show a quick response first
        const quickResponse = getQuickResponse(userMessage);
        if (quickResponse) {
            addMessageToChat(quickResponse, 'bot');
        }
        
        // Send to backend to process with Gemini
        const response = await fetch('/HomeScreen/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userMessage,
                history: chatHistory
            })
        });
        
        removeLoadingIndicator();
        
        const data = await response.json();
        
        if (data.success) {
            // Only add bot response if it's different from quick response
            if (!quickResponse || data.response !== quickResponse) {
                addMessageToChat(data.response, 'bot');
            }
            
            // If there's action data, process it
            if (data.action === 'distance') {
                handleDistanceRequest(data);
            } else if (data.action === 'journey') {
                handleJourneyRequest(data, userMessage);
            }
        } else {
            addMessageToChat('Sorry, there was an error processing your request: ' + data.error, 'bot');
        }
    } catch (error) {
        removeLoadingIndicator();
        console.error('Chat error:', error);
        addMessageToChat('Sorry, I encountered an error. Please check your internet connection and try again.', 'bot');
    }
}

function getQuickResponse(message) {
    const lower = message.toLowerCase();
    
    // Quick responses for common patterns
    if (lower.includes('distance') || lower.includes('how far')) {
        return "🔍 Let me calculate the distance for you...";
    }
    
    if (lower.includes('journey') || lower.includes('plan') || lower.includes('visit')) {
        return "🗺️ Let me plan a great journey for you...";
    }
    
    if (lower.includes('hello') || lower.includes('hi')) {
        return "👋 Hello! How can I help you today?";
    }
    
    return null;
}

async function handleDistanceRequest(data) {
    try {
        // Show processing message
        addMessageToChat("🔄 Calculating route and distance...", 'bot');
        
        const payload = {
            start: data.start_location,
            end: data.end_location
        };
        
        // If multiple locations were found, pass them all
        if (data.all_locations && data.all_locations.length > 2) {
            payload.all_locations = data.all_locations;
        }
        
        const response = await fetch('/HomeScreen/api/calculate-route/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        const routeData = await response.json();
        
        if (routeData.success) {
            const distance = routeData.distance_km;
            const duration = routeData.duration;
            const numStops = routeData.num_stops || 2;
            
            let result = `✅ Route calculated successfully!\n\n`;
            
            // Show waypoints
            if (routeData.waypoints && routeData.waypoints.length > 0) {
                result += `🗺️ Route: `;
                result += routeData.waypoints.map(wp => wp.name).join(' → ');
                result += `\n\n`;
            }
            
            result += `📏 Total Distance: ${distance} km\n`;
            result += `⏱️ Estimated Time: ${duration}\n`;
            result += `🚩 Number of stops: ${numStops}`;
            
            addMessageToChat(result, 'bot');
            
            // Draw route on map if available
            if (routeData.route_coordinates && routeData.route_coordinates.length > 0) {
                drawRouteOnMap(routeData.route_coordinates, routeData.waypoints);
                addMessageToChat("📍 Route has been displayed on the map!", 'bot');
            }
        } else {
            addMessageToChat('❌ Could not calculate route: ' + routeData.error + '\n\nPlease try with more specific location names.', 'bot');
        }
    } catch (error) {
        console.error('Distance calculation error:', error);
        addMessageToChat('❌ Error calculating distance. Please check your internet connection and try again.', 'bot');
    }
}

async function handleJourneyRequest(data, originalMessage) {
    try {
        // Show processing message
        addMessageToChat("🔍 Searching for the best places to visit...", 'bot');
        clearJourneyPanel();
        
        const response = await fetch('/HomeScreen/api/plan-journey/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: originalMessage,
                start_location: data.start_location,
                categories: data.categories,
                preferences: data.preferences
            })
        });
        
        const journeyData = await response.json();
        if (journeyData.success && Array.isArray(journeyData.journey) && journeyData.journey.length > 0) {
            const summary = journeyData.summary || {};
            const startName = (journeyData.start && journeyData.start.name) || data.start_location || 'your starting point';
            const stopCount = summary.stops_planned || journeyData.journey.length;
            const distanceKm = typeof summary.total_distance_km === 'number' ? summary.total_distance_km : null;
            const durationMinutes = typeof summary.estimated_total_minutes === 'number' ? summary.estimated_total_minutes : null;
            let responseText = `✅ Planned ${stopCount} stops starting from ${startName}.\n`;
            if (distanceKm !== null) {
                responseText += `📏 Distance: ~${distanceKm} km\n`;
            }
            if (durationMinutes !== null) {
                responseText += `⏱️ Estimated duration: ~${formatMinutes(durationMinutes)}\n`;
            }
            if (typeof summary.average_stop_minutes === 'number') {
                responseText += `🛑 Avg stay per stop: ~${formatMinutes(summary.average_stop_minutes)}\n`;
            }
            if (typeof summary.average_drive_leg_minutes === 'number') {
                responseText += `🚗 Avg travel between stops: ~${formatMinutes(summary.average_drive_leg_minutes)}\n`;
            }
            if (summary.must_visit_satisfied && summary.must_visit_satisfied.length) {
                responseText += `⭐ Must-visit covered: ${summary.must_visit_satisfied.join(', ')}\n`;
            }
            responseText += '\nStops:\n';
            journeyData.journey.forEach((stop) => {
                responseText += `${stop.order}. ${stop.name}`;
                if (stop.category) {
                    responseText += ` (${stop.category})`;
                }
                if (stop.must_visit) {
                    responseText += ' ⭐';
                }
                responseText += '\n';
            });
            responseText += '\n📍 Journey displayed on the map and in the side panel.';
            addMessageToChat(responseText.trim(), 'bot');
            displayBestJourneyOnMap(journeyData);
            return;
        }

        if (journeyData.success && journeyData.routes && journeyData.routes.length > 0) {
            // Legacy response path
            let response_text = '🗺️ Here are your journey options:\n\n';
            journeyData.routes.forEach((route, index) => {
                response_text += `🚩 Option ${index + 1}: ${route.category.toUpperCase()}\n`;
                response_text += `📍 ${route.description}\n`;
                response_text += `📏 Distance: ~${route.total_distance}km\n`;
                response_text += `⏱️ Time: ~${route.total_time}\n\n`;
            });
            response_text += "✨ Routes are displayed on the map with different colors!";
            addMessageToChat(response_text, 'bot');
            displayJourneyRoutesOnMap(journeyData.routes);
            return;
        }

        const errorMsg = journeyData.error || 'No suitable places found';
        addMessageToChat(`❌ Could not plan journey: ${errorMsg}\n\nTry specifying a different location or category (restaurant, cafe, shopping, park, museum).`, 'bot');
    } catch (error) {
        console.error('Journey planning error:', error);
        addMessageToChat('❌ Error planning journey. Please check your internet connection and try again.', 'bot');
    }
}

// Store route layers for cleanup
let currentRouteLayers = [];

function drawRouteOnMap(coordinates, waypoints) {
    // Clear previous routes
    clearPreviousRoutes();
    
    // Draw a line on the map from start to end
    if (typeof map !== 'undefined' && coordinates && coordinates.length > 0) {
        const latlngs = coordinates.map(coord => [coord.lat, coord.lon]);
        const polyline = L.polyline(latlngs, {
            color: '#667eea',
            weight: 4,
            opacity: 0.8,
            smoothFactor: 1
        }).addTo(map);
        
        currentRouteLayers.push(polyline);
        
        // Add markers for waypoints if provided
        if (waypoints && waypoints.length > 0) {
            waypoints.forEach((wp, index) => {
                const isStart = !!wp.isStart || index === 0;
                const isEnd = !!wp.isEnd || (!isStart && index === waypoints.length - 1);
                const marker = L.marker([wp.lat, wp.lon], {
                    title: `${isStart ? 'Start: ' : ''}${wp.name}`
                }).addTo(map);
                
                let popupHtml = `<strong>${isStart ? 'Start: ' : ''}${wp.name}</strong>`;
                if (wp.category) {
                    popupHtml += `<br>Category: ${wp.category}`;
                }
                if (wp.notes) {
                    popupHtml += `<br>${wp.notes}`;
                }
                if (wp.stay_minutes) {
                    popupHtml += `<br>Stay ~${formatMinutes(wp.stay_minutes)}`;
                }
                marker.bindPopup(popupHtml);
                currentRouteLayers.push(marker);
                
                // Add numbered divIcon for better visibility
                const labelValue = isStart ? 'S' : (isEnd ? 'F' : (wp.order || index + 1));
                const color = isStart ? '#4CAF50' : (isEnd ? '#F44336' : '#FF9800');
                const numberIcon = L.divIcon({
                    html: `<div style="background: ${color}; color: white; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">${labelValue}</div>`,
                    className: 'route-marker',
                    iconSize: [25, 25],
                    iconAnchor: [12, 12]
                });
                
                const numberMarker = L.marker([wp.lat, wp.lon], { icon: numberIcon }).addTo(map);
                currentRouteLayers.push(numberMarker);
            });
        }
        
        // Fit map to route
        try {
            map.fitBounds(polyline.getBounds(), { padding: [20, 20] });
        } catch (e) {
            console.log('Could not fit map bounds:', e);
        }
    }
}

function displayJourneyRoutesOnMap(routes) {
    // Clear previous routes
    clearPreviousRoutes();
    clearJourneyPanel();
    
    // Display multiple route options on the map
    routes.forEach((route, index) => {
        if (route.coordinates && route.coordinates.length > 0) {
            const latlngs = route.coordinates.map(coord => [coord.lat, coord.lon]);
            const colors = ['#667eea', '#764ba2', '#FF6B6B', '#4CAF50', '#FF9800'];
            
            const polyline = L.polyline(latlngs, {
                color: colors[index % colors.length],
                weight: 3,
                opacity: 0.7,
                smoothFactor: 1,
                dashArray: index > 0 ? '8, 8' : null
            }).addTo(map);
            
            currentRouteLayers.push(polyline);
            
            // Add popup with route info
            const popup = L.popup()
                .setLatLng(latlngs[0])
                .setContent(`<strong>Option ${index + 1}: ${route.category}</strong><br>${route.description}<br><small>Distance: ${route.total_distance}km, Time: ${route.total_time}</small>`);
            
            polyline.bindPopup(popup);
            
            // Add markers for places in this route
            route.coordinates.forEach((coord, placeIndex) => {
                const placeMarker = L.circleMarker([coord.lat, coord.lon], {
                    radius: 6,
                    fillColor: colors[index % colors.length],
                    color: 'white',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(map);
                
                currentRouteLayers.push(placeMarker);
                
                // Add place info if available
                if (route.places && route.places[placeIndex]) {
                    const place = route.places[placeIndex];
                    placeMarker.bindPopup(`<strong>${place.title}</strong><br>${place.address || ''}<br>Rating: ${place.rating || 'N/A'}`);
                }
            });
        }
    });
}

function clearPreviousRoutes() {
    // Remove all current route layers
    currentRouteLayers.forEach(layer => {
        try {
            map.removeLayer(layer);
        } catch (e) {
            // Layer might already be removed
        }
    });
    currentRouteLayers = [];
}

function displayBestJourneyOnMap(plan) {
    if (!plan || !plan.journey || plan.journey.length === 0) {
        return;
    }
    const waypoints = [];
    if (plan.start && plan.start.lat && plan.start.lon) {
        waypoints.push({
            name: plan.start.name || 'Starting point',
            lat: plan.start.lat,
            lon: plan.start.lon,
            isStart: true,
            category: 'start'
        });
    }
    plan.journey.forEach((stop, index) => {
        if (stop.lat == null || stop.lon == null) {
            return;
        }
        waypoints.push({
            name: stop.name,
            lat: stop.lat,
            lon: stop.lon,
            category: stop.category,
            notes: stop.notes,
            stay_minutes: stop.stay_minutes,
            order: stop.order,
            isEnd: index === plan.journey.length - 1
        });
    });
    const coordinates = (plan.route_coordinates && plan.route_coordinates.length > 0)
        ? plan.route_coordinates
        : waypoints.map((wp) => ({ lat: wp.lat, lon: wp.lon }));
    drawRouteOnMap(coordinates, waypoints);
    updateJourneyPanel(plan);
}

function updateJourneyPanel(plan) {
    const panel = document.getElementById('journey-panel');
    if (!panel) {
        return;
    }
    panel.classList.remove('hidden');
    const summaryEl = document.getElementById('journey-summary');
    const summary = plan.summary || {};
    const stats = [];
    if (typeof summary.total_distance_km === 'number') {
        stats.push(`Distance ~${summary.total_distance_km} km`);
    }
    if (typeof summary.estimated_total_minutes === 'number') {
        stats.push(`Duration ~${formatMinutes(summary.estimated_total_minutes)}`);
    }
    if (summary.categories_covered && summary.categories_covered.length) {
        stats.push(`Categories: ${summary.categories_covered.join(', ')}`);
    }
    if (summaryEl) {
        summaryEl.textContent = stats.join(' • ');
    }
    const listEl = document.getElementById('journey-stops');
    if (listEl) {
        listEl.innerHTML = '';
        plan.journey.forEach((stop) => {
            const li = document.createElement('li');
            let inner = `<strong>${stop.order}. ${stop.name}${stop.must_visit ? ' ⭐' : ''}</strong>`;
            if (stop.category) {
                inner += ` <span class="journey-stop-category">${stop.category}</span>`;
            }
            if (stop.address) {
                inner += `<div class="journey-stop-meta">${stop.address}</div>`;
            }
            if (stop.notes) {
                inner += `<div class="journey-stop-notes">${stop.notes}</div>`;
            }
            if (typeof stop.rating === 'number') {
                inner += `<div class="journey-stop-meta">Rating ${stop.rating}${stop.reviews ? ` (${stop.reviews} reviews)` : ''}</div>`;
            }
            if (stop.hours) {
                inner += `<div class="journey-stop-meta">Hours ${stop.hours}</div>`;
            }
            if (stop.stay_minutes) {
                inner += `<div class="journey-stop-meta">Stay ~${formatMinutes(stop.stay_minutes)}</div>`;
            }
            if (typeof stop.travel_minutes_from_previous === 'number' && stop.travel_minutes_from_previous >= 0) {
                inner += `<div class="journey-stop-meta">Travel ~${formatMinutes(stop.travel_minutes_from_previous)} from previous</div>`;
            }
            li.innerHTML = inner;
            listEl.appendChild(li);
        });
    }
}

function clearJourneyPanel() {
    const panel = document.getElementById('journey-panel');
    if (panel) {
        panel.classList.add('hidden');
    }
    const summaryEl = document.getElementById('journey-summary');
    if (summaryEl) {
        summaryEl.textContent = '';
    }
    const listEl = document.getElementById('journey-stops');
    if (listEl) {
        listEl.innerHTML = '';
    }
}

function clearJourneyPlan() {
    clearPreviousRoutes();
    clearJourneyPanel();
}

window.clearJourneyPlan = clearJourneyPlan;

function formatMinutes(totalMinutes) {
    const minutes = parseInt(totalMinutes, 10);
    if (isNaN(minutes)) {
        return '';
    }
    const hours = Math.floor(minutes / 60);
    const remaining = minutes % 60;
    if (hours && remaining) {
        return `${hours}h ${remaining}m`;
    }
    if (hours) {
        return `${hours}h`;
    }
    return `${remaining}m`;
}
