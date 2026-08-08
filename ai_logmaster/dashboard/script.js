// ─── DOM References ───
const DOM = {
    // AI Provider
    provider: document.getElementById('ai-provider'),
    model: document.getElementById('ai-model'),
    modelSuggestions: document.getElementById('model-suggestions'),
    apiKey: document.getElementById('ai-api-key'),
    toggleKeyVisibility: document.getElementById('toggle-key-visibility'),
    envHint: document.getElementById('env-hint'),
    baseUrl: document.getElementById('ai-base-url'),
    baseUrlGroup: document.getElementById('base-url-group'),

    // Tuning
    temperature: document.getElementById('ai-temperature'),
    temperatureValue: document.getElementById('temperature-value'),
    maxTokens: document.getElementById('ai-max-tokens'),

    // Agent
    agentUseAI: document.getElementById('agent-use-ai'),
    agentCached: document.getElementById('agent-cached'),
    agentFetchDocs: document.getElementById('agent-fetch-docs'),
    agentAutoFix: document.getElementById('agent-auto-fix'),
    agentIndependentAutoFix: document.getElementById('agent-independent-auto-fix'),
    agentAutoRecover: document.getElementById('agent-auto-recover'),
    agentMaxRetries: document.getElementById('agent-max-retries'),

    // Documentation
    docEnableSearch: document.getElementById('doc-enable-search'),
    docSearchEngine: document.getElementById('doc-search-engine'),

    // Output
    outputVerbose: document.getElementById('output-verbose'),
    outputShowAPI: document.getElementById('output-show-api'),

    // Cache
    cacheTotalEntries: document.getElementById('cache-total-entries'),
    cacheTotalHits: document.getElementById('cache-total-hits'),
    cacheSize: document.getElementById('cache-size'),
    cachePath: document.getElementById('cache-path'),
    cacheTableBody: document.getElementById('cache-table-body'),
    btnRefreshCache: document.getElementById('btn-refresh-cache'),
    btnClearCache: document.getElementById('btn-clear-cache'),
    cacheActionResult: document.getElementById('cache-action-result'),

    // Actions
    btnTestConnection: document.getElementById('btn-test-connection'),
    testResult: document.getElementById('test-result'),
    btnSave: document.getElementById('btn-save'),
    btnReset: document.getElementById('btn-reset'),
    saveStatus: document.getElementById('save-status'),
    configPathBadge: document.getElementById('config-path-badge'),
};

// ─── State ───
let meta = {};  // provider_models, provider_env_vars, config_path

// ─── Initialize ───
document.addEventListener('DOMContentLoaded', init);

async function init() {
    try {
        const res = await fetch('/api/config');
        const config = await res.json();

        meta = config._meta || {};
        delete config._meta;

        populateForm(config);
        setupEventListeners();

        if (meta.config_path) {
            DOM.configPathBadge.textContent = meta.config_path;
        }
    } catch (err) {
        console.error('Failed to load config:', err);
        DOM.saveStatus.textContent = '⚠ Failed to load configuration';
        DOM.saveStatus.className = 'save-status error';
    }

    // Load cache stats on startup
    loadCacheStats();
}

// ─── Populate Form ───
function populateForm(config) {
    const ai = config.ai || {};
    const agent = config.agent || {};
    const doc = config.documentation || {};
    const output = config.output || {};

    // AI Provider
    DOM.provider.value = ai.provider || 'groq';
    DOM.model.value = ai.model || '';
    
    // Resolve API key — if it's an env var reference like ${GROQ_API_KEY}, show empty
    const rawKey = ai.api_key || '';
    DOM.apiKey.value = rawKey.startsWith('${') ? '' : rawKey;
    
    DOM.baseUrl.value = ai.base_url || '';
    updateProviderUI();

    // Tuning
    DOM.temperature.value = ai.temperature ?? 0.2;
    DOM.temperatureValue.textContent = ai.temperature ?? 0.2;
    DOM.maxTokens.value = ai.max_tokens ?? 1000;

    // Agent
    DOM.agentUseAI.checked = agent.use_ai_analysis !== false;
    DOM.agentCached.checked = agent.use_cached_solutions !== false;
    DOM.agentFetchDocs.checked = agent.fetch_documentation !== false;
    DOM.agentAutoFix.checked = agent.auto_fix !== false;
    DOM.agentIndependentAutoFix.checked = agent.independent_auto_fix === true;
    DOM.agentAutoRecover.checked = agent.auto_recover === true;
    DOM.agentMaxRetries.value = agent.max_retries ?? 3;

    // Documentation
    DOM.docEnableSearch.checked = doc.enable_search !== false;
    DOM.docSearchEngine.value = doc.search_engine || 'duckduckgo';

    // Output
    DOM.outputVerbose.checked = output.verbose !== false;
    DOM.outputShowAPI.checked = output.show_api_calls !== false;
}

// ─── Build Config Object from Form ───
function buildConfig() {
    return {
        ai: {
            provider: DOM.provider.value,
            model: DOM.model.value,
            api_key: DOM.apiKey.value,
            temperature: parseFloat(DOM.temperature.value),
            max_tokens: parseInt(DOM.maxTokens.value, 10),
            ...(DOM.baseUrl.value ? { base_url: DOM.baseUrl.value } : {}),
        },
        agent: {
            use_cached_solutions: DOM.agentCached.checked,
            fetch_documentation: DOM.agentFetchDocs.checked,
            use_ai_analysis: DOM.agentUseAI.checked,
            auto_fix: DOM.agentAutoFix.checked,
            independent_auto_fix: DOM.agentIndependentAutoFix.checked,
            auto_recover: DOM.agentAutoRecover.checked,
            max_retries: parseInt(DOM.agentMaxRetries.value, 10),
            cached_error_types: ["connection", "import", "memory", "timeout", "permission"],
            complex_error_types: ["syntax", "type", "value", "unknown"],
        },
        documentation: {
            enable_search: DOM.docEnableSearch.checked,
            search_engine: DOM.docSearchEngine.value,
        },
        output: {
            verbose: DOM.outputVerbose.checked,
            show_api_calls: DOM.outputShowAPI.checked,
        },
    };
}

// ─── Event Listeners ───
function setupEventListeners() {
    // Provider change → update model suggestions + env hint + base url visibility
    DOM.provider.addEventListener('change', () => {
        updateProviderUI();
        // Clear model and let them pick from suggestions
        DOM.model.value = '';
        showSuggestions();
    });

    // Temperature slider
    DOM.temperature.addEventListener('input', () => {
        DOM.temperatureValue.textContent = DOM.temperature.value;
    });

    // API key visibility toggle
    DOM.toggleKeyVisibility.addEventListener('click', () => {
        const isPassword = DOM.apiKey.type === 'password';
        DOM.apiKey.type = isPassword ? 'text' : 'password';
        DOM.toggleKeyVisibility.querySelector('.eye-icon').textContent = isPassword ? '🙈' : '👁';
    });

    // Model input → show/filter suggestions
    DOM.model.addEventListener('focus', showSuggestions);
    DOM.model.addEventListener('input', showSuggestions);
    document.addEventListener('click', (e) => {
        if (!DOM.model.contains(e.target) && !DOM.modelSuggestions.contains(e.target)) {
            DOM.modelSuggestions.classList.remove('visible');
        }
    });

    // Test connection
    DOM.btnTestConnection.addEventListener('click', testConnection);

    // Save
    DOM.btnSave.addEventListener('click', saveConfig);

    // Reset
    DOM.btnReset.addEventListener('click', resetConfig);

    // Cache
    DOM.btnRefreshCache.addEventListener('click', loadCacheStats);
    DOM.btnClearCache.addEventListener('click', clearCache);
}

// ─── Provider UI Updates ───
function updateProviderUI() {
    const provider = DOM.provider.value;

    // Update env hint
    const envVars = meta.provider_env_vars || {};
    const envVar = envVars[provider] || `${provider.toUpperCase()}_API_KEY`;
    DOM.envHint.textContent = `env: ${envVar}`;

    // Show base URL field for providers that need it
    const needsBaseUrl = ['nvidia', 'lm_studio', 'ollama'].includes(provider);
    DOM.baseUrlGroup.style.display = needsBaseUrl ? 'block' : 'none';

    // Auto-fill default base URLs for local providers
    const defaultUrls = {
        lm_studio: 'http://localhost:1234/v1',
        ollama: 'http://localhost:11434/v1',
        nvidia: 'https://integrate.api.nvidia.com/v1',
    };
    if (needsBaseUrl && !DOM.baseUrl.value && defaultUrls[provider]) {
        DOM.baseUrl.value = defaultUrls[provider];
    }
    if (!needsBaseUrl) {
        DOM.baseUrl.value = '';
    }
}

// ─── Model Suggestions ───
function showSuggestions() {
    const provider = DOM.provider.value;
    const models = (meta.provider_models || {})[provider] || [];
    const query = DOM.model.value.toLowerCase();

    const filtered = query
        ? models.filter(m => m.toLowerCase().includes(query))
        : models;

    if (filtered.length === 0) {
        DOM.modelSuggestions.classList.remove('visible');
        return;
    }

    DOM.modelSuggestions.innerHTML = filtered.map(m =>
        `<div class="model-suggestion-item" data-model="${m}">${m}</div>`
    ).join('');

    DOM.modelSuggestions.classList.add('visible');

    // Click to select
    DOM.modelSuggestions.querySelectorAll('.model-suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            DOM.model.value = item.dataset.model;
            DOM.modelSuggestions.classList.remove('visible');
        });
    });
}

// ─── Test Connection ───
async function testConnection() {
    const btn = DOM.btnTestConnection;
    const btnText = btn.querySelector('.btn-text');
    const btnSpinner = btn.querySelector('.btn-spinner');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline-flex';

    DOM.testResult.className = 'test-result';
    DOM.testResult.style.display = 'none';
    DOM.testResult.textContent = '';

    try {
        const config = buildConfig();
        const res = await fetch('/api/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        const data = await res.json();

        DOM.testResult.textContent = data.message;
        DOM.testResult.className = `test-result ${data.success ? 'success' : 'error'}`;
    } catch (err) {
        DOM.testResult.textContent = `Network error: ${err.message}`;
        DOM.testResult.className = 'test-result error';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline-flex';
        btnSpinner.style.display = 'none';
    }
}

// ─── Save Config ───
async function saveConfig() {
    const btn = DOM.btnSave;
    const btnText = btn.querySelector('.btn-text');
    const btnSpinner = btn.querySelector('.btn-spinner');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline-flex';

    try {
        const config = buildConfig();
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        const data = await res.json();

        if (data.success) {
            DOM.saveStatus.textContent = '✅ ' + data.message;
            DOM.saveStatus.className = 'save-status success';

            // Shutdown server after a short delay so user sees the success message
            setTimeout(async () => {
                try {
                    await fetch('/api/shutdown', { method: 'POST' });
                } catch {
                    // Expected — server closes
                }
                // Show final message
                document.body.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;gap:1rem;font-family:'Inter',sans-serif;color:#e8e8ed;background:#0a0a0f;">
                        <div style="font-size:3rem;">✅</div>
                        <h2 style="font-weight:600;font-size:1.3rem;">Configuration Saved!</h2>
                        <p style="color:#8b8b9e;font-size:0.9rem;">You can close this tab. Run <code style="background:rgba(99,102,241,0.15);padding:0.2rem 0.6rem;border-radius:6px;color:#a78bfa;font-family:'JetBrains Mono',monospace;">logmaster run "your command"</code> to start.</p>
                    </div>
                `;
            }, 1200);
        } else {
            DOM.saveStatus.textContent = '❌ ' + data.message;
            DOM.saveStatus.className = 'save-status error';
        }
    } catch (err) {
        DOM.saveStatus.textContent = `❌ Save failed: ${err.message}`;
        DOM.saveStatus.className = 'save-status error';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline-flex';
        btnSpinner.style.display = 'none';
    }
}

// ─── Reset Config ───
async function resetConfig() {
    if (!confirm('Reset all settings to defaults? This will reload the page.')) return;

    try {
        // Fetch the default config from server (it will re-read from package default)
        const res = await fetch('/api/config');
        const config = await res.json();
        meta = config._meta || {};
        delete config._meta;
        populateForm(config);

        DOM.saveStatus.textContent = '🔄 Reset to defaults (not saved yet)';
        DOM.saveStatus.className = 'save-status';

        // Clear test result
        DOM.testResult.className = 'test-result';
        DOM.testResult.style.display = 'none';
    } catch (err) {
        DOM.saveStatus.textContent = `❌ Reset failed: ${err.message}`;
        DOM.saveStatus.className = 'save-status error';
    }
}

// ─── Cache: Load Stats ───
async function loadCacheStats() {
    DOM.btnRefreshCache.disabled = true;
    DOM.btnRefreshCache.textContent = '⏳ Loading...';
    DOM.cacheActionResult.textContent = '';
    DOM.cacheActionResult.className = 'cache-action-result';

    try {
        const res = await fetch('/api/cache');
        const json = await res.json();

        if (!json.success) throw new Error(json.message || 'Failed to load cache');

        const data = json.data;

        // Update stat counters
        DOM.cacheTotalEntries.textContent = data.total_entries;
        DOM.cacheTotalHits.textContent = data.total_hits;
        DOM.cacheSize.textContent = formatBytes(data.size_bytes);
        DOM.cachePath.textContent = data.cache_path;

        // Render table
        if (data.entries.length === 0) {
            DOM.cacheTableBody.innerHTML = `<tr><td colspan="4" class="cache-empty">No cached solutions yet — errors will be cached automatically after AI analysis.</td></tr>`;
        } else {
            DOM.cacheTableBody.innerHTML = data.entries.map(e => `
                <tr>
                    <td title="${escapeHtml(e.error_signature)}">${escapeHtml(truncate(e.error_signature, 60))}</td>
                    <td>${escapeHtml(e.type)}</td>
                    <td><span class="cache-hits-badge">${e.hits}</span></td>
                    <td>${formatDate(e.last_seen)}</td>
                </tr>
            `).join('');
        }
    } catch (err) {
        DOM.cacheTableBody.innerHTML = `<tr><td colspan="4" class="cache-empty">⚠ Could not load cache: ${escapeHtml(err.message)}</td></tr>`;
    } finally {
        DOM.btnRefreshCache.disabled = false;
        DOM.btnRefreshCache.textContent = '🔄 Refresh';
    }
}

// ─── Cache: Clear ───
async function clearCache() {
    if (!confirm('Clear all cached error solutions? This cannot be undone.\n\nFuture errors will be re-analyzed by AI and re-cached automatically.')) return;

    const btn = DOM.btnClearCache;
    const btnText = btn.querySelector('.btn-text');
    const btnSpinner = btn.querySelector('.btn-spinner');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline-flex';
    DOM.cacheActionResult.textContent = '';
    DOM.cacheActionResult.className = 'cache-action-result';

    try {
        const res = await fetch('/api/cache', { method: 'DELETE' });
        const data = await res.json();

        if (data.success) {
            DOM.cacheActionResult.textContent = '✅ ' + data.message;
            DOM.cacheActionResult.className = 'cache-action-result success';
            // Refresh the table to show empty state
            await loadCacheStats();
        } else {
            DOM.cacheActionResult.textContent = '❌ ' + (data.message || 'Clear failed');
            DOM.cacheActionResult.className = 'cache-action-result error';
        }
    } catch (err) {
        DOM.cacheActionResult.textContent = `❌ Network error: ${err.message}`;
        DOM.cacheActionResult.className = 'cache-action-result error';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline-flex';
        btnSpinner.style.display = 'none';
    }
}

// ─── Helpers ───
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatDate(isoStr) {
    if (!isoStr) return '—';
    try {
        const d = new Date(isoStr);
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
        return isoStr;
    }
}

function truncate(str, maxLen) {
    return str && str.length > maxLen ? str.slice(0, maxLen) + '…' : (str || '');
}

function escapeHtml(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}


// ─── State ───
let meta = {};  // provider_models, provider_env_vars, config_path

// ─── Initialize ───
document.addEventListener('DOMContentLoaded', init);

async function init() {
    try {
        const res = await fetch('/api/config');
        const config = await res.json();

        meta = config._meta || {};
        delete config._meta;

        populateForm(config);
        setupEventListeners();

        if (meta.config_path) {
            DOM.configPathBadge.textContent = meta.config_path;
        }
    } catch (err) {
        console.error('Failed to load config:', err);
        DOM.saveStatus.textContent = '⚠ Failed to load configuration';
        DOM.saveStatus.className = 'save-status error';
    }
}

// ─── Populate Form ───
function populateForm(config) {
    const ai = config.ai || {};
    const agent = config.agent || {};
    const doc = config.documentation || {};
    const output = config.output || {};

    // AI Provider
    DOM.provider.value = ai.provider || 'groq';
    DOM.model.value = ai.model || '';
    
    // Resolve API key — if it's an env var reference like ${GROQ_API_KEY}, show empty
    const rawKey = ai.api_key || '';
    DOM.apiKey.value = rawKey.startsWith('${') ? '' : rawKey;
    
    DOM.baseUrl.value = ai.base_url || '';
    updateProviderUI();

    // Tuning
    DOM.temperature.value = ai.temperature ?? 0.2;
    DOM.temperatureValue.textContent = ai.temperature ?? 0.2;
    DOM.maxTokens.value = ai.max_tokens ?? 1000;

    // Agent
    DOM.agentUseAI.checked = agent.use_ai_analysis !== false;
    DOM.agentCached.checked = agent.use_cached_solutions !== false;
    DOM.agentFetchDocs.checked = agent.fetch_documentation !== false;
    DOM.agentAutoFix.checked = agent.auto_fix !== false;
    DOM.agentIndependentAutoFix.checked = agent.independent_auto_fix === true;
    DOM.agentAutoRecover.checked = agent.auto_recover === true;
    DOM.agentMaxRetries.value = agent.max_retries ?? 3;

    // Documentation
    DOM.docEnableSearch.checked = doc.enable_search !== false;
    DOM.docSearchEngine.value = doc.search_engine || 'duckduckgo';

    // Output
    DOM.outputVerbose.checked = output.verbose !== false;
    DOM.outputShowAPI.checked = output.show_api_calls !== false;
}

// ─── Build Config Object from Form ───
function buildConfig() {
    return {
        ai: {
            provider: DOM.provider.value,
            model: DOM.model.value,
            api_key: DOM.apiKey.value,
            temperature: parseFloat(DOM.temperature.value),
            max_tokens: parseInt(DOM.maxTokens.value, 10),
            ...(DOM.baseUrl.value ? { base_url: DOM.baseUrl.value } : {}),
        },
        agent: {
            use_cached_solutions: DOM.agentCached.checked,
            fetch_documentation: DOM.agentFetchDocs.checked,
            use_ai_analysis: DOM.agentUseAI.checked,
            auto_fix: DOM.agentAutoFix.checked,
            independent_auto_fix: DOM.agentIndependentAutoFix.checked,
            auto_recover: DOM.agentAutoRecover.checked,
            max_retries: parseInt(DOM.agentMaxRetries.value, 10),
            cached_error_types: ["connection", "import", "memory", "timeout", "permission"],
            complex_error_types: ["syntax", "type", "value", "unknown"],
        },
        documentation: {
            enable_search: DOM.docEnableSearch.checked,
            search_engine: DOM.docSearchEngine.value,
        },
        output: {
            verbose: DOM.outputVerbose.checked,
            show_api_calls: DOM.outputShowAPI.checked,
        },
    };
}

// ─── Event Listeners ───
function setupEventListeners() {
    // Provider change → update model suggestions + env hint + base url visibility
    DOM.provider.addEventListener('change', () => {
        updateProviderUI();
        // Clear model and let them pick from suggestions
        DOM.model.value = '';
        showSuggestions();
    });

    // Temperature slider
    DOM.temperature.addEventListener('input', () => {
        DOM.temperatureValue.textContent = DOM.temperature.value;
    });

    // API key visibility toggle
    DOM.toggleKeyVisibility.addEventListener('click', () => {
        const isPassword = DOM.apiKey.type === 'password';
        DOM.apiKey.type = isPassword ? 'text' : 'password';
        DOM.toggleKeyVisibility.querySelector('.eye-icon').textContent = isPassword ? '🙈' : '👁';
    });

    // Model input → show/filter suggestions
    DOM.model.addEventListener('focus', showSuggestions);
    DOM.model.addEventListener('input', showSuggestions);
    document.addEventListener('click', (e) => {
        if (!DOM.model.contains(e.target) && !DOM.modelSuggestions.contains(e.target)) {
            DOM.modelSuggestions.classList.remove('visible');
        }
    });

    // Test connection
    DOM.btnTestConnection.addEventListener('click', testConnection);

    // Save
    DOM.btnSave.addEventListener('click', saveConfig);

    // Reset
    DOM.btnReset.addEventListener('click', resetConfig);
}

// ─── Provider UI Updates ───
function updateProviderUI() {
    const provider = DOM.provider.value;

    // Update env hint
    const envVars = meta.provider_env_vars || {};
    const envVar = envVars[provider] || `${provider.toUpperCase()}_API_KEY`;
    DOM.envHint.textContent = `env: ${envVar}`;

    // Show/hide base URL field
    const needsBaseUrl = ['nvidia'].includes(provider);
    DOM.baseUrlGroup.style.display = needsBaseUrl ? 'block' : 'none';
}

// ─── Model Suggestions ───
function showSuggestions() {
    const provider = DOM.provider.value;
    const models = (meta.provider_models || {})[provider] || [];
    const query = DOM.model.value.toLowerCase();

    const filtered = query
        ? models.filter(m => m.toLowerCase().includes(query))
        : models;

    if (filtered.length === 0) {
        DOM.modelSuggestions.classList.remove('visible');
        return;
    }

    DOM.modelSuggestions.innerHTML = filtered.map(m =>
        `<div class="model-suggestion-item" data-model="${m}">${m}</div>`
    ).join('');

    DOM.modelSuggestions.classList.add('visible');

    // Click to select
    DOM.modelSuggestions.querySelectorAll('.model-suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            DOM.model.value = item.dataset.model;
            DOM.modelSuggestions.classList.remove('visible');
        });
    });
}

// ─── Test Connection ───
async function testConnection() {
    const btn = DOM.btnTestConnection;
    const btnText = btn.querySelector('.btn-text');
    const btnSpinner = btn.querySelector('.btn-spinner');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline-flex';

    DOM.testResult.className = 'test-result';
    DOM.testResult.style.display = 'none';
    DOM.testResult.textContent = '';

    try {
        const config = buildConfig();
        const res = await fetch('/api/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        const data = await res.json();

        DOM.testResult.textContent = data.message;
        DOM.testResult.className = `test-result ${data.success ? 'success' : 'error'}`;
    } catch (err) {
        DOM.testResult.textContent = `Network error: ${err.message}`;
        DOM.testResult.className = 'test-result error';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline-flex';
        btnSpinner.style.display = 'none';
    }
}

// ─── Save Config ───
async function saveConfig() {
    const btn = DOM.btnSave;
    const btnText = btn.querySelector('.btn-text');
    const btnSpinner = btn.querySelector('.btn-spinner');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline-flex';

    try {
        const config = buildConfig();
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        const data = await res.json();

        if (data.success) {
            DOM.saveStatus.textContent = '✅ ' + data.message;
            DOM.saveStatus.className = 'save-status success';

            // Shutdown server after a short delay so user sees the success message
            setTimeout(async () => {
                try {
                    await fetch('/api/shutdown', { method: 'POST' });
                } catch {
                    // Expected — server closes
                }
                // Show final message
                document.body.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;gap:1rem;font-family:'Inter',sans-serif;color:#e8e8ed;background:#0a0a0f;">
                        <div style="font-size:3rem;">✅</div>
                        <h2 style="font-weight:600;font-size:1.3rem;">Configuration Saved!</h2>
                        <p style="color:#8b8b9e;font-size:0.9rem;">You can close this tab. Run <code style="background:rgba(99,102,241,0.15);padding:0.2rem 0.6rem;border-radius:6px;color:#a78bfa;font-family:'JetBrains Mono',monospace;">logmaster run "your command"</code> to start.</p>
                    </div>
                `;
            }, 1200);
        } else {
            DOM.saveStatus.textContent = '❌ ' + data.message;
            DOM.saveStatus.className = 'save-status error';
        }
    } catch (err) {
        DOM.saveStatus.textContent = `❌ Save failed: ${err.message}`;
        DOM.saveStatus.className = 'save-status error';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline-flex';
        btnSpinner.style.display = 'none';
    }
}

// ─── Reset Config ───
async function resetConfig() {
    if (!confirm('Reset all settings to defaults? This will reload the page.')) return;

    try {
        // Fetch the default config from server (it will re-read from package default)
        const res = await fetch('/api/config');
        const config = await res.json();
        meta = config._meta || {};
        delete config._meta;
        populateForm(config);

        DOM.saveStatus.textContent = '🔄 Reset to defaults (not saved yet)';
        DOM.saveStatus.className = 'save-status';

        // Clear test result
        DOM.testResult.className = 'test-result';
        DOM.testResult.style.display = 'none';
    } catch (err) {
        DOM.saveStatus.textContent = `❌ Reset failed: ${err.message}`;
        DOM.saveStatus.className = 'save-status error';
    }
}
