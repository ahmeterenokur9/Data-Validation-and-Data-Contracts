// app.js

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element Selection ---
    const connectionStatusEl = document.getElementById('connection-status');
    const statusTextEl = connectionStatusEl.querySelector('.status-text');
    const messageLogEl = document.getElementById('message-log');
    const logPlaceholderEl = document.querySelector('.log-placeholder');

    // Stats counters
    const totalCountEl = document.getElementById('total-count');
    const validatedCountEl = document.getElementById('validated-count');
    const failedCountEl = document.getElementById('failed-count');

    // Filter elements
    const sourceTopicFilterContainer = document.getElementById('source-topic-filter');
    const filterGroupTitle = sourceTopicFilterContainer.previousElementSibling;
    filterGroupTitle.textContent = "Actuator IDs"; // Change filter title

    const statusFilterCheckboxes = document.querySelectorAll('#status-filter input[type="checkbox"]');
    const failedStatusCheckbox = document.querySelector('#status-filter input[value="failed"]');
    const errorTypeFilterGroup = document.getElementById('error-type-filter-group');
    const errorTypeFilterCheckboxes = document.querySelectorAll('#error-type-filter input[type="checkbox"]');
    const clearLogBtn = document.getElementById('clear-log-btn');

    // --- MQTT Settings ---
    const brokerUrl = 'wss://broker.hivemq.com:8884/mqtt';
    // The topics list is now dynamic and will be fetched from the server.
    // const topics = ['/sensor1/validated', '/sensor1/failed', '/sensor2/validated', '/sensor2/failed', '/sensor3/validated', '/sensor3/failed'];
    
    let client;
    let allMessages = []; // Array to store all messages for filtering
    let stats = { total: 0, validated: 0, failed: 0 };
    let validatedTopics = new Set(); // Store validated topics for quick lookup
    let commandValidatedTopics = new Set(); // <-- NEW: For command topics
    let statusValidatedTopics = new Set();  // <-- NEW: For status topics
    let topicToSourceMap = new Map(); // Maps any topic (validated/failed) back to its source topic
    const knownErrorTypes = new Set(); // Will be populated dynamically
    const errorTypeLabels = {}; // To store pretty labels for error types

    /**
     * Creates a user-friendly label from an error type string.
     * Example: 'check_failed:isin' becomes 'Is In Check'
     */
    function formatErrorType(type) {
        if (type.startsWith('check_failed:')) {
            const checkName = type.split(':')[1];
            // Capitalize first letter and format the rest
            return checkName.charAt(0).toUpperCase() + checkName.slice(1).replace(/_/g, ' ') + ' Check';
        }
        // Fallback for existing or simple error types
        return type.charAt(0).toUpperCase() + type.slice(1).replace(/_/g, ' ');
    }
    
    /**
     * Dynamically adds new error type filters to the UI if they don't exist.
     */
    function updateErrorTypeFilters(newErrorTypes) {
        let filtersChanged = false;
        const container = document.getElementById('error-type-filter');

        newErrorTypes.forEach(type => {
            if (!knownErrorTypes.has(type)) {
                knownErrorTypes.add(type);
                const labelText = formatErrorType(type);
                errorTypeLabels[type] = labelText; // Store for later use

                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = type;
                checkbox.checked = true; // New filters are active by default
                checkbox.addEventListener('change', applyFilters);
                
                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(` ${labelText}`));
                container.appendChild(label);
                filtersChanged = true;
            }
        });
        return filtersChanged;
    }

    // --- Helper Functions ---

    /**
     * Formats a timestamp to "HH:MM:SS".
     * @param {string} isoTimestamp - Timestamp in ISO 8601 format.
     * @returns {string} Formatted time.
     */
    const formatTimestamp = (isoTimestamp) => {
        try {
            return new Date(isoTimestamp).toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (error) {
            return 'Invalid Time';
        }
    };

    /**
     * Updates the connection status display.
     * @param {string} status - The status (connected, disconnected, connecting, error).
     * @param {string} message - The text to display.
     */
    const updateConnectionStatus = (status, message) => {
        connectionStatusEl.className = 'connection-status'; // Reset classes
        connectionStatusEl.classList.add(status);
        statusTextEl.textContent = message;
    };

    /**
     * Updates the statistics counters in the UI.
     */
    const updateStats = () => {
        totalCountEl.textContent = stats.total;
        validatedCountEl.textContent = stats.validated;
        failedCountEl.textContent = stats.failed;
    };
    
    /**
     * Converts incoming JSON data to a user-friendly HTML format.
     * @param {object} data - The JSON data object.
     * @param {boolean} isError - Indicates if the message is an error message.
     * @returns {string} An HTML string.
     */
    const createPrettyView = (data, isError = false) => {
        let html = '<div class="pretty-view">';
        for (const [key, value] of Object.entries(data)) {
            // Display error details in a separate section
            if (key === 'errors' && Array.isArray(value)) continue;

            html += `<span class="field-name">${key}:</span>`;
            html += `<span class="field-value">${JSON.stringify(value, null, 2)}</span>`;
        }
        html += '</div>';

        // If it's an error, add a separate section for error details
        if (isError && data.errors && Array.isArray(data.errors)) {
            html += '<div class="error-details">';
            html += '<span class="field-name">Error Details:</span><div>';
             data.errors.forEach(err => {
                html += `<div class="field-value">- ${err.reason}</div>`;
            });
            html += '</div></div>';
        }
        return html;
    };

    // --- Core Functions ---

    /**
     * Creates an HTML card for a new message and appends it to the DOM.
     * @param {string} topic - The topic the message was received on.
     * @param {string} message - The message payload (JSON string).
     */
    const createMessageCard = (topic, message) => {
        const messageId = `msg-${Date.now()}-${Math.random()}`;
        // Determine status by checking if the topic is in our set of validated topics
        const status = validatedTopics.has(topic) ? 'validated' : 'failed';
        
        // --- NEW: Determine message type for styling ---
        let messageTypeClass = status; // Default to 'validated' or 'failed'
        if (status === 'validated') {
            if (commandValidatedTopics.has(topic)) {
                messageTypeClass = 'validated-command';
            } else if (statusValidatedTopics.has(topic)) {
                messageTypeClass = 'validated-status';
            }
        }
        // --- END NEW ---

        // This will be determined from the payload later
        let actuatorId = 'unknown'; // Fallback
        const sourceTopic = topicToSourceMap.get(topic) || 'unknown_source'; // sourceTopic is now actuator_id
        
        // Update stats
        stats.total++;
        if (status === 'validated') stats.validated++;
        else stats.failed++;
        updateStats();

        let data;
        try {
            data = JSON.parse(message);
            // Determine actuatorId from the payload for robustness
            actuatorId = data.actuator_id || 'unknown';
        } catch (e) {
            console.error('JSON parsing error:', e);
            data = { error: "The incoming message is not in JSON format.", content: message };
        }

        const card = {
            id: messageId,
            topic: topic,
            status: status,
            actuatorId: actuatorId, 
            sourceTopic: sourceTopic, // Represents actuatorId
            timestamp: data.timestamp || new Date().toISOString(),
            data: data,
            element: document.createElement('div')
        };
        
        card.element.className = `message-card ${messageTypeClass}`; // Use the new specific class
        card.element.id = messageId;
        card.element.dataset.actuatorId = actuatorId;
        card.element.dataset.status = status;
        card.element.dataset.sourceTopic = sourceTopic; // Still use this for filter matching
        
        // If the message failed, store the error types for filtering
        if (status === 'failed' && data.errors) {
            const errorTypes = new Set(data.errors.map(e => e.error_type));
            card.element.dataset.errorTypes = [...errorTypes].join(' ');

            // Dynamically update filters if a new error type is found
            updateErrorTypeFilters(errorTypes);
        }

        // --- NEW: Use different icons based on message type ---
        let cardIcon;
        if (status === 'failed') {
            cardIcon = '<i class="ph-fill ph-x-circle"></i>';
        } else { // It's validated
            if (commandValidatedTopics.has(topic)) {
                cardIcon = '<i class="ph-fill ph-lightning"></i>'; // Command icon
            } else if (statusValidatedTopics.has(topic)) {
                cardIcon = '<i class="ph-fill ph-gauge"></i>';       // Status icon
            } else {
                cardIcon = '<i class="ph-fill ph-check-circle"></i>'; // Fallback
            }
        }
        // --- END NEW ---

        card.element.innerHTML = `
            <div class="card-header">
                <span class="card-topic">${cardIcon} ${topic}</span>
                <span class="card-timestamp">${formatTimestamp(card.timestamp)}</span>
            </div>
            <div class="card-body">
                <!-- Views will be rendered here -->
            </div>
            <div class="card-actions">
                <button class="view-toggle-btn active" data-view="pretty">Pretty View</button>
                <button class="view-toggle-btn" data-view="json">JSON</button>
                <button class="copy-btn" title="Copy JSON to clipboard">
                    <i class="ph ph-copy"></i>
                </button>
            </div>
        `;
        
        // Add the card to the message array and the DOM
        allMessages.unshift(card); // Newest message at the top
        messageLogEl.prepend(card.element);

        // Hide the placeholder
        if (!logPlaceholderEl.classList.contains('hidden')) {
            logPlaceholderEl.classList.add('hidden');
        }

        // Add functionality to the view toggle buttons
        const body = card.element.querySelector('.card-body');
        const prettyBtn = card.element.querySelector('[data-view="pretty"]');
        const jsonBtn = card.element.querySelector('[data-view="json"]');
        const copyBtn = card.element.querySelector('.copy-btn');

        const prettyViewHTML = createPrettyView(data, status === 'failed');
        const jsonString = JSON.stringify(data, null, 2);
        const jsonViewHTML = `<pre>${jsonString}</pre>`;
        
        body.innerHTML = prettyViewHTML; // Default view

        prettyBtn.addEventListener('click', () => {
            body.innerHTML = prettyViewHTML;
            prettyBtn.classList.add('active');
            jsonBtn.classList.remove('active');
        });

        jsonBtn.addEventListener('click', () => {
            body.innerHTML = jsonViewHTML;
            jsonBtn.classList.add('active');
            prettyBtn.classList.remove('active');
        });

        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(jsonString).then(() => {
                const icon = copyBtn.querySelector('i');
                icon.classList.remove('ph-copy');
                icon.classList.add('ph-check-fat');
                copyBtn.title = "Copied!";
                setTimeout(() => {
                    icon.classList.remove('ph-check-fat');
                    icon.classList.add('ph-copy');
                    copyBtn.title = "Copy JSON to clipboard";
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                copyBtn.title = "Copy failed!";
            });
        });

        return card;
    };
    
    /**
     * Applies the current filter settings and shows/hides messages accordingly.
     */
    const applyFilters = () => {
        const selectedSourceTopics = [...document.querySelectorAll('#source-topic-filter input:checked')].map(cb => cb.value);
        const selectedStatuses = [...document.querySelectorAll('#status-filter input:checked')].map(cb => cb.value);
        const selectedErrorTypes = [...document.querySelectorAll('#error-type-filter input:checked')].map(cb => cb.value);
        const isFailedFilterActive = selectedStatuses.includes('failed');

        // Toggle error type filter visibility
        errorTypeFilterGroup.classList.toggle('disabled', !isFailedFilterActive);

        allMessages.forEach(card => {
            const isSourceTopicMatch = selectedSourceTopics.includes(card.sourceTopic);
            const isStatusMatch = selectedStatuses.includes(card.status);

            let isErrorTypeMatch = true;
            if (isFailedFilterActive && card.status === 'failed') {
                // If no error types are selected, we match none.
                if (selectedErrorTypes.length === 0) {
                    isErrorTypeMatch = false;
                } else {
                    const cardErrorTypes = card.element.dataset.errorTypes?.split(' ') || [];
                    // The card must have at least one of the selected error types
                    isErrorTypeMatch = selectedErrorTypes.some(type => cardErrorTypes.includes(type));
                }
            }
            
            if (isSourceTopicMatch && isStatusMatch && isErrorTypeMatch) {
                card.element.classList.remove('hidden');
            } else {
                card.element.classList.add('hidden');
            }
        });
    };


    // --- MQTT Client ---

    const connectToBroker = (topicsToSubscribe) => {
        updateConnectionStatus('connecting', 'Connecting...');
        client = mqtt.connect(brokerUrl);

        client.on('connect', () => {
            updateConnectionStatus('connected', 'Connection Successful');
            console.log('Successfully connected to MQTT broker.');
            topicsToSubscribe.forEach(topic => {
                client.subscribe(topic, (err) => {
                    if (err) {
                        console.error(`Error subscribing to topic '${topic}':`, err);
                    } else {
                        console.log(`Subscribed to topic '${topic}'.`);
                    }
                });
            });
        });

        client.on('message', (topic, message) => {
            console.log(`Message received [${topic}]: ${message.toString()}`);
            createMessageCard(topic, message.toString());
            // Check if the new card matches the current filters
            applyFilters(); 
        });

        client.on('error', (err) => {
            updateConnectionStatus('error', 'Connection Error');
            console.error('MQTT Connection Error:', err);
            // client.end() öğesini kaldırdık. Bu, kütüphanenin otomatik yeniden bağlanma
            // özelliğinin devreye girmesine izin verir. "Yetki yok" hatası gibi
            // kalıcı hatalar zaten zaman aşımına uğrayacak ve döngüye girmeyecektir.
            // client.end(); // Close connection on error
        });

        client.on('close', () => {
            if (connectionStatusEl.classList.contains('connected')) {
                updateConnectionStatus('disconnected', 'Disconnected');
            }
            console.log('MQTT connection closed.');
        });

        client.on('reconnect', () => {
             updateConnectionStatus('connecting', 'Reconnecting...');
        });
    };
    
    /**
     * Renders the source topic filters based on the current mappings.
     */
    function renderActuatorIdFilters(mappings) {
        sourceTopicFilterContainer.innerHTML = '';
        const actuatorIds = [...new Set(mappings.map(m => m.actuator_id))];
        
        actuatorIds.forEach(actuatorId => {
            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = actuatorId;
            checkbox.checked = true;
            checkbox.addEventListener('change', applyFilters);
            
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` ${actuatorId}`));
            sourceTopicFilterContainer.appendChild(label);
        });
    }

    /**
     * Fetches topics from the backend and initializes the MQTT client.
     */
    async function initializeApp() {
        try {
            const response = await fetch('/api/actuator-mappings'); // <-- CORRECT
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const mappings = await response.json();
            
            // Rebuild validatedTopics and topicToSourceMap for the new structure
            validatedTopics.clear();
            topicToSourceMap.clear();
            commandValidatedTopics.clear(); // <-- NEW
            statusValidatedTopics.clear();  // <-- NEW
            const topicsToSubscribe = [];

            mappings.forEach(m => {
                // Add all 'validated' topics to the set for quick status checks
                if (m.command_validated_topic) {
                    validatedTopics.add(m.command_validated_topic);
                    commandValidatedTopics.add(m.command_validated_topic); // <-- NEW
                }
                if (m.status_validated_topic) {
                    validatedTopics.add(m.status_validated_topic);
                    statusValidatedTopics.add(m.status_validated_topic); // <-- NEW
                }

                // Map all topics back to the actuator_id for filtering
                const allTopics = [
                    m.command_validated_topic, m.command_failed_topic,
                    m.status_validated_topic, m.status_failed_topic
                ];
                allTopics.forEach(topic => {
                    if (topic) {
                        topicToSourceMap.set(topic, m.actuator_id);
                        topicsToSubscribe.push(topic);
                    }
                });
            });
            
            // Dynamically create the filters in the sidebar based on actuator_id
            renderActuatorIdFilters(mappings);
            
            // Disconnect old client if it exists before creating a new one
            if (client && client.connected) {
                client.end(true, () => {
                    console.log('Old MQTT client disconnected. Re-initializing in 1 second...');
                    setTimeout(() => {
                        if (topicsToSubscribe.length > 0) {
                            connectToBroker(topicsToSubscribe);
                        } else {
                            updateConnectionStatus('disconnected', 'No topics configured.');
                        }
                    }, 1000); 
                });
            } else {
                if (topicsToSubscribe.length > 0) {
                    connectToBroker(topicsToSubscribe);
                } else {
                    updateConnectionStatus('disconnected', 'No topics configured.');
                    console.log('No topics to subscribe to from server config.');
                }
            }
        } catch (error) {
            updateConnectionStatus('error', 'Failed to fetch config.');
            console.error('Could not fetch topic mappings from server:', error);
        }
    }

    /**
     * Sets up a WebSocket connection to listen for configuration changes.
     */
    function setupWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/config-updates`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connection established for config updates.');
        };

        ws.onmessage = (event) => {
            if (event.data === 'config_updated') {
                console.log('Configuration has changed on the server. Re-initializing...');
                // initializeApp zaten bağlantıyı güvenli bir şekilde yönetiyor.
                initializeApp();
            }
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed. Attempting to reconnect in 5 seconds...');
            setTimeout(setupWebSocket, 5000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    // --- Event Listeners ---

    // Note: Source topic filter listeners are added dynamically in renderSourceTopicFilters
    document.querySelectorAll('#status-filter input').forEach(cb => cb.addEventListener('change', applyFilters));
    // Error type filters are now fully dynamic, so we delegate the event listener to the parent
    document.getElementById('error-type-filter').addEventListener('change', (event) => {
        if (event.target.type === 'checkbox') {
            applyFilters();
        }
    });
    
    clearLogBtn.addEventListener('click', () => {
        allMessages = [];
        messageLogEl.innerHTML = '';
        logPlaceholderEl.classList.remove('hidden');
        // Reset stats
        stats = { total: 0, validated: 0, failed: 0 };
        updateStats();
    });

    // --- Initialization ---
    initializeApp();
    setupWebSocket(); // Also set up the WebSocket listener
});
