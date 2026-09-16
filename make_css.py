CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: linear-gradient(135deg, #faf5ff 0%, #f8fafc 50%, #f3e8ff 100%);
  color: #0f172a;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
header {
  position: sticky; top: 0; z-index: 40;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #e9d5ff;
  padding: 10px 16px;
}
.header-box {
  max-width: 1200px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
}
.brand { display: flex; align-items: center; gap: 10px; }
.brand-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #7e22ce, #9333ea);
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 900; font-size: 16px;
  box-shadow: 0 4px 10px rgba(126,34,206,0.25);
  letter-spacing: -0.5px;
}
.brand-title { font-size: 17px; font-weight: 800; color: #1e1b4b; display: flex; align-items: center; gap: 6px; }
.tag { font-size: 10px; font-weight: 700; background: #f3e8ff; color: #581c87; padding: 2px 7px; border-radius: 9999px; border: 1px solid #e9d5ff; }
.brand-sub { font-size: 11px; color: #64748b; }
.actions { display: flex; align-items: center; gap: 8px; }
.host-pill {
  display: flex; align-items: center; background: #faf5ff;
  border: 1px solid #e9d5ff; border-radius: 8px; padding: 4px 8px;
  font-size: 11px; color: #581c87;
}
.host-pill input {
  background: none; border: none; border-bottom: 1px solid #c084fc;
  width: 90px; font-family: monospace; font-weight: 600; font-size: 11px;
  color: #581c87; margin: 0 4px; outline: none;
}
.btn-cfg {
  background: white; border: 1px solid #cbd5e1; border-radius: 8px;
  padding: 6px 12px; font-size: 11px; font-weight: 700; color: #334155;
  cursor: pointer; display: flex; align-items: center; gap: 4px;
  transition: all 0.15s;
}
.btn-cfg:hover { background: #f3e8ff; color: #7e22ce; border-color: #d8b4fe; }

main {
  flex: 1; max-width: 1200px; width: 100%; margin: 0 auto;
  padding: 16px 12px; display: flex; flex-direction: column; gap: 16px;
}
.hero {
  background: white; border-radius: 14px; padding: 16px;
  border: 1px solid #e9d5ff; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
}
.hero-title { font-size: 18px; font-weight: 800; color: #1e1b4b; }
.hero-desc { font-size: 12px; color: #64748b; margin-top: 3px; max-width: 720px; }
.chips { display: flex; gap: 6px; }
.chip { font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 9999px; }
.chip-green { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
.chip-purple { background: #faf5ff; color: #6b21a8; border: 1px solid #e9d5ff; }

.grid {
  display: grid; grid-template-columns: 1.25fr 1fr; gap: 16px;
}
@media (max-width: 850px) { .grid { grid-template-columns: 1fr; } }

.card {
  background: white; border-radius: 14px; padding: 16px;
  border: 1px solid #e9d5ff; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px; font-size: 11px; color: #64748b; font-weight: 600;
}
.viewport {
  position: relative; width: 100%; aspect-ratio: 4/3;
  background: #020617; border-radius: 10px; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
}
.viewport img { width: 100%; height: 100%; object-fit: cover; display: block; }
.rec {
  position: absolute; top: 10px; right: 10px; z-index: 20;
  background: rgba(0,0,0,0.65); backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.15); border-radius: 9999px;
  padding: 3px 8px; display: flex; align-items: center; gap: 5px;
  color: #f87171; font-family: monospace; font-size: 10px; font-weight: 800;
}
.rec-dot {
  width: 7px; height: 7px; border-radius: 50%; background: #ef4444;
  box-shadow: 0 0 6px #ef4444; animation: pulse 1s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.res {
  position: absolute; top: 10px; left: 10px; z-index: 20;
  background: rgba(0,0,0,0.55); border-radius: 5px; padding: 2px 6px;
  color: #cbd5e1; font-family: monospace; font-size: 10px;
}
.overlay {
  position: absolute; inset: 0; display: flex; align-items: center;
  justify-content: center; pointer-events: none; transition: opacity 0.2s;
}

/* Larger, wider targeting grid */
.target-box {
  position: relative; width: 270px; height: 270px;
  max-width: 82%; max-height: 82%;
  border: 2px dashed rgba(192, 132, 252, 0.85); border-radius: 14px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.35);
  background-size: 33.33% 33.33%;
  background-image: 
    linear-gradient(to right, rgba(255,255,255,0.2) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255,255,255,0.2) 1px, transparent 1px);
}
.c-tl { position: absolute; top: -2px; left: -2px; width: 22px; height: 22px; border-top: 3.5px solid #e9d5ff; border-left: 3.5px solid #e9d5ff; border-top-left-radius: 6px; }
.c-tr { position: absolute; top: -2px; right: -2px; width: 22px; height: 22px; border-top: 3.5px solid #e9d5ff; border-right: 3.5px solid #e9d5ff; border-top-right-radius: 6px; }
.c-bl { position: absolute; bottom: -2px; left: -2px; width: 22px; height: 22px; border-bottom: 3.5px solid #e9d5ff; border-left: 3.5px solid #e9d5ff; border-bottom-left-radius: 6px; }
.c-br { position: absolute; bottom: -2px; right: -2px; width: 22px; height: 22px; border-bottom: 3.5px solid #e9d5ff; border-right: 3.5px solid #e9d5ff; border-bottom-right-radius: 6px; }
.cross { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
.cross-dot { width: 6px; height: 6px; border-radius: 50%; background: #c084fc; border: 1px solid white; }
.t-label { position: absolute; bottom: -26px; left: 0; right: 0; text-align: center; }
.t-label span { background: rgba(0,0,0,0.75); color: #e9d5ff; padding: 2px 10px; border-radius: 9999px; font-size: 10px; font-weight: 700; border: 1px solid rgba(192, 132, 252, 0.4); }

.shutter { position: absolute; inset: 0; background: white; opacity: 0; pointer-events: none; transition: opacity 0.15s; }
.standby {
  position: absolute; inset: 0; background: linear-gradient(135deg, #0f172a, #3b0764, #0f172a);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 16px; text-align: center; color: #cbd5e1;
}
.standby.hidden { display: none; }

/* Centered & Larger Controls Layout */
.controls-container {
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; margin-top: 14px; padding-top: 14px; border-top: 1px solid #f1f5f9;
}
.btn-snap {
  width: 100%; max-width: 320px; padding: 14px 24px;
  font-size: 15px; font-weight: 800; letter-spacing: 0.5px;
  border-radius: 12px; border: none; cursor: pointer;
  background: linear-gradient(135deg, #7e22ce, #9333ea 50%, #e11d48 100%);
  color: white; box-shadow: 0 6px 18px rgba(126,34,206,0.3);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: all 0.2s;
}
.btn-snap:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(126,34,206,0.4); }
.btn-snap:active:not(:disabled) { transform: scale(0.98); }
.btn-snap:disabled { opacity: 0.85; cursor: wait; transform: none; }

.sub-controls { display: flex; justify-content: center; gap: 10px; width: 100%; }
.btn-secondary {
  padding: 8px 16px; border-radius: 8px; font-size: 12px; font-weight: 700;
  border: 1px solid #e2e8f0; background: #f8fafc; color: #334155;
  cursor: pointer; transition: all 0.15s;
}
.btn-secondary:hover { background: #f3e8ff; color: #7e22ce; border-color: #d8b4fe; }

/* Spinner for thinking state */
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Prediction Panel */
.pred-box { text-align: center; margin: 16px 0; }
.pred-label { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.badge {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 10px 24px; border-radius: 14px; font-size: 22px; font-weight: 900;
  border: 2px solid #fecdd3; background: #fff1f2; color: #f43f5e;
  box-shadow: 0 4px 10px rgba(244,63,94,0.12); transition: all 0.3s;
  min-width: 160px;
}
.badge.thinking {
  background: #f8fafc; border-color: #cbd5e1; color: #64748b;
  box-shadow: none; animation: pulse 1s infinite;
}
.conf { margin-top: 8px; font-size: 38px; font-weight: 900; letter-spacing: -1px; color: #0f172a; }
.conf-sub { font-size: 10px; font-weight: 600; color: #64748b; }
.bars { display: flex; flex-direction: column; gap: 10px; padding-top: 12px; border-top: 1px solid #f1f5f9; }
.bar-header { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #64748b; }
.bar-row { display: flex; flex-direction: column; gap: 3px; }
.bar-meta { display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; }
.track { width: 100%; height: 9px; background: #f1f5f9; border-radius: 9999px; overflow: hidden; }
.fill { height: 100%; border-radius: 9999px; transition: width 0.4s ease; }
.fill-u { background: #10b981; }
.fill-r { background: #f43f5e; }
.fill-o { background: #8b5cf6; }
.advice {
  margin-top: 14px; padding: 10px 12px; border-radius: 10px;
  background: #faf5ff; border: 1px solid #e9d5ff; font-size: 11px; color: #581c87;
  display: flex; flex-direction: column; gap: 2px;
}
.advice-title { font-weight: 800; font-size: 11px; color: #7e22ce; text-transform: uppercase; letter-spacing: 0.5px; }

/* Serial & History */
.serial {
  background: #020617; color: #cbd5e1; font-family: monospace; font-size: 11px;
  padding: 10px 12px; border-radius: 10px; height: 130px; overflow-y: auto;
  border: 1px solid #1e1b4b; display: flex; flex-direction: column; gap: 3px;
}
.line { display: flex; align-items: flex-start; gap: 6px; }
.time { color: #64748b; }
.history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
.h-card { border: 1px solid #e9d5ff; border-radius: 10px; padding: 8px; background: white; font-size: 10px; }
.h-thumb { width: 100%; height: 70px; border-radius: 6px; object-fit: cover; margin-bottom: 5px; }

/* Modal */
.modal {
  position: fixed; inset: 0; z-index: 50; background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 12px;
}
.modal.hidden { display: none; }
.modal-content {
  background: white; border-radius: 14px; border: 1px solid #e9d5ff;
  width: 100%; max-width: 900px; height: 80vh; display: flex; flex-direction: column; overflow: hidden;
}
.modal-top { padding: 10px 14px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-body { flex: 1; background: #f1f5f9; }
.modal-body iframe { width: 100%; height: 100%; border: none; }
"""
