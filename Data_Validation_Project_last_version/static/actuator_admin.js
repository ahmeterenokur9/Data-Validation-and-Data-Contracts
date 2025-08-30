document.addEventListener('DOMContentLoaded', () => {
    let availableSchemas = [];
    let isEditMode = false;
    let currentEditingFilename = null;

    const configStatus = document.getElementById('config-status');
    const mappingsList = document.getElementById('mappings-list');
    const schemasTableBody = document.querySelector('#schemas-table tbody');
    const schemaEditorContainer = document.getElementById('schema-editor-container');
    const schemaEditorForm = document.getElementById('schema-editor-form');
    const editorTitle = document.getElementById('editor-title');
    const schemaFilenameInput = document.getElementById('schema-filename');
    const schemaStatus = document.getElementById('schema-status');

    // Editor Mode Elements
    let currentEditorMode = 'visual'; // 'visual' or 'raw'
    const visualEditorBtn = document.getElementById('visual-editor-btn');
    const rawEditorBtn = document.getElementById('raw-editor-btn');
    const visualEditor = document.getElementById('visual-editor');
    const rawEditor = document.getElementById('raw-editor');
    const schemaContentRaw = document.getElementById('schema-content-raw');

    // New Schema Builder Elements
    const columnsContainer = document.getElementById('columns-container');
    const addColumnBtn = document.getElementById('add-column-btn');
    const columnTemplate = document.getElementById('column-template');
    const checkTemplate = document.getElementById('check-template');

    // --- UI LOGIC ---

    function addColumn(columnData = {}) {
        const columnCard = columnTemplate.content.cloneNode(true).firstElementChild;
        
        // Populate fields if data is provided (for editing)
        columnCard.querySelector('.column-name').value = columnData.name || '';
        if (columnData.dtype) columnCard.querySelector('.column-dtype').value = columnData.dtype;
        columnCard.querySelector('.column-nullable').checked = columnData.nullable || false;
        columnCard.querySelector('.column-unique').checked = columnData.unique || false;
        
        const checksContainer = columnCard.querySelector('.checks-container');
        if (columnData.checks) {
            for (const [type, value] of Object.entries(columnData.checks)) {
                addCheck(checksContainer, { type, value });
            }
        }

        columnsContainer.appendChild(columnCard);
    }

    function addCheck(container, checkData = {}) {
        const checkItem = checkTemplate.content.cloneNode(true).firstElementChild;
        if (checkData.type) checkItem.querySelector('.check-type').value = checkData.type;
        
        // Handle array values for 'in_range'
        if (checkData.type === 'in_range' && Array.isArray(checkData.value)) {
             checkItem.querySelector('.check-value').value = JSON.stringify(checkData.value);
        } else {
            checkItem.querySelector('.check-value').value = checkData.value || '';
        }

        container.appendChild(checkItem);
    }

    function buildSchemaJsonFromForm() {
        const schema = { columns: {} };
        
        // General settings
        schema.strict = document.getElementById('schema-strict').checked;
        schema.ordered = document.getElementById('schema-ordered').checked;
        schema.coerce = document.getElementById('schema-coerce').checked;

        columnsContainer.querySelectorAll('.column-card').forEach(card => {
            const name = card.querySelector('.column-name').value.trim();
            if (!name) return; // Skip empty columns

            const column = {
                dtype: card.querySelector('.column-dtype').value,
                nullable: card.querySelector('.column-nullable').checked,
                unique: card.querySelector('.column-unique').checked,
                checks: {}
            };

            card.querySelectorAll('.check-item').forEach(item => {
                const type = item.querySelector('.check-type').value;
                let value = item.querySelector('.check-value').value;
                
                // --- NEW: Smartly parse values for list-based checks ---
                if (type === 'isin' || type === 'notin') {
                    // Try to parse as JSON array first. If it fails, assume comma-separated.
                    try {
                        const parsed = JSON.parse(value);
                        if (Array.isArray(parsed)) {
                            value = parsed; // It's already a valid array
                        } else {
                           // It was valid JSON but not an array, treat as a single-element list
                           value = [parsed];
                        }
                    } catch (e) {
                        // Not a valid JSON array, treat as comma-separated string
                        value = value.split(',').map(s => {
                            const trimmed = s.trim();
                            // Attempt to convert to number if it looks like one
                            if (!isNaN(trimmed) && trimmed !== '') {
                                return Number(trimmed);
                            }
                            // Otherwise, remove quotes if user added them
                            return trimmed.replace(/^["']|["']$/g, '');
                        });
                    }
                } else if (!type.startsWith('str_')) {
                    // Original logic for other non-string types
                    try { value = JSON.parse(value); } catch (e) { /* keep as string */ }
                }
                // --- END NEW ---
                
                column.checks[type] = value;
            });
            
            if (Object.keys(column.checks).length === 0) {
                delete column.checks;
            }

            schema.columns[name] = column;
        });

        return schema;
    }

    function populateFormFromJson(schema) {
        // Clear existing form
        columnsContainer.innerHTML = '';

        if (!schema) return;

        // Populate general settings
        document.getElementById('schema-strict').checked = schema.strict || false;
        document.getElementById('schema-ordered').checked = schema.ordered || false;
        document.getElementById('schema-coerce').checked = schema.coerce || false;

        // Populate columns
        if (schema.columns) {
            for (const [name, data] of Object.entries(schema.columns)) {
                addColumn({ name, ...data });
            }
        }
    }
    
    function switchToVisual() {
        try {
            const content = schemaContentRaw.value.trim();
            if (!content) {
                // If the raw editor is empty, just switch without error, maybe populate with a default.
                populateFormFromJson({ strict: true, columns: {} });
            } else {
                const schemaJson = JSON.parse(content);
                populateFormFromJson(schemaJson);
            }
            
            visualEditor.style.display = 'block';
            rawEditor.style.display = 'none';
            visualEditorBtn.classList.add('active');
            rawEditorBtn.classList.remove('active');
            currentEditorMode = 'visual';
        } catch (e) {
            showStatus(schemaStatus, `Invalid JSON in raw editor. Please fix before switching. Error: ${e.message}`, false);
        }
    }

    function switchToRaw() {
        const schemaJson = buildSchemaJsonFromForm();
        schemaContentRaw.value = JSON.stringify(schemaJson, null, 4);

        rawEditor.style.display = 'block';
        visualEditor.style.display = 'none';
        rawEditorBtn.classList.add('active');
        visualEditorBtn.classList.remove('active');
        currentEditorMode = 'raw';
    }


    // --- API & DATA LOGIC ---

    async function apiCall(url, options = {}) {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    function showStatus(element, message, isSuccess) {
        element.textContent = message;
        element.className = `status-message ${isSuccess ? 'success' : 'error'}`;
        element.classList.remove('hidden');
        setTimeout(() => element.classList.add('hidden'), 5000);
    }

    async function loadInitialConfig() {
        try {
            // UPDATED: Fetch from actuator-specific endpoints
            const [settings, mappings, schemas] = await Promise.all([
                apiCall('/api/mqtt-settings'), // This can remain common for now
                apiCall('/api/actuator-mappings'),
                apiCall('/api/actuator-schemas') // We will create this backend endpoint next
            ]);
            availableSchemas = schemas;
            document.getElementById('broker').value = settings.broker || '';
            document.getElementById('port').value = settings.port || '';
            renderMappings(mappings);
            renderSchemaFileList(schemas);
        } catch (error) {
            showStatus(configStatus, `Error loading config: ${error.message}`, false);
        }
    }

    function renderMappings(mappings = []) {
        mappingsList.innerHTML = '';
        mappings.forEach((mapping, index) => {
            mappingsList.appendChild(createMappingItem(mapping, index));
        });
    }

    function createMappingItem(mapping, index) {
        const div = document.createElement('div');
        div.className = 'mapping-item';
        
        const commandSchemaOptions = availableSchemas.map(s => `<option value="${s}" ${s === mapping.command_schema ? 'selected' : ''}>${s.split('/').pop()}</option>`).join('');
        const statusSchemaOptions = availableSchemas.map(s => `<option value="${s}" ${s === mapping.status_schema ? 'selected' : ''}>${s.split('/').pop()}</option>`).join('');

        div.innerHTML = `
            <div class="mapping-header">
                <h4>Actuator #${index + 1}</h4>
                <button type="button" class="delete-btn delete-mapping-btn"><i class="ph ph-trash"></i></button>
            </div>
            <div class="form-group">
                <label>Actuator ID</label>
                <input type="text" class="mapping-actuator-id" value="${mapping.actuator_id || ''}" placeholder="e.g., smart_lamp_1">
            </div>

            <h5 style="margin-top: 1rem;">Command Topics</h5>
            <div class="mapping-fields" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                <div class="form-group">
                    <label>Command Topic (Raw)</label>
                    <input type="text" class="mapping-command-topic" value="${mapping.command_topic || ''}">
                </div>
                <div class="form-group">
                    <label>Validated Command Topic</label>
                    <input type="text" class="mapping-command-validated-topic" value="${mapping.command_validated_topic || ''}">
                </div>
                <div class="form-group">
                    <label>Failed Command Topic</label>
                    <input type="text" class="mapping-command-failed-topic" value="${mapping.command_failed_topic || ''}">
                </div>
            </div>
             <div class="form-group">
                <label>Command Schema</label>
                <select class="mapping-command-schema"><option value="">- None -</option>${commandSchemaOptions}</select>
            </div>

            <hr style="margin: 1rem 0;">

            <h5>Status Topics</h5>
            <div class="mapping-fields" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                <div class="form-group">
                    <label>Status Topic (Raw)</label>
                    <input type="text" class="mapping-status-topic" value="${mapping.status_topic || ''}">
                </div>
                <div class="form-group">
                    <label>Validated Status Topic</label>
                    <input type="text" class="mapping-status-validated-topic" value="${mapping.status_validated_topic || ''}">
                </div>
                 <div class="form-group">
                    <label>Failed Status Topic</label>
                    <input type="text" class="mapping-status-failed-topic" value="${mapping.status_failed_topic || ''}">
                </div>
            </div>
            <div class="form-group">
                <label>Status Schema</label>
                <select class="mapping-status-schema"><option value="">- None -</option>${statusSchemaOptions}</select>
            </div>
            `;

        return div;
    }

    function renderSchemaFileList(schemas = []) {
        schemasTableBody.innerHTML = '';
        schemas.forEach(schemaPath => {
            const filename = schemaPath.split('/').pop();
            const row = document.createElement('tr');
            row.innerHTML = `<td>${filename}</td><td><button class="edit-btn" data-filename="${filename}">Edit</button><button class="delete-btn" data-filename="${filename}">Delete</button></td>`;
            schemasTableBody.appendChild(row);
        });
    }

    function showSchemaEditor(isNew, filename = '') {
        isEditMode = !isNew;
        currentEditingFilename = isNew ? null : filename;
        editorTitle.textContent = isNew ? 'Create New Schema' : `Editing: ${filename}`;
        schemaFilenameInput.value = isNew ? '' : filename;
        schemaFilenameInput.readOnly = !isNew;
        
        if (isNew) {
            // Start with a clean slate for the form
            populateFormFromJson({
                strict: true,
                coerce: false,
                ordered: false,
                columns: {
                    "sensor_id": { "dtype": "str", "nullable": false },
                    "timestamp": { "dtype": "str", "nullable": false }
                }
            });
        }
        schemaEditorContainer.style.display = 'block';
    }

    function hideSchemaEditor() {
        schemaEditorContainer.style.display = 'none';
        schemaEditorForm.reset();
        columnsContainer.innerHTML = ''; // Clear dynamic columns
    }

    document.getElementById('mqtt-config-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // --- UPDATED FOR ACTUATORS ---

        // 1. Save MQTT Settings (can be a separate call)
        const settings = {
            broker: document.getElementById('broker').value,
            port: parseInt(document.getElementById('port').value, 10)
        };
        
        // 2. Build and save actuator mappings
        const mappingElements = mappingsList.querySelectorAll('.mapping-item');
        const mappings = Array.from(mappingElements).map(item => {
            const actuatorId = item.querySelector('.mapping-actuator-id').value.trim();
            if (!actuatorId) return null;

            return {
                actuator_id: actuatorId,
                command_topic: item.querySelector('.mapping-command-topic').value.trim(),
                command_validated_topic: item.querySelector('.mapping-command-validated-topic').value.trim(),
                command_failed_topic: item.querySelector('.mapping-command-failed-topic').value.trim(),
                status_topic: item.querySelector('.mapping-status-topic').value.trim(),
                status_validated_topic: item.querySelector('.mapping-status-validated-topic').value.trim(),
                status_failed_topic: item.querySelector('.mapping-status-failed-topic').value.trim(),
                command_schema: item.querySelector('.mapping-command-schema').value,
                status_schema: item.querySelector('.mapping-status-schema').value
            };
        }).filter(m => m && m.actuator_id);

        try {
            // Make separate API calls for each config file
            await apiCall('/api/mqtt-settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(settings) });
            await apiCall('/api/actuator-mappings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(mappings) });
            showStatus(configStatus, 'Configuration saved successfully!', true);
        } catch (error) {
            showStatus(configStatus, `Failed to save configuration: ${error.message}`, false);
        }
        // --- END UPDATE ---
    });

    document.getElementById('add-mapping-btn').addEventListener('click', () => {
        mappingsList.appendChild(createMappingItem({}, mappingsList.children.length));
    });

    mappingsList.addEventListener('click', (e) => {
        if (e.target.closest('.delete-mapping-btn')) {
            e.target.closest('.mapping-item').remove();
        }
    });

    document.getElementById('new-schema-btn').addEventListener('click', () => showSchemaEditor(true));
    document.getElementById('cancel-edit-btn').addEventListener('click', hideSchemaEditor);
    
    schemasTableBody.addEventListener('click', (e) => {
        const button = e.target.closest('button');
        if (!button) return;
        const filename = button.dataset.filename;
        
        if (button.classList.contains('edit-btn')) {
            // UPDATED: Use the new actuator-specific endpoint
            apiCall(`/api/actuator-schemas/${filename}`).then(content => {
                showSchemaEditor(false, filename);
                // Populate both editors initially
                populateFormFromJson(content);
                schemaContentRaw.value = JSON.stringify(content, null, 4);
                // Default to visual editor
                switchToVisual();
            }).catch(err => showStatus(schemaStatus, err.message, false));
        } else if (button.classList.contains('delete-btn')) {
            if (confirm(`Are you sure you want to delete "${filename}"?`)) {
                // UPDATED: Use the new actuator-specific endpoint
                apiCall(`/api/actuator-schemas/${filename}`, { method: 'DELETE' }).then(() => {
                    showStatus(schemaStatus, `"${filename}" deleted.`, true);
                    loadInitialConfig();
                }).catch(err => showStatus(schemaStatus, err.message, false));
            }
        }
    });

    schemaEditorForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const filename = schemaFilenameInput.value.trim();
        if (!filename) {
            showStatus(schemaStatus, 'Filename is required.', false);
            return;
        }
        
        let schemaContentStr;

        if (currentEditorMode === 'visual') {
            const schemaJson = buildSchemaJsonFromForm();
            schemaContentStr = JSON.stringify(schemaJson);
        } else { // raw mode
            schemaContentStr = schemaContentRaw.value;
            // Now, we do a client-side check for valid JSON before sending
            try {
                JSON.parse(schemaContentStr);
            } catch (e) {
                showStatus(schemaStatus, `Save failed: Content is not valid JSON. Error: ${e.message}`, false);
                return; // Stop the submission
            }
        }

        // UPDATED: Use the new actuator-specific endpoints
        const url = isEditMode ? `/api/actuator-schemas/${filename}` : '/api/actuator-schemas';
        const method = isEditMode ? 'PUT' : 'POST';
        
        let finalBody = schemaContentStr;
        // For POST, the backend expects a different structure {filename, content}
        // The content here is now a string that the backend will parse
        if (!isEditMode) {
            finalBody = JSON.stringify({ filename, content: schemaContentStr });
        }

        fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: finalBody })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'An unknown error occurred'); });
                }
                return response.json();
            })
            .then(result => {
                showStatus(schemaStatus, result.message, true);
                loadInitialConfig();
                hideSchemaEditor();
            })
            .catch(err => {
                showStatus(schemaStatus, `Save failed: ${err.message}`, false);
            });
    });
    
    // --- DYNAMIC FORM EVENT LISTENERS ---
    
    visualEditorBtn.addEventListener('click', switchToVisual);
    rawEditorBtn.addEventListener('click', switchToRaw);
    
    addColumnBtn.addEventListener('click', () => addColumn());

    columnsContainer.addEventListener('click', e => {
        if (e.target.closest('.delete-column-btn')) {
            e.target.closest('.column-card').remove();
        } else if (e.target.closest('.add-check-btn')) {
            const checksContainer = e.target.closest('.column-card').querySelector('.checks-container');
            addCheck(checksContainer);
        } else if (e.target.closest('.delete-check-btn')) {
            e.target.closest('.check-item').remove();
        }
    });
    
    // Show/hide checks based on dtype
    columnsContainer.addEventListener('change', e => {
        if (e.target.classList.contains('column-dtype')) {
            const columnCard = e.target.closest('.column-card');
            const checksWrapper = columnCard.querySelector('.column-checks-wrapper');
            if (e.target.value === 'datetime') {
                checksWrapper.style.display = 'none';
            } else {
                checksWrapper.style.display = 'block';
            }
        }
    });

    loadInitialConfig();
});
