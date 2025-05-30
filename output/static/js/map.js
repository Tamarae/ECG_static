// Enhanced Map Handler - Fixes coordinate jumping and improves map interactions

    class ECGMapHandler {
        constructor() {
            this.map = null;
            this.mapData = [];
            this.allMarkers = [];
            this.activeFilter = null;
            this.originalBounds = null;
            this.mapboxToken = 'pk.eyJ1IjoidGFtYXJhZTI0IiwiYSI6ImNtYjB0czAwdDB2OGcybXNoejI2eGp6cTYifQ.AesnE6yuzOEmJIBIWSH6ag';

            // Bind methods to preserve 'this' context
            this.initializeMap = this.initializeMap.bind(this);
            this.createAllMarkers = this.createAllMarkers.bind(this);
            this.applyLanguageFilter = this.applyLanguageFilter.bind(this);
            this.resetFilter = this.resetFilter.bind(this);
        }

        async initializeMap() {
            try {
                console.log('🗺️ Initializing ECG Map...');

                mapboxgl.accessToken = this.mapboxToken;

                const response = await fetch('map-data.json');
                this.mapData = await response.json();

                if (!this.mapData || this.mapData.length === 0) {
                    console.error('No map data found');
                    return;
                }

                // Calculate and store original bounds
                this.calculateOriginalBounds();

                // Create map with fixed bounds
                this.map = new mapboxgl.Map({
                    container: 'inscriptions-map',
                    style: 'mapbox://styles/mapbox/light-v11',
                    bounds: this.originalBounds,
                    fitBoundsOptions: {
                        padding: 40,
                        maxZoom: 10  // Prevent excessive zoom
                    }
                });

                // Add navigation controls
                this.map.addControl(new mapboxgl.NavigationControl({
                    showCompass: false,
                    showZoom: true,
                    visualizePitch: false
                }), 'top-right');

                // Initialize markers and interactions when map loads
                this.map.on('load', () => {
                    console.log('✅ Map loaded successfully');
                    this.createAllMarkers();
                    this.setupLegendInteractivity();
                    this.setupMapEventHandlers();
                });

                // Prevent map from jumping on resize
                this.map.on('resize', () => {
                    if (this.originalBounds && !this.activeFilter) {
                        setTimeout(() => {
                            this.map.fitBounds(this.originalBounds, {
                                padding: 40,
                                duration: 0  // No animation to prevent jumping
                            });
                        }, 100);
                    }
                });

            } catch (error) {
                console.error('❌ Error loading map:', error);
            }
        }

        calculateOriginalBounds() {
            let minLat = Infinity, maxLat = -Infinity;
            let minLon = Infinity, maxLon = -Infinity;

            this.mapData.forEach(location => {
                const lat = parseFloat(location.lat);
                const lon = parseFloat(location.lon);

                if (!isNaN(lat) && !isNaN(lon)) {
                    minLat = Math.min(minLat, lat);
                    maxLat = Math.max(maxLat, lat);
                    minLon = Math.min(minLon, lon);
                    maxLon = Math.max(maxLon, lon);
                }
            });

            // Store original bounds with slight padding
            this.originalBounds = [
                [minLon - 0.5, minLat - 0.5],
                [maxLon + 0.5, maxLat + 0.5]
            ];

            console.log('📍 Original bounds calculated:', this.originalBounds);
        }

        setupMapEventHandlers() {
            // Prevent coordinates from jumping when popups open/close
            this.map.on('popup.open', () => {
                // Store current center to prevent jumping
                this.currentCenter = this.map.getCenter();
                this.currentZoom = this.map.getZoom();
            });

            this.map.on('popup.close', () => {
                // Restore position if it jumped
                setTimeout(() => {
                    if (this.currentCenter && this.currentZoom) {
                        const currentPos = this.map.getCenter();
                        const distance = this.calculateDistance(currentPos, this.currentCenter);

                        // If map jumped significantly, restore position
                        if (distance > 0.1) {
                            this.map.easeTo({
                                center: this.currentCenter,
                                zoom: this.currentZoom,
                                duration: 300
                            });
                        }
                    }
                }, 50);
            });
        }

        calculateDistance(coord1, coord2) {
            const dx = coord1.lng - coord2.lng;
            const dy = coord1.lat - coord2.lat;
            return Math.sqrt(dx * dx + dy * dy);
        }

        getEnhancedLocationLanguages(location) {
            const languages = {};

            location.inscriptions.forEach(insc => {
                let detectedLang = insc.language || 'unknown';

                if (detectedLang === 'unknown' || !detectedLang) {
                    detectedLang = this.detectLanguageFromText(insc.title);
                }

                languages[detectedLang] = (languages[detectedLang] || 0) + 1;
            });

            return languages;
        }

        detectLanguageFromText(text) {
            if (!text) return 'unknown';

            // Georgian detection
            if (/[Ⴀ-ჿⴀ-⴯Ა-Ჿ]/.test(text)) {
                return 'ka';
            }

            // Greek detection
            if (/[Ͱ-Ͽἀ-῿]/.test(text)) {
                return 'grc';
            }

            // Armenian detection
            if (/[԰-֏ﬓ-ﬗ]/.test(text)) {
                return 'hy';
            }

            // Hebrew detection
            if (/[֐-׿]/.test(text)) {
                return 'he';
            }

            // Arabic detection
            if (/[؀-ۿ]/.test(text)) {
                return 'ar';
            }

            // Cyrillic detection
            if (/[Ѐ-ӿ]/.test(text)) {
                return 'ru';
            }

            // Latin detection
            if (/[a-zA-Z]/.test(text)) {
                return 'other';
            }

            return 'unknown';
        }

        getPrimaryLanguage(languages) {
            if (!languages || Object.keys(languages).length === 0) return 'other';

            const entries = Object.entries(languages);

            if (entries.length === 1) {
                return entries[0][0];
            }

            if (entries.length > 1) {
                const total = entries.reduce((sum, entry) => sum + entry[1], 0);
                const dominant = entries.reduce((a, b) => a[1] > b[1] ? a : b);

                if (dominant[1] / total > 0.8) {
                    return dominant[0];
                }

                return 'mixed';
            }

            return entries[0][0];
        }

        getLanguageColor(languages) {
            const colors = {
                ka: '#27ae60',    // Georgian - Bright Green
                grc: '#3498db',   // Greek - Bright Blue
                hy: '#e67e22',    // Armenian - Bright Orange
                he: '#9b59b6',    // Hebrew - Purple
                ar: '#e74c3c',    // Arabic - Red
                ru: '#f39c12',    // Cyrillic - Orange
                other: '#7f8c8d', // Other - Gray
                mixed: '#9b59b6', // Mixed - Purple
                unknown: '#95a5a6' // Unknown - Light Gray
            };

            const primaryLang = this.getPrimaryLanguage(languages);
            return colors[primaryLang] || colors.other;
        }

        createAllMarkers() {
            console.log('🗺️ Creating markers...');

            // Clear existing markers
            this.allMarkers.forEach(markerData => markerData.marker.remove());
            this.allMarkers = [];

            const languageStats = { ka: 0, grc: 0, hy: 0, mixed: 0, other: 0, unknown: 0 };

            this.mapData.forEach(location => {
                const lat = parseFloat(location.lat);
                const lon = parseFloat(location.lon);

                if (isNaN(lat) || isNaN(lon)) return;

                const languageData = this.getEnhancedLocationLanguages(location);
                const primaryLanguage = this.getPrimaryLanguage(languageData);
                const color = this.getLanguageColor(languageData);
                const size = Math.min(Math.max(12 + location.count * 2, 16), 32);

                // Update stats
                languageStats[primaryLanguage] = (languageStats[primaryLanguage] || 0) + location.count;

                // Create marker element with fixed positioning
                const markerElement = document.createElement('div');
                markerElement.className = 'modern-marker';
                markerElement.style.cssText = `
                    width: ${size}px;
                    height: ${size}px;
                    background: ${color};
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: ${Math.max(10, size * 0.4)}px;
                    font-weight: 500;
                    color: white;
                    cursor: pointer;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                    border: 2px solid rgba(255,255,255,0.9);
                    position: relative;
                    z-index: 1;
                `;
                markerElement.textContent = location.count;

                // Store language data
                markerElement.dataset.languages = JSON.stringify(languageData);
                markerElement.dataset.primaryLanguage = primaryLanguage;

                // Improved hover effects
                markerElement.addEventListener('mouseenter', () => {
                    markerElement.style.transform = 'scale(1.1)';
                    markerElement.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                    markerElement.style.zIndex = '10';
                });

                markerElement.addEventListener('mouseleave', () => {
                    if (!markerElement.classList.contains('popup-open')) {
                        markerElement.style.transform = 'scale(1)';
                        markerElement.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                        markerElement.style.zIndex = '1';
                    }
                });

                // Create marker with anchor set to center-bottom
                const marker = new mapboxgl.Marker({
                    element: markerElement,
                    anchor: 'center'
                }).setLngLat([lon, lat]).addTo(this.map);

                // Create popup with better positioning
                const popupHTML = this.createEnhancedPopup(location, languageData);
                const popup = new mapboxgl.Popup({
                    offset: [0, -size/2 - 10],
                    closeButton: true,
                    closeOnClick: false,
                    anchor: 'bottom',
                    maxWidth: '320px'
                }).setHTML(popupHTML);

                // Improved click handling
                markerElement.addEventListener('click', (e) => {
                    e.stopPropagation();

                    // Close other popups
                    this.closeAllPopups();

                    // Mark this marker as having popup open
                    markerElement.classList.add('popup-open');

                    // Open popup
                    popup.addTo(this.map);

                    // Handle popup close
                    popup.on('close', () => {
                        markerElement.classList.remove('popup-open');
                        markerElement.style.transform = 'scale(1)';
                        markerElement.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
                        markerElement.style.zIndex = '1';
                    });
                });

                // Store marker data
                this.allMarkers.push({
                    marker: marker,
                    element: markerElement,
                    popup: popup,
                    languages: languageData,
                    primaryLanguage: primaryLanguage,
                    location: location
                });
            });

            this.updateLanguageCounts(languageStats);
            console.log('✅ Created', this.allMarkers.length, 'markers');
        }

        closeAllPopups() {
            this.allMarkers.forEach(markerData => {
                if (markerData.popup.isOpen()) {
                    markerData.popup.remove();
                }
                markerData.element.classList.remove('popup-open');
            });
        }

        createEnhancedPopup(location, languageData) {
            const langSummary = Object.entries(languageData)
                .map(([lang, count]) => `${this.getLanguageName(lang)}: ${count}`)
                .join(', ');

            let inscriptionsList = '';
            const maxShow = 4;
            const inscriptions = location.inscriptions;

            for (let i = 0; i < Math.min(maxShow, inscriptions.length); i++) {
                const insc = inscriptions[i];
                const detectedLang = this.detectLanguageFromText(insc.title);
                const langClass = detectedLang === 'ka' ? 'georgian-text' : '';
                inscriptionsList += `
                    <a href="${insc.url}" class="popup-inscription ${langClass}">
                        ${insc.title}
                    </a>
                `;
            }

            if (inscriptions.length > maxShow) {
                inscriptionsList += `
                    <div class="popup-more">
                        +${inscriptions.length - maxShow} more inscriptions
                    </div>
                `;
            }

            return `
                <div class="modern-popup">
                    <div class="popup-header">
                        <h3>${location.place}</h3>
                        <div class="popup-meta">
                            <span class="count">${location.count} inscriptions</span>
                            <span class="languages">${langSummary}</span>
                        </div>
                    </div>
                    <div class="popup-inscriptions">
                        ${inscriptionsList}
                    </div>
                </div>
            `;
        }

        getLanguageName(code) {
            const names = {
                ka: 'Georgian',
                grc: 'Greek',
                hy: 'Armenian',
                he: 'Hebrew',
                ar: 'Arabic',
                ru: 'Cyrillic',
                other: 'Other',
                unknown: 'Unknown',
                mixed: 'Mixed'
            };
            return names[code] || code;
        }

        updateLanguageCounts(stats) {
            Object.entries(stats).forEach(([lang, count]) => {
                const countElement = document.getElementById(`count-${lang}`);
                if (countElement) {
                    countElement.textContent = count;
                    countElement.style.display = count > 0 ? 'inline' : 'none';
                }
            });
        }

        setupLegendInteractivity() {
            const legendItems = document.querySelectorAll('.clickable-legend');
            const resetButton = document.getElementById('resetMapFilter');

            legendItems.forEach(item => {
                item.addEventListener('click', () => {
                    const language = item.dataset.language;

                    if (this.activeFilter === language) {
                        this.resetFilter();
                    } else {
                        this.applyLanguageFilter(language);

                        legendItems.forEach(li => li.classList.remove('active'));
                        item.classList.add('active');
                        resetButton.style.display = 'inline-block';
                        this.activeFilter = language;
                    }
                });
            });

            resetButton.addEventListener('click', this.resetFilter);
        }

        applyLanguageFilter(targetLanguage) {
            console.log('🔍 Applying filter:', targetLanguage);

            // Close all popups first
            this.closeAllPopups();

            let visibleMarkers = [];

            this.allMarkers.forEach(markerData => {
                const shouldShow = targetLanguage === 'mixed'
                    ? Object.keys(markerData.languages).length > 1
                    : markerData.primaryLanguage === targetLanguage;

                if (shouldShow) {
                    markerData.marker.addTo(this.map);
                    markerData.element.style.opacity = '1';
                    markerData.element.style.transform = 'scale(1.05)';
                    visibleMarkers.push(markerData);
                } else {
                    markerData.marker.remove();
                }
            });

            // Fit bounds to visible markers only
            if (visibleMarkers.length > 0) {
                const bounds = new mapboxgl.LngLatBounds();
                visibleMarkers.forEach(markerData => {
                    bounds.extend([markerData.location.lon, markerData.location.lat]);
                });

                this.map.fitBounds(bounds, {
                    padding: 50,
                    maxZoom: 10,
                    duration: 800
                });
            }
        }

        resetFilter() {
            console.log('🔄 Resetting filter');

            // Close all popups
            this.closeAllPopups();

            // Show all markers
            this.allMarkers.forEach(markerData => {
                markerData.marker.addTo(this.map);
                markerData.element.style.opacity = '1';
                markerData.element.style.transform = 'scale(1)';
            });

            // Reset UI
            document.querySelectorAll('.clickable-legend').forEach(item => {
                item.classList.remove('active');
            });
            document.getElementById('resetMapFilter').style.display = 'none';
            this.activeFilter = null;

            // Return to original bounds
            if (this.originalBounds) {
                this.map.fitBounds(this.originalBounds, {
                    padding: 40,
                    duration: 800
                });
            }
        }
    }

    // Initialize map when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        const mapHandler = new ECGMapHandler();
        mapHandler.initializeMap();
    });
