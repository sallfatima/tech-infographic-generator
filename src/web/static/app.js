let currentImageUrl = null;
let currentFilename = null;
let currentMode = 'standard'; // 'standard' or 'pro'

function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    // Update button text
    const genBtn = document.getElementById('generate-btn');
    genBtn.textContent = mode === 'pro' ? 'Generate Pro (3 Agents)' : 'Generate Infographic';
}

function getFormData() {
    const text = document.getElementById('input-text').value.trim();
    const type = document.getElementById('type-select').value || null;
    const theme = document.getElementById('theme-select').value;
    const format = document.getElementById('format-select').value;
    const size = document.getElementById('size-select').value.split('x');
    return {
        text,
        infographic_type: type,
        theme,
        format,
        width: parseInt(size[0]),
        height: parseInt(size[1]),
        frame_duration: 500,
    };
}

function showLoading(message) {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('loading-text').textContent = message;
    document.getElementById('result').classList.add('hidden');
    document.getElementById('json-view').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('generate-btn').disabled = true;
    // Hide pipeline summary from previous run
    const summaryEl = document.getElementById('pipeline-summary');
    if (summaryEl) summaryEl.classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('generate-btn').disabled = false;
}

function showError(message) {
    hideLoading();
    hidePipelineProgress();
    document.getElementById('error').classList.remove('hidden');
    document.getElementById('error-text').textContent = message;
}

// ---- Pipeline progress (Pro mode) ----

function showPipelineProgress() {
    const el = document.getElementById('pipeline-progress');
    el.classList.remove('hidden');
    // Reset all steps
    document.querySelectorAll('.pipeline-step').forEach(step => {
        step.classList.remove('active', 'completed');
    });
    document.querySelectorAll('.step-connector').forEach(c => {
        c.classList.remove('active');
    });
}

function hidePipelineProgress() {
    document.getElementById('pipeline-progress').classList.add('hidden');
}

function activatePipelineStep(stepName) {
    const steps = ['research', 'structure', 'render'];
    const idx = steps.indexOf(stepName);

    document.querySelectorAll('.pipeline-step').forEach((step, i) => {
        if (i < idx) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (i === idx) {
            step.classList.add('active');
            step.classList.remove('completed');
        }
    });

    document.querySelectorAll('.step-connector').forEach((c, i) => {
        c.classList.toggle('active', i < idx);
    });
}

function completePipelineStep(stepName) {
    const step = document.querySelector(`.pipeline-step[data-step="${stepName}"]`);
    if (step) {
        step.classList.remove('active');
        step.classList.add('completed');
    }
}

function completeAllPipelineSteps() {
    document.querySelectorAll('.pipeline-step').forEach(step => {
        step.classList.remove('active');
        step.classList.add('completed');
    });
    document.querySelectorAll('.step-connector').forEach(c => {
        c.classList.add('active');
    });
}

// ---- Generation ----

async function generate() {
    const data = getFormData();
    if (!data.text) {
        showError('Please enter a text description or paste a LinkedIn post.');
        return;
    }

    if (currentMode === 'pro') {
        await generatePro(data);
    } else {
        await generateStandard(data);
    }
}

async function generateStandard(data) {
    showLoading('Analyzing text with AI...');
    hidePipelineProgress();

    try {
        setTimeout(() => {
            const loadingEl = document.getElementById('loading-text');
            if (!document.getElementById('loading').classList.contains('hidden')) {
                loadingEl.textContent = 'Rendering infographic...';
            }
        }, 3000);

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Generation failed');
        }

        const result = await response.json();
        hideLoading();
        showResult(result, data);

    } catch (err) {
        showError(err.message);
    }
}

async function generatePro(data) {
    showLoading('Starting multi-agent pipeline...');
    showPipelineProgress();

    try {
        // Simulate step progression while waiting for the API response
        activatePipelineStep('research');
        document.getElementById('loading-text').textContent = 'Agent 1: Searching visual references...';

        const stepTimer1 = setTimeout(() => {
            completePipelineStep('research');
            activatePipelineStep('structure');
            document.getElementById('loading-text').textContent = 'Agent 2: Building infographic structure...';
        }, 3000);

        const stepTimer2 = setTimeout(() => {
            completePipelineStep('structure');
            activatePipelineStep('render');
            document.getElementById('loading-text').textContent = 'Agent 3: Rendering final image...';
        }, 12000);

        const proData = {
            text: data.text,
            infographic_type: data.infographic_type,
            theme: data.theme,
            format: data.format,
            width: data.width,
            height: data.height,
            frame_duration: data.frame_duration,
            enable_research: true,
            enable_quality_check: false,
        };

        const response = await fetch('/api/generate-pro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(proData),
        });

        // Clear simulated timers
        clearTimeout(stepTimer1);
        clearTimeout(stepTimer2);

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Pro generation failed');
        }

        const result = await response.json();
        hideLoading();
        completeAllPipelineSteps();
        showProResult(result, data);

    } catch (err) {
        showError(err.message);
    }
}

function showResult(result, data) {
    currentImageUrl = result.image_url;
    currentFilename = result.filename;

    document.getElementById('result').classList.remove('hidden');
    document.getElementById('preview-img').src = result.image_url + '?t=' + Date.now();
    document.getElementById('result-info').textContent =
        `${result.infographic_data.type} | ${data.theme} | ${result.generation_time}s | ${result.format.toUpperCase()}`;

    document.getElementById('json-view').classList.remove('hidden');
    document.getElementById('json-content').textContent =
        JSON.stringify(result.infographic_data, null, 2);
}

function showProResult(result, data) {
    currentImageUrl = result.image_url;
    currentFilename = result.filename;

    document.getElementById('result').classList.remove('hidden');
    document.getElementById('preview-img').src = result.image_url + '?t=' + Date.now();

    // Build info with pipeline details
    const summary = result.pipeline_summary || {};
    const steps = summary.pipeline_steps || [];
    const timingStr = steps.map(s => `${s.name}: ${s.duration}s`).join(' | ');
    const researchInfo = summary.research_summary ? ` | refs: ${summary.research_summary.references_found}` : '';

    document.getElementById('result-info').textContent =
        `PRO | ${result.infographic_data.type || 'auto'} | ${timingStr}${researchInfo} | Total: ${result.generation_time}s`;

    // Show pipeline summary
    showPipelineSummary(summary);

    // Show JSON
    document.getElementById('json-view').classList.remove('hidden');
    document.getElementById('json-content').textContent =
        JSON.stringify(result.infographic_data, null, 2);
}

function showPipelineSummary(summary) {
    let el = document.getElementById('pipeline-summary');
    if (!el) {
        el = document.createElement('div');
        el.id = 'pipeline-summary';
        el.className = 'pipeline-summary';
        document.querySelector('.output').insertBefore(el, document.getElementById('json-view'));
    }
    el.classList.remove('hidden');

    const steps = summary.pipeline_steps || [];
    const research = summary.research_summary;
    const warnings = summary.warnings || [];

    let html = '<h3>Pipeline Summary</h3><div class="summary-grid">';

    for (const step of steps) {
        const statusIcon = step.status === 'completed' ? '&#10003;' : '&#10007;';
        const statusClass = step.status === 'completed' ? 'success' : 'fail';
        html += `<div class="summary-item ${statusClass}">
            <span class="summary-icon">${statusIcon}</span>
            <span class="summary-name">${step.name}</span>
            <span class="summary-time">${step.duration}s</span>
        </div>`;
    }
    html += '</div>';

    if (research) {
        html += `<div class="summary-research">
            <strong>Research:</strong> ${research.topic || 'N/A'}
            ${research.keywords?.length ? `<br><em>Keywords: ${research.keywords.join(', ')}</em>` : ''}
            ${research.references_found ? `<br>References found: ${research.references_found}` : ''}
            ${research.suggested_type ? `<br>Suggested type: ${research.suggested_type}` : ''}
        </div>`;
    }

    if (warnings.length > 0) {
        html += `<div class="summary-warnings">
            <strong>Warnings:</strong><ul>${warnings.map(w => `<li>${w}</li>`).join('')}</ul>
        </div>`;
    }

    el.innerHTML = html;
}

// ---- Analyze ----

async function analyzeOnly() {
    const data = getFormData();
    if (!data.text) {
        showError('Please enter a text description.');
        return;
    }

    showLoading('Analyzing text with AI...');
    hidePipelineProgress();

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Analysis failed');
        }

        const result = await response.json();
        hideLoading();

        document.getElementById('result').classList.add('hidden');
        document.getElementById('json-view').classList.remove('hidden');
        document.getElementById('json-content').textContent =
            JSON.stringify(result.data, null, 2);

    } catch (err) {
        showError(err.message);
    }
}

// ---- Download ----

function downloadImage() {
    if (!currentImageUrl) return;
    const a = document.createElement('a');
    a.href = currentImageUrl;
    a.download = currentFilename || 'infographic.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// ---- Keyboard shortcut ----

document.getElementById('input-text').addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        generate();
    }
});
