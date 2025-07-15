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
    const sensorFilterCheckboxes = document.querySelectorAll('#sensor-filter input[type="checkbox"]');
    const statusFilterCheckboxes = document.querySelectorAll('#status-filter input[type="checkbox"]');
    const failedStatusCheckbox = document.querySelector('#status-filter input[value="failed"]');
    const errorTypeFilterGroup = document.getElementById('error-type-filter-group');
    const errorTypeFilterCheckboxes = document.querySelectorAll('#error-type-filter input[type="checkbox"]');
    const clearLogBtn = document.getElementById('clear-log-btn');

    // --- MQTT Settings ---
    const brokerUrl = 'wss://broker.hivemq.com:8884/mqtt';
    const topics = ['/sensor1/validated', '/sensor1/failed', '/sensor2/validated', '/sensor2/failed', '/sensor3/validated', '/sensor3/failed'];
    
    let client;
    let allMessages = []; // Array to store all messages for filtering
    let stats = { total: 0, validated: 0, failed: 0 };

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
        const status = topic.includes('validated') ? 'validated' : 'failed';
        const sensorId = topic.split('/')[1] || 'unknown';
        
        // Update stats
        stats.total++;
        if (status === 'validated') stats.validated++;
        else stats.failed++;
        updateStats();

        let data;
        try {
            data = JSON.parse(message);
        } catch (e) {
            console.error('JSON parsing error:', e);
            data = { error: "The incoming message is not in JSON format.", content: message };
        }

        const card = {
            id: messageId,
            topic: topic,
            status: status,
            sensorId: sensorId,
            timestamp: data.timestamp || new Date().toISOString(),
            data: data,
            element: document.createElement('div')
        };
        
        card.element.className = `message-card ${status}`;
        card.element.id = messageId;
        card.element.dataset.sensorId = sensorId;
        card.element.dataset.status = status;
        
        // If the message failed, store the error types for filtering
        if (status === 'failed' && data.errors) {
            const errorTypes = new Set(data.errors.map(e => e.error_type));
            card.element.dataset.errorTypes = [...errorTypes].join(' ');
        }

        const cardIcon = status === 'validated' 
            ? '<i class="ph-fill ph-check-circle"></i>' 
            : '<i class="ph-fill ph-x-circle"></i>';

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
        const selectedSensors = [...sensorFilterCheckboxes].filter(cb => cb.checked).map(cb => cb.value);
        const selectedStatuses = [...statusFilterCheckboxes].filter(cb => cb.checked).map(cb => cb.value);
        const selectedErrorTypes = [...errorTypeFilterCheckboxes].filter(cb => cb.checked).map(cb => cb.value);
        const isFailedFilterActive = failedStatusCheckbox.checked;

        // Toggle error type filter visibility
        errorTypeFilterGroup.classList.toggle('disabled', !isFailedFilterActive);

        allMessages.forEach(card => {
            const isSensorMatch = selectedSensors.includes(card.sensorId);
            const isStatusMatch = selectedStatuses.includes(card.status);

            let isErrorTypeMatch = true;
            if (isFailedFilterActive && card.status === 'failed') {
                const cardErrorTypes = card.element.dataset.errorTypes?.split(' ') || [];
                // The card must have at least one of the selected error types
                isErrorTypeMatch = selectedErrorTypes.some(type => cardErrorTypes.includes(type));
            }
            
            if (isSensorMatch && isStatusMatch && isErrorTypeMatch) {
                card.element.classList.remove('hidden');
            } else {
                card.element.classList.add('hidden');
            }
        });
    };


    // --- MQTT Client ---

    const connectToBroker = () => {
        updateConnectionStatus('connecting', 'Connecting...');
        client = mqtt.connect(brokerUrl);

        client.on('connect', () => {
            updateConnectionStatus('connected', 'Connection Successful');
            console.log('Successfully connected to MQTT broker.');
            topics.forEach(topic => {
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
            client.end(); // Close connection on error
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

    // --- Event Listeners ---

    sensorFilterCheckboxes.forEach(cb => cb.addEventListener('change', applyFilters));
    statusFilterCheckboxes.forEach(cb => cb.addEventListener('change', applyFilters));
    errorTypeFilterCheckboxes.forEach(cb => cb.addEventListener('change', applyFilters));
    
    clearLogBtn.addEventListener('click', () => {
        allMessages = [];
        messageLogEl.innerHTML = '';
        logPlaceholderEl.classList.remove('hidden');
        // Reset stats
        stats = { total: 0, validated: 0, failed: 0 };
        updateStats();
    });

    // --- Initialization ---
    connectToBroker();
    applyFilters(); // Apply initial filter state on load

});