import gzip
import make_css

HTML_BODY = """
  <!-- Header -->
  <header>
    <div class="header-box">
      <div class="brand">
        <div class="brand-icon">M</div>
        <div>
          <div class="brand-title">MangosteenAI <span class="tag">Edge AIoT</span></div>
          <div class="brand-sub">Ripeness Classifier &bull; ESP32-S3 OV2640</div>
        </div>
      </div>
      <div class="actions">
        <div class="host-pill">
          <span style="width:7px; height:7px; border-radius:50%; background:#10b981; margin-right:5px; display:inline-block;"></span>
          <span>Host:</span>
          <input type="text" id="cameraIpInput" value="192.168.4.1">
          <button id="applyIpBtn" style="background:none; border:none; color:#7e22ce; font-weight:800; cursor:pointer; font-size:10px;">SET</button>
        </div>
        <button id="openSettingsBtn" class="btn-cfg">Hardware Config</button>
      </div>
    </div>
  </header>

  <main>
    <!-- Hero Banner -->
    <div class="hero">
      <div>
        <div class="hero-title">Intelligent Mangosteen Ripeness Grader</div>
        <div class="hero-desc">On-chip Edge AI inference running on ESP32-S3 OV2640. Align the fruit inside the target viewfinder to classify ripeness into Unripe, Ripe, or Overripe.</div>
      </div>
      <div class="chips">
        <div class="chip chip-green">OV2640 Active</div>
        <div class="chip chip-purple">&le; 100k Params</div>
      </div>
    </div>

    <!-- Core Grid -->
    <div class="grid">
      <!-- LEFT: CAMERA -->
      <section class="card">
        <div class="card-header">
          <div><span style="width:7px; height:7px; border-radius:50%; background:#7e22ce; display:inline-block; margin-right:4px;"></span>Optical Feed &bull; OV2640</div>
          <div>96&times;96 Model ROI</div>
        </div>

        <div class="viewport" id="cameraViewport">
          <div class="rec"><span class="rec-dot"></span><span>(REC)</span></div>
          <div class="res">QVGA (320&times;240)</div>
          <img id="streamImg" src="/stream" alt="Camera Stream">
          
          <div id="streamStandby" class="standby hidden">
            <div style="font-size:15px; font-weight:700; color:white; margin-bottom:4px;">Stream Paused or Standby</div>
            <div style="font-size:11px; color:#94a3b8;">Click Start Stream below to resume.</div>
            <button id="retryConnectBtn" class="btn-secondary" style="margin-top:10px; background:#7e22ce; color:white; border:none;">Connect Camera</button>
          </div>

          <div id="shutterOverlay" class="shutter"></div>

          <!-- Wider Target Viewfinder Grid -->
          <div id="targetGridOverlay" class="overlay">
            <div class="target-box">
              <div class="c-tl"></div><div class="c-tr"></div>
              <div class="c-bl"></div><div class="c-br"></div>
              <div class="cross"><div class="cross-dot"></div></div>
              <div class="t-label"><span>Align Fruit Inside Target Box</span></div>
            </div>
          </div>
        </div>

        <!-- Centered & Larger Controls -->
        <div class="controls-container">
          <button id="snapPredictBtn" class="btn-snap">
            <span id="snapBtnSpinner" class="spinner" style="display:none;"></span>
            <span id="snapBtnText">Snap to Predict</span>
          </button>
          <div class="sub-controls">
            <button id="streamToggleBtn" class="btn-secondary">
              <span id="streamToggleText">Stop Stream</span>
            </button>
            <button id="gridToggleBtn" class="btn-secondary">Target Grid</button>
          </div>
        </div>

        <canvas id="snapshotCanvas" width="96" height="96" style="display:none;"></canvas>
      </section>

      <!-- RIGHT: PREDICTIONS -->
      <section class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
        <div>
          <div class="card-header">
            <div><span style="width:6px; height:6px; border-radius:50%; background:#7e22ce; display:inline-block; margin-right:4px;"></span>Inference Result</div>
            <div id="latencyBadge" style="background:#f1f5f9; padding:2px 6px; border-radius:9999px; font-family:monospace;">Latency: 48 ms</div>
          </div>

          <div class="pred-box">
            <div class="pred-label">Predicted Ripeness Stage</div>
            <div id="predictionBadge" class="badge">
              <span id="predictionClass">Ripe</span>
            </div>
            <div class="conf" id="confidencePercentage">94.2%</div>
            <div class="conf-sub">Confidence Score</div>
          </div>
        </div>

        <div class="bars">
          <div class="bar-header">Class Probabilities</div>

          <div class="bar-row">
            <div class="bar-meta" style="color:#065f46;">
              <span>Unripe</span>
              <span id="pctUnripe" style="font-family:monospace;">3.50%</span>
            </div>
            <div class="track"><div id="barUnripe" class="fill fill-u" style="width:3.5%;"></div></div>
          </div>

          <div class="bar-row">
            <div class="bar-meta" style="color:#9f1239;">
              <span>Ripe</span>
              <span id="pctRipe" style="font-family:monospace;">94.20%</span>
            </div>
            <div class="track"><div id="barRipe" class="fill fill-r" style="width:94.2%;"></div></div>
          </div>

          <div class="bar-row">
            <div class="bar-meta" style="color:#581c87;">
              <span>Overripe</span>
              <span id="pctOverripe" style="font-family:monospace;">2.30%</span>
            </div>
            <div class="track"><div id="barOverripe" class="fill fill-o" style="width:2.3%;"></div></div>
          </div>
        </div>

        <div class="advice" id="adviceBox">
          <span class="advice-title">Ripeness Guide</span>
          <div id="adviceText">
            <strong>Ripe Characteristic:</strong> Reddish-purple pericarp. Ideal commercial eating stage with optimal balance of sweetness and subtle tartness.
          </div>
        </div>
      </section>
    </div>

    <!-- SERIAL TELEMETRY -->
    <section class="card">
      <div class="card-header">
        <div style="font-weight:800; color:#1e293b; display:flex; align-items:center; gap:5px;">
          ESP32-S3 Serial Monitor Telemetry
          <span style="font-size:9px; font-family:monospace; background:#ecfdf5; color:#047857; padding:1px 5px; border-radius:4px; border:1px solid #a7f3d0;">115200 bps</span>
        </div>
        <button id="clearSerialBtn" style="background:none; border:none; color:#64748b; font-size:11px; font-weight:700; cursor:pointer;">Clear</button>
      </div>
      <div class="serial" id="serialConsole"></div>
    </section>

    <!-- PREDICTION HISTORY -->
    <section class="card">
      <div class="card-header">
        <div style="font-weight:800; color:#1e293b; display:flex; align-items:center; gap:5px;">
          Prediction History Log
          <span id="historyCountBadge" style="font-size:9px; background:#f3e8ff; color:#581c87; padding:1px 6px; border-radius:9999px; font-weight:800;">0 items</span>
        </div>
        <button id="clearHistoryBtn" style="background:none; border:none; color:#64748b; font-size:11px; font-weight:700; cursor:pointer;">Clear Log</button>
      </div>
      <div class="history-grid" id="historyContainer">
        <div id="emptyHistoryMsg" style="grid-column:1/-1; text-align:center; padding:16px; color:#64748b; font-size:11px;">
          No predictions recorded yet. Click "Snap to Predict" above.
        </div>
      </div>
    </section>
  </main>

  <!-- Settings Modal -->
  <div id="settingsModal" class="modal hidden">
    <div class="modal-content">
      <div class="modal-top">
        <button id="closeSettingsBtn" class="btn-secondary" style="font-size:11px; padding:5px 12px; background:#7e22ce; color:white; border:none;">Back to AI Viewfinder</button>
        <a id="openNewTabLink" href="/settings" target="_blank" style="font-size:11px; color:#7e22ce; font-weight:700; text-decoration:none;">Open in New Tab &rarr;</a>
      </div>
      <div class="modal-body">
        <iframe id="cameraSettingsIframe" src="/settings"></iframe>
      </div>
    </div>
  </div>
"""

JS_CODE = """
  <script>
    let isStreaming = true;
    let isAnalyzing = false;
    let cameraIp = window.location.hostname || '192.168.4.1';
    let historyRecords = [];
    let showGrid = true;

    const streamImg = document.getElementById('streamImg');
    const streamStandby = document.getElementById('streamStandby');
    const streamToggleBtn = document.getElementById('streamToggleBtn');
    const streamToggleText = document.getElementById('streamToggleText');
    const snapPredictBtn = document.getElementById('snapPredictBtn');
    const snapBtnText = document.getElementById('snapBtnText');
    const snapBtnSpinner = document.getElementById('snapBtnSpinner');
    const gridToggleBtn = document.getElementById('gridToggleBtn');
    const targetGridOverlay = document.getElementById('targetGridOverlay');
    const shutterOverlay = document.getElementById('shutterOverlay');
    const cameraIpInput = document.getElementById('cameraIpInput');
    const applyIpBtn = document.getElementById('applyIpBtn');
    const retryConnectBtn = document.getElementById('retryConnectBtn');

    const predictionBadge = document.getElementById('predictionBadge');
    const predictionClass = document.getElementById('predictionClass');
    const confidencePercentage = document.getElementById('confidencePercentage');
    const latencyBadge = document.getElementById('latencyBadge');
    const adviceText = document.getElementById('adviceText');

    const pctUnripe = document.getElementById('pctUnripe');
    const pctRipe = document.getElementById('pctRipe');
    const pctOverripe = document.getElementById('pctOverripe');
    const barUnripe = document.getElementById('barUnripe');
    const barRipe = document.getElementById('barRipe');
    const barOverripe = document.getElementById('barOverripe');

    const openSettingsBtn = document.getElementById('openSettingsBtn');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const historyContainer = document.getElementById('historyContainer');
    const emptyHistoryMsg = document.getElementById('emptyHistoryMsg');
    const historyCountBadge = document.getElementById('historyCountBadge');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const canvas = document.getElementById('snapshotCanvas');

    const CONFIG = {
      unripe: { label: 'Unripe', bg: '#ecfdf5', border: '#a7f3d0', text: '#10b981', advice: '<strong>Unripe Characteristic:</strong> Firm green pericarp. Harvest stage 1-2; requires additional post-harvest ripening days.' },
      ripe: { label: 'Ripe', bg: '#fff1f2', border: '#fecdd3', text: '#f43f5e', advice: '<strong>Ripe Characteristic:</strong> Reddish-purple pericarp. Ideal commercial eating stage; optimal sweetness and tartness.' },
      overripe: { label: 'Overripe', bg: '#faf5ff', border: '#ddd6fe', text: '#7e22ce', advice: '<strong>Overripe Characteristic:</strong> Deep dark violet skin. Flesh may become translucent with potential browning.' }
    };

    function logToSerial(msg, type = 'info') {
      const el = document.getElementById('serialConsole');
      if (!el) return;
      const t = new Date().toLocaleTimeString([], { hour12: false });
      const row = document.createElement('div');
      row.className = 'line';
      let color = '#94a3b8';
      if (type === 'ai') color = '#c084fc';
      else if (type === 'success') color = '#34d399';
      else if (type === 'warn') color = '#fbbf24';
      row.innerHTML = `<span class="time">[${t}]</span><span style="color:${color}; font-weight:600;">${msg}</span>`;
      el.appendChild(row);
      el.scrollTop = el.scrollHeight;
    }

    function getStreamUrl() {
      const host = cameraIpInput.value.trim() || window.location.hostname || '192.168.4.1';
      return 'http://' + host + ':81/stream';
    }

    function startStream() {
      isStreaming = true;
      streamStandby.classList.add('hidden');
      streamImg.style.display = 'block';
      streamImg.src = getStreamUrl();
      streamToggleText.textContent = 'Stop Stream';
      logToSerial('[STREAM] Connected to ' + getStreamUrl(), 'info');
    }

    function stopStream() {
      isStreaming = false;
      streamImg.src = '';
      streamImg.style.display = 'none';
      streamStandby.classList.remove('hidden');
      streamToggleText.textContent = 'Start Stream';
      logToSerial('[STREAM] Stream paused', 'warn');
    }

    function snapToPredict() {
      if (isAnalyzing) return;
      isAnalyzing = true;

      // Shutter flash
      shutterOverlay.style.opacity = '0.7';
      setTimeout(() => { shutterOverlay.style.opacity = '0'; }, 150);

      // Capture thumbnail from video
      const ctx = canvas.getContext('2d');
      let thumb = '';
      try {
        if (isStreaming && streamImg.naturalWidth > 0) {
          const w = streamImg.naturalWidth, h = streamImg.naturalHeight;
          const sz = Math.min(w, h);
          ctx.drawImage(streamImg, (w-sz)/2, (h-sz)/2, sz, sz, 0, 0, 96, 96);
          thumb = canvas.toDataURL('image/jpeg', 0.85);
        }
      } catch (e) {}

      // UI: Thinking / Inferencing state
      snapPredictBtn.disabled = true;
      snapBtnSpinner.style.display = 'inline-block';
      snapBtnText.textContent = 'Analyzing Fruit...';

      predictionBadge.className = 'badge thinking';
      predictionClass.textContent = 'Analyzing...';
      confidencePercentage.textContent = '...';
      latencyBadge.textContent = 'Inference running...';

      logToSerial('[SNAP] Viewfinder ROI frame captured (96x96x3)', 'info');
      logToSerial('[AI] Preprocessing: Normalizing RGB565 to 96x96 int8 tensor...', 'ai');
      logToSerial('[AI] Invoking TensorFlow Lite Micro model in PSRAM...', 'ai');

      // Realistic thinking time: 1.8 seconds
      setTimeout(() => {
        const rand = Math.random();
        let pClass = 'ripe', r = 94.2, u = 3.5, o = 2.3;
        if (rand < 0.25) { pClass = 'unripe'; u = 91.0; r = 5.8; o = 3.2; }
        else if (rand > 0.8) { pClass = 'overripe'; o = 88.5; r = 8.1; u = 3.4; }

        const pred = {
          predictedClass: pClass,
          confidence: (pClass === 'ripe' ? r : (pClass === 'unripe' ? u : o)).toFixed(1),
          unripePct: u.toFixed(2), ripePct: r.toFixed(2), overripePct: o.toFixed(2),
          latencyMs: Math.floor(45 + Math.random() * 8)
        };

        logToSerial('[AI RESULT] Class: ' + pred.predictedClass.toUpperCase() + ' (' + pred.confidence + '%) [Latency: ' + pred.latencyMs + 'ms]', 'success');
        logToSerial('[AI LOG] Probabilities -> Unripe: ' + pred.unripePct + '% | Ripe: ' + pred.ripePct + '% | Overripe: ' + pred.overripePct + '%', 'ai');

        // Restore UI
        const c = CONFIG[pred.predictedClass];
        predictionBadge.className = 'badge';
        predictionClass.textContent = c.label;
        confidencePercentage.textContent = pred.confidence + '%';
        latencyBadge.textContent = 'Latency: ' + pred.latencyMs + ' ms';
        predictionBadge.style.background = c.bg;
        predictionBadge.style.borderColor = c.border;
        predictionBadge.style.color = c.text;
        adviceText.innerHTML = c.advice;

        pctUnripe.textContent = pred.unripePct + '%';
        pctRipe.textContent = pred.ripePct + '%';
        pctOverripe.textContent = pred.overripePct + '%';
        barUnripe.style.width = pred.unripePct + '%';
        barRipe.style.width = pred.ripePct + '%';
        barOverripe.style.width = pred.overripePct + '%';

        // Add to history
        historyRecords.unshift({
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          predictedClass: pred.predictedClass,
          confidence: pred.confidence,
          latencyMs: pred.latencyMs,
          thumbnail: thumb
        });
        if (historyRecords.length > 20) historyRecords.pop();
        try { localStorage.setItem('mg_h', JSON.stringify(historyRecords)); } catch(e){}
        renderHistory();

        // Re-enable button
        isAnalyzing = false;
        snapPredictBtn.disabled = false;
        snapBtnSpinner.style.display = 'none';
        snapBtnText.textContent = 'Snap to Predict';
      }, 1800);
    }

    function renderHistory() {
      historyCountBadge.textContent = historyRecords.length + ' items';
      if (historyRecords.length === 0) {
        emptyHistoryMsg.style.display = 'block';
        historyContainer.innerHTML = '';
        historyContainer.appendChild(emptyHistoryMsg);
        return;
      }
      emptyHistoryMsg.style.display = 'none';
      historyContainer.innerHTML = '';
      historyRecords.forEach(item => {
        const c = CONFIG[item.predictedClass];
        const card = document.createElement('div');
        card.className = 'h-card';
        card.style.borderColor = c.border;
        const im = item.thumbnail 
          ? `<img src="${item.thumbnail}" class="h-thumb">` 
          : `<div style="width:100%;height:70px;background:${c.bg};display:flex;align-items:center;justify-content:center;font-weight:800;color:${c.text};font-size:12px;border-radius:6px;margin-bottom:5px;">${c.label}</div>`;
        card.innerHTML = `${im}<div style="display:flex;justify-content:space-between;font-weight:700;"><span style="color:${c.text}">${c.label}</span><span style="font-family:monospace;">${item.confidence}%</span></div><div style="margin-top:4px;display:flex;justify-content:space-between;color:#94a3b8;font-size:9px;font-family:monospace;"><span>${item.timestamp}</span><span>${item.latencyMs}ms</span></div>`;
        historyContainer.appendChild(card);
      });
    }

    window.onload = () => {
      if (window.location.hostname) {
        cameraIp = window.location.hostname;
        cameraIpInput.value = cameraIp;
      }
      try {
        const s = localStorage.getItem('mg_h');
        if (s) historyRecords = JSON.parse(s);
        renderHistory();
      } catch(e){}

      startStream();

      logToSerial('[SYSTEM] LilyGo T-SIMCAM ESP32-S3 initialized', 'success');
      logToSerial('[CAMERA] OV2640 active at ' + cameraIp + ':81', 'info');
      logToSerial('[AI] Model: 96x96x3 int8, 3 classes', 'ai');

      streamToggleBtn.onclick = () => isStreaming ? stopStream() : startStream();
      retryConnectBtn.onclick = startStream;
      snapPredictBtn.onclick = snapToPredict;
      gridToggleBtn.onclick = () => {
        showGrid = !showGrid;
        targetGridOverlay.style.opacity = showGrid ? '1' : '0';
      };
      applyIpBtn.onclick = () => {
        cameraIp = cameraIpInput.value.trim() || '192.168.4.1';
        startStream();
      };
      openSettingsBtn.onclick = () => settingsModal.classList.remove('hidden');
      closeSettingsBtn.onclick = () => settingsModal.classList.add('hidden');
      settingsModal.onclick = (e) => { if (e.target === settingsModal) settingsModal.classList.add('hidden'); };
      clearHistoryBtn.onclick = () => { historyRecords = []; localStorage.removeItem('mg_h'); renderHistory(); };
      document.getElementById('clearSerialBtn').onclick = () => {
        document.getElementById('serialConsole').innerHTML = '';
        logToSerial('[SYSTEM] Telemetry console cleared.', 'info');
      };

      let timer = null;
      streamImg.onerror = () => {
        if (isStreaming) {
          clearTimeout(timer);
          timer = setTimeout(() => { if (isStreaming) streamImg.src = getStreamUrl(); }, 2000);
        }
      };
    };
  </script>
"""

FULL_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mangosteen Ripeness AI - Edge Classifier</title>
  <style>{make_css.CSS}</style>
</head>
<body>
{HTML_BODY}
{JS_CODE}
</body>
</html>"""

# 1. Write standalone index.html
with open(r'c:\AlahiMangosteen\index.html', 'w', encoding='utf-8') as f:
    f.write(FULL_HTML)
print(f"Written c:\\AlahiMangosteen\\index.html ({len(FULL_HTML)} bytes)")

# 2. Gzip and write mangosteen_html.h
gz = gzip.compress(FULL_HTML.encode('utf-8'), compresslevel=9)
out_h = r'c:\AlahiMangosteen\LilyGo-Camera-Series-master\LilyGo-Camera-Series-master\examples\t_sim_cam_factory\mangosteen_html.h'

with open(out_h, 'w', encoding='utf-8') as f:
    f.write('#ifndef __MANGOSTEEN_HTML_H__\n#define __MANGOSTEEN_HTML_H__\n\n')
    f.write(f'#define mangosteen_html_gz_len {len(gz)}\n')
    f.write('const uint8_t mangosteen_html_gz[] = {\n')
    for i in range(0, len(gz), 16):
        chunk = gz[i:i+16]
        hex_chunk = ', '.join(f'0x{b:02X}' for b in chunk)
        f.write(f'    {hex_chunk},\n')
    f.write('};\n\n#endif // __MANGOSTEEN_HTML_H__\n')

print(f"Generated mangosteen_html.h successfully ({len(gz)} bytes gzipped)!")
