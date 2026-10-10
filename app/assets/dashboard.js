"use strict";

const el = (id) => document.getElementById(id);
const fmt = (n, decimals = 2) => Number.isFinite(n)
  ? n.toLocaleString("it-IT", {minimumFractionDigits: decimals, maximumFractionDigits: decimals}) : "—";
const colors = ["#078d88", "#e18b26", "#6577d3"];
let waveform = null, selectedName = "", events = [], lastEventsAt = 0;
let selectionVersion = 0;
let selectedPowerName = "", powerSessions = [], powerHistory = [];
let powerVersion = 0, lastPowerListAt = 0, lastPowerReadAt = 0;
let currentPowerName = "", loggerError = "", powerAPIError = "";
let economicSettingsLoaded = false;
let demoActionPending = false, demoActionError = "", lastEconomics = null;
let inspectionSettingsLoaded = false, inspectionPending = false, inspectionError = "";

async function getJSON(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 6000);
  try {
    const response = await fetch(path, {...options, cache: "no-store", signal: controller.signal});
    if (!response.ok) {
      const message = await response.json().catch(() => ({}));
      throw new Error(typeof message.detail === "string" ? message.detail : `HTTP ${response.status}`);
    }
    return await response.json();
  } finally { clearTimeout(timeout); }
}

function showStatus(data) {
  const phases = {
    STARTING: ["AVVIO", "In attesa del firmware.", "busy"],
    READY: ["READY", "Pronto: puoi far cadere la pallina.", "ready"],
    WAIT: ["ATTESA", "Attendi il pretrigger completo e il ritorno del piezo sotto soglia.", "busy"],
    TRANSFER: ["SALVATAGGIO", "Trasferimento della forma d’onda e salvataggio del CSV.", "busy"],
    PAUSED: ["TELEMETRIA SOSPESA", "Possibile cattura in corso; attendi il prossimo READY.", "busy"],
    NO_TELEMETRY: ["DATI NON AGGIORNATI", "Controlla il firmware e i log di App Lab.", "bad"],
    SENSOR_ERROR: ["SENSOR ERROR", "Controlla il messaggio di errore e i log.", "bad"]
  };
  const [title, description, cls] = phases[data.phase] || phases.STARTING;
  el("phase").textContent = title;
  el("phase").className = `badge ${cls}`;
  el("status-detail").textContent = description;
  el("error").hidden = !data.error;
  el("error").textContent = data.error || "";
  el("telemetry-age").textContent = data.telemetry_age_s == null ? "Nessuna lettura"
    : `Ultima anteprima ${fmt(data.telemetry_age_s, 1)} s fa`;
  const live = data.live;
  const fresh = live && data.telemetry_age_s < 1.8 && data.phase !== "TRANSFER";
  for (const [id, key] of [["ax", "ax"], ["ay", "ay"], ["az", "az"]]) {
    el(id).textContent = fresh && live.imu_ok ? fmt(live[key], 4) : "—";
  }
  el("impacts").textContent = live ? fmt(live.events, 0) : "—";
  el("piezo").textContent = fresh ? `${fmt(live.adc, 0)} / ${fmt(live.peak, 0)}` : "—";
  el("piezo-active").textContent = fresh ? (live.active ? "SÌ · attesa rilascio" : "No") : "—";
  el("crossings").textContent = live ? `${fmt(live.raw, 0)} / ${fmt(live.suppressed, 0)}` : "—";
  // Sottrazione modulo 2^32 per il rollover di millis() nel firmware.
  const powerAge = live ? ((live.t_ms - live.power_t_ms + 4294967296) % 4294967296) / 1000
    + data.telemetry_age_s : Infinity;
  const powerFresh = live && live.power_ok && powerAge < 3 && fresh;
  el("voltage").textContent = powerFresh ? fmt(live.v_in, 3) : "—";
  el("current").textContent = powerFresh ? fmt(live.current_ma, 2) : "—";
  el("power").textContent = powerFresh ? fmt(live.power_w * 1000, 3) : "—";
  const powerErrors = {2: "Errore I²C", 3: "Errore configurazione", 4: "Timeout", 5: "Fuori range"};
  el("ina-state").textContent = !live ? "In attesa" : powerErrors[live.power_error]
    || (powerFresh ? "Lettura disponibile" : "In attesa di una nuova lettura");
  el("power-detail").textContent = powerFresh ? "V_IN × I · INA219 R100" : "Misura non disponibile / sospesa";
  const history = data.power_history;
  if (history) {
    currentPowerName = history.name;
    el("power-log-status").textContent = `Sessione corrente: ${fmt(history.written, 0)} letture salvate · ${fmt(history.queued, 0)} in coda`;
    loggerError = history.error ? `Salvataggio storico sospeso: ${history.error}. Controlla spazio/permessi e riavvia la App.`
      : history.dropped ? `${fmt(history.dropped, 0)} letture non registrate: coda piena.` : "";
    showPowerError();
  }
  if (data.economics) showEconomics(data.economics);
  el("ai-chip").textContent = data.ai_enabled ? "Inferenza AI attiva" : "AI non attiva";
  if (data.inspection) showInspection(data.inspection, live, fresh);
}

function showInspection(data, live, fresh) {
  const settings = data.settings;
  if (!inspectionSettingsLoaded) {
    el("inspection-impacts").value = settings.min_impacts;
    el("inspection-drop").value = settings.drop_pct;
    el("inspection-samples").value = settings.consecutive_samples;
    inspectionSettingsLoaded = true;
  }
  el("inspection-panel").classList.toggle("alerting", data.active);
  el("inspection-title").textContent = data.active ? "Ispezione consigliata" : "Segnalazione di ispezione";
  const alert = data.alert, evidence = alert?.evidence;
  el("inspection-reason").textContent = alert?.reason === "ELECTRICAL_DECLINE"
    ? `Calo di potenza rilevato: ${fmt(evidence.drop_pct, 1)}% dopo ${evidence.impacts_since_reference} impatti, per ${evidence.consecutive_samples} letture consecutive. Possibile alterazione: verificare luce, carico e pannello.`
    : alert?.reason === "AI_ANOMALY"
      ? `Anomalia vibrazionale: score ${fmt(evidence.score, 4)} oltre la soglia ${fmt(evidence.threshold, 4)}. Ispezione consigliata.`
      : data.reference_available ? "Monitoraggio attivo rispetto al riferimento elettrico."
        : "Acquisisci un nuovo riferimento elettrico con il pannello illuminato, prima degli impatti.";
  el("inspection-progress").textContent = `Impatti dal riferimento: ${fmt(data.impacts_since_reference, 0)} / ${settings.min_impacts} · Letture consecutive con calo ≥ ${fmt(settings.drop_pct, 1)}%: ${data.consecutive_low_samples} / ${settings.consecutive_samples}`;
  const hardware = fresh && [0, 1].includes(live?.led_on);
  el("inspection-led").textContent = !hardware
    ? (fresh && live ? "Aggiorna il firmware LED" : "LED: stato non aggiornato")
    : Boolean(live.led_on) !== data.active ? "LED: aggiornamento in corso"
      : live.led_on ? "LED ROSSO ACCESO" : "LED spento";
  el("inspection-led").className = `badge ${hardware && live.led_on ? "bad" : "busy"}`;
  el("inspection-reset").disabled = inspectionPending || !data.active;
  el("inspection-save").disabled = inspectionPending;
  const message = [inspectionError, data.io_error].filter(Boolean).join(" ");
  el("inspection-error").hidden = !message;
  el("inspection-error").textContent = message;
}

async function inspectionAction(endpoint, body = {}) {
  if (inspectionPending) return;
  inspectionPending = true; inspectionError = "";
  el("inspection-save").disabled = true; el("inspection-reset").disabled = true;
  try {
    await getJSON(`/api/inspection/${endpoint}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
    });
  } catch (error) {
    inspectionError = `${error.message}. Controlla lo stato aggiornato prima di ripetere.`;
  } finally { inspectionPending = false; }
}

const economicFields = {
  daily_kwh: "scenario-daily", days: "scenario-days", self_consumption_pct: "scenario-self",
  buy_eur_kwh: "scenario-buy", sell_eur_kwh: "scenario-sell",
  reduction_mode: "scenario-mode", assumed_reduction_pct: "scenario-reduction"
};

function money(value) {
  if (!Number.isFinite(value)) return "—";
  return value > 0 && value < 0.000001 ? value.toExponential(2) : fmt(value, value < .01 ? 6 : 2);
}

function showEconomics(data) {
  lastEconomics = data;
  if (!economicSettingsLoaded) {
    for (const [key, id] of Object.entries(economicFields)) el(id).value = data.settings[key];
    economicSettingsLoaded = true;
    el("scenario-reduction").disabled = data.settings.reduction_mode !== "manual";
  }
  const trial = data.comparison, running = Boolean(trial?.running);
  el("reference-button").disabled = demoActionPending || data.phase === "COLLECTING" || running;
  el("comparison-start").disabled = demoActionPending || running || data.phase !== "REFERENCE_READY" || data.health !== "OK";
  el("comparison-stop").disabled = demoActionPending || !running;
  el("economic-save").disabled = demoActionPending;
  el("comparison-report").hidden = !data.report_available;
  const progress = data.phase === "COLLECTING" ? ` (${data.reference_progress}/${data.reference_target})` : "";
  el("demo-status").textContent = data.message + progress;
  el("reference-power").textContent = fmt(data.reference_w == null ? null : data.reference_w * 1000, 3);
  el("comparison-power").textContent = fmt(data.current_w == null ? null : data.current_w * 1000, 3);
  el("live-reduction").textContent = fmt(data.live_reduction_pct, 1);
  el("period-reduction").textContent = fmt(trial?.period_reduction_pct, 1);
  const covered = trial && trial.covered_s > 0;
  el("measured-energy").textContent = covered ? `${fmt(trial.measured_wh, 6)} Wh` : "—";
  el("reference-energy").textContent = covered ? `${fmt(trial.reference_wh, 6)} Wh` : "—";
  el("deficit-energy").textContent = covered ? `${fmt(trial.net_deficit_wh, 6)} Wh` : "—";
  el("deficit-value").textContent = covered ? `${money(trial.deficit_value_eur)} €` : "—";
  el("comparison-coverage").textContent = trial
    ? `${fmt(trial.covered_s, 1)} / ${fmt(trial.wall_duration_s, 1)} s · ${trial.excluded_intervals} intervalli esclusi` : "—";
  const healthNote = data.health === "REVERSE_POWER" ? "Flusso inverso: potenza esclusa dalla stima di produzione."
    : data.health === "NO_RECENT_POWER" && data.reference_w != null ? "Misura elettrica sospesa o non recente; attendi la ripresa della telemetria." : "";
  const messages = [demoActionError, data.settings_error, data.io_error,
    data.phase === "REFERENCE_ERROR" ? data.message : "", healthNote].filter(Boolean);
  el("demo-error").hidden = !messages.length;
  el("demo-error").textContent = messages.join(" ");
  const scenario = data.scenario;
  el("scenario-effective").textContent = fmt(scenario?.reduction_pct, 1);
  el("scenario-kwh").textContent = fmt(scenario?.lost_kwh, 2);
  el("scenario-self-cost").textContent = scenario ? money(scenario.self_consumption_cost_eur) : "—";
  el("scenario-total").textContent = scenario ? money(scenario.total_eur) : "—";
  el("scenario-description").textContent = scenario
    ? `Scenario ipotetico su ${data.settings.days} giorni: riduzione ${fmt(scenario.reduction_pct, 1)}% ${data.settings.reduction_mode === "manual" ? "inserita manualmente" : "derivata dal confronto energetico"}. Mancato ricavo da vendita: ${money(scenario.export_revenue_lost_eur)} €. Nessuna previsione verificata su un impianto domestico.`
    : "Avvia un confronto e raccogli almeno due misure, oppure imposta una percentuale manuale.";
}

async function economicAction(endpoint, body = {}) {
  if (demoActionPending) return;
  demoActionPending = true; demoActionError = "";
  if (lastEconomics) showEconomics(lastEconomics);
  try {
    const result = await getJSON(`/api/economics/${endpoint}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
    });
    showEconomics(result);
    return true;
  } catch (error) {
    // Un timeout della risposta non dimostra che il comando non sia stato eseguito.
    demoActionError = `${error.message}. Controlla lo stato aggiornato prima di ripetere.`;
    return false;
  } finally {
    demoActionPending = false;
    if (lastEconomics) showEconomics(lastEconomics);
  }
}

function chartBase(id, emptyText) {
  const canvas = el(id), rect = canvas.getBoundingClientRect(), ratio = window.devicePixelRatio || 1;
  canvas.width = Math.round(rect.width * ratio);
  canvas.height = Math.round(rect.height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  const w = rect.width, h = rect.height;
  ctx.font = "11px system-ui";
  ctx.fillStyle = "#657a82";
  if (emptyText) { ctx.textAlign = "center"; ctx.fillText(emptyText, w / 2, h / 2); }
  return {ctx, w, h, left: 52, right: w - 13, top: 17, bottom: h - 30};
}

function grid(chart, xmin, xmax, ymin, ymax, xLabel, yLabel) {
  const {ctx, left, right, top, bottom} = chart;
  const px = (v) => left + (v - xmin) / (xmax - xmin) * (right - left);
  const py = (v) => bottom - (v - ymin) / (ymax - ymin) * (bottom - top);
  ctx.strokeStyle = "#e7eeed"; ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = top + i / 4 * (bottom - top);
    ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(right, y); ctx.stroke();
    ctx.fillStyle = "#657a82"; ctx.textAlign = "right";
    ctx.fillText(yLabel(ymax - i / 4 * (ymax - ymin)), left - 7, y + 4);
    const x = left + i / 4 * (right - left);
    ctx.textAlign = "center";
    ctx.fillText(xLabel(xmin + i / 4 * (xmax - xmin)), x, bottom + 19);
  }
  return {px, py};
}

function drawPower() {
  if (powerHistory.length < 2) { chartBase("power-chart", "In attesa di almeno due letture elettriche"); return; }
  const c = chartBase("power-chart");
  const axis = Number(el("power-quantity").value);
  const values = powerHistory.map((p) => p[axis]);
  let ymin = Math.min(0, ...values), ymax = Math.max(0, ...values);
  const margin = Math.max((ymax - ymin) * .1, .02);
  ymin -= margin; ymax += margin;
  const end = powerHistory[powerHistory.length - 1][0];
  const {px, py} = grid(c, powerHistory[0][0], Math.max(end, powerHistory[0][0] + 1), ymin, ymax,
    (t) => `${Math.round(t)} s`, (v) => fmt(v, axis === 1 ? 3 : 2));
  c.ctx.strokeStyle = colors[0]; c.ctx.lineWidth = 2; c.ctx.beginPath();
  powerHistory.forEach((p, i) => {
    if (!i || p[0] - powerHistory[i - 1][0] > 2.5) c.ctx.moveTo(px(p[0]), py(p[axis]));
    else c.ctx.lineTo(px(p[0]), py(p[axis]));
  });
  c.ctx.stroke();
}

function showPowerError() {
  const message = [loggerError, powerAPIError].filter(Boolean).join(" ");
  el("power-history-error").hidden = !message;
  el("power-history-error").textContent = message;
}

async function loadPowerSession(name) {
  const version = ++powerVersion;
  if (name !== selectedPowerName) {
    powerHistory = [];
    drawPower();
    el("power-download").hidden = true;
  }
  selectedPowerName = name;
  el("power-session").value = name;
  try {
    const result = await getJSON(`/api/power/${encodeURIComponent(name)}?limit=600`);
    if (version !== powerVersion) return;
    powerHistory = result.samples;
    powerAPIError = ""; showPowerError();
    el("power-download").href = `/api/power/${encodeURIComponent(name)}/download`;
    el("power-download").hidden = false;
    const first = powerHistory[0], last = powerHistory[powerHistory.length - 1];
    const span = first && last ? ` · ${new Date(first[4]).toLocaleString("it-IT")} → ${new Date(last[4]).toLocaleString("it-IT")}` : "";
    el("power-history-info").textContent = `Ultime ${powerHistory.length} letture salvate${span}. Il download include l’intera sessione.`;
    lastPowerReadAt = Date.now();
    drawPower();
  } catch (error) {
    if (version === powerVersion) {
      powerAPIError = `Storico non leggibile (${error.message}).`;
      showPowerError();
    }
  }
}

async function refreshPowerSessions() {
  const result = await getJSON("/api/power");
  powerSessions = result.sessions;
  const select = el("power-session"); select.replaceChildren();
  if (!powerSessions.length) select.add(new Option("In attesa della prima misura", ""));
  for (const session of powerSessions) {
    select.add(new Option(`${session.name}${session.active ? " · corrente" : ""}`, session.name));
  }
  select.value = selectedPowerName;
  let target = selectedPowerName;
  if (el("power-follow").checked) {
    // Prima misura non ancora scritta: conserva l'ultima sessione disponibile.
    target = powerSessions.find((session) => session.name === currentPowerName)?.name
      || (powerSessions.some((session) => session.name === target) ? target : powerSessions[0]?.name);
  } else if (!target) target = powerSessions[0]?.name;
  if (target && target !== selectedPowerName) await loadPowerSession(target);
  lastPowerListAt = Date.now();
}

async function refreshPowerHistory() {
  try {
    if (Date.now() - lastPowerListAt > 10000 || !powerSessions.length
        || (currentPowerName && !powerSessions.some((session) => session.name === currentPowerName))) {
      await refreshPowerSessions();
    }
    if (selectedPowerName && Date.now() - lastPowerReadAt > 3000) await loadPowerSession(selectedPowerName);
  } catch (error) {
    powerAPIError = `Archivio elettrico non disponibile (${error.message}).`;
    showPowerError();
  }
}

function drawWaveform() {
  if (!waveform || !waveform.samples.length) { chartBase("wave-chart", "Nessuna forma d’onda selezionata"); return; }
  const samples = waveform.samples;
  const before = samples.filter((p) => p[0] < 0);
  const offsets = [1, 2, 3].map((axis) => el("remove-offset").checked && before.length
    ? before.reduce((sum, p) => sum + p[axis], 0) / before.length : 0);
  const values = samples.flatMap((p) => [1, 2, 3].map((axis) => p[axis] - offsets[axis - 1]));
  let ymin = Math.min(...values), ymax = Math.max(...values);
  const margin = Math.max((ymax - ymin) * .08, .001);
  ymin -= margin; ymax += margin;
  const c = chartBase("wave-chart");
  const xmin = Math.min(0, samples[0][0]), xmax = Math.max(1, samples[samples.length - 1][0]);
  const {px, py} = grid(c, xmin, xmax, ymin, ymax, (v) => fmt(v, 0), (v) => fmt(v, 3));
  c.ctx.strokeStyle = "#9aaeb2"; c.ctx.setLineDash([4, 4]);
  c.ctx.beginPath(); c.ctx.moveTo(px(0), c.top); c.ctx.lineTo(px(0), c.bottom); c.ctx.stroke();
  c.ctx.setLineDash([]); c.ctx.fillStyle = "#657a82"; c.ctx.textAlign = "left";
  c.ctx.fillText("trigger", px(0) + 4, c.top + 10);
  [1, 2, 3].forEach((axis) => {
    c.ctx.strokeStyle = colors[axis - 1]; c.ctx.lineWidth = 1.4; c.ctx.beginPath();
    samples.forEach((p, i) => {
      const x = px(p[0]), y = py(p[axis] - offsets[axis - 1]);
      // Non tracciare un segmento attraverso un buco del campionamento.
      if (!i || p[0] - samples[i - 1][0] > 30) c.ctx.moveTo(x, y);
      else c.ctx.lineTo(x, y);
    });
    c.ctx.stroke();
  });
}

function downloadURL(name, extension) { return `/api/download/${encodeURIComponent(name)}/${extension}`; }

async function selectEvent(name) {
  const version = ++selectionVersion;
  selectedName = name;
  el("event-select").value = name;
  waveform = null; drawWaveform();
  el("csv-download").hidden = true; el("json-download").hidden = true;
  el("event-reasons").hidden = true;
  el("event-info").textContent = "Caricamento della forma d’onda…";
  try {
    const result = await getJSON(`/api/events/${encodeURIComponent(name)}`);
    if (version !== selectionVersion) return;
    waveform = result;
    const meta = result.metadata, complete = meta.capture_complete === true;
    el("event-info").textContent = `${name} · ${result.samples.length} campioni · ${fmt(meta.mean_sample_rate_hz, 1)} Hz · ${complete ? "Cattura completa" : "Cattura da escludere dal dataset"}`;
    const reasons = meta.unusable_reasons || [];
    el("event-reasons").hidden = complete;
    el("event-reasons").textContent = reasons.join("; ") || "Acquisizione marcata non valida.";
    for (const extension of ["csv", "json"]) {
      const link = el(`${extension}-download`);
      link.href = downloadURL(name, extension); link.hidden = false;
    }
    drawWaveform();
  } catch (error) {
    if (version === selectionVersion) {
      selectedName = ""; // Ritenta al prossimo aggiornamento se si segue l'ultimo evento.
      el("event-info").textContent = `Evento non leggibile (${error.message}).`;
    }
  }
}

async function refreshEvents() {
  const result = await getJSON("/api/events");
  events = result.events;
  const select = el("event-select"); select.replaceChildren();
  if (!events.length) select.add(new Option("Nessun evento salvato", ""));
  for (const event of events) select.add(new Option(event.name, event.name));
  select.value = selectedName;
  el("event-count").textContent = `${result.total} eventi · visualizzati ${events.length}`;
  const body = el("events-body"); body.replaceChildren();
  for (const event of events) {
    const row = document.createElement("tr");
    const nameCell = document.createElement("td"), button = document.createElement("button");
    button.className = "event-link"; button.textContent = event.name;
    button.onclick = () => { el("follow").checked = false; selectEvent(event.name); };
    nameCell.append(button); row.append(nameCell);
    for (const value of [event.complete ? "Completa" : "Da escludere", fmt(event.samples, 0), `${fmt(event.rate_hz, 1)} Hz`]) {
      const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
    }
    const fileCell = document.createElement("td");
    for (const extension of ["csv", "json"]) {
      const link = document.createElement("a"); link.className = "file-link";
      link.textContent = extension.toUpperCase(); link.href = downloadURL(event.name, extension);
      fileCell.append(link);
    }
    row.append(fileCell); body.append(row);
  }
  if (!events.length) {
    const row = document.createElement("tr"), cell = document.createElement("td");
    cell.colSpan = 5; cell.className = "muted"; cell.textContent = "Nessun evento salvato.";
    row.append(cell); body.append(row);
  }
  if (events.length && ((!selectedName) || el("follow").checked) && selectedName !== events[0].name) {
    await selectEvent(events[0].name);
  }
  lastEventsAt = Date.now();
}

async function poll() {
  try {
    const data = await getJSON("/api/status");
    el("connection").textContent = "UNO Q connessa";
    el("connection-dot").className = "dot online";
    showStatus(data);
    if (Date.now() - lastEventsAt > 5000 || (data.last_event && data.last_event !== events[0]?.name)) {
      try { await refreshEvents(); }
      catch (error) { el("event-count").textContent = `Archivio non disponibile (${error.message})`; }
    }
  } catch (error) {
    el("connection").textContent = "UNO Q non raggiungibile";
    el("connection-dot").className = "dot offline";
    el("phase").textContent = "OFFLINE"; el("phase").className = "badge bad";
    el("status-detail").textContent = "Controlla la rete e che la App sia in esecuzione.";
    el("telemetry-age").textContent = "Dati live non disponibili";
    for (const id of ["voltage", "current", "power", "ax", "ay", "az", "piezo", "piezo-active"]) el(id).textContent = "—";
    el("ina-state").textContent = "Non raggiungibile";
    el("power-detail").textContent = "Misura non disponibile";
    for (const id of ["reference-button", "comparison-start", "comparison-stop", "economic-save", "inspection-save", "inspection-reset"]) el(id).disabled = true;
    el("inspection-led").textContent = "LED: stato non aggiornato";
    el("comparison-power").textContent = "—";
    el("live-reduction").textContent = "—";
    el("demo-status").textContent = "UNO Q non raggiungibile: gli altri valori sono gli ultimi ricevuti. Il confronto continua se la App resta attiva.";
  } finally { setTimeout(poll, 1000); }
}

el("event-select").onchange = (event) => {
  el("follow").checked = false;
  if (event.target.value) selectEvent(event.target.value);
};
el("follow").onchange = () => { if (el("follow").checked && events.length) selectEvent(events[0].name); };
el("remove-offset").onchange = drawWaveform;
el("inspection-reset").onclick = () => inspectionAction("reset");
el("inspection-form").onsubmit = (event) => {
  event.preventDefault();
  inspectionAction("settings", {
    min_impacts: Number(el("inspection-impacts").value),
    drop_pct: Number(el("inspection-drop").value),
    consecutive_samples: Number(el("inspection-samples").value)
  });
};
el("reference-button").onclick = () => economicAction("reference");
el("comparison-start").onclick = () => economicAction("start");
el("comparison-stop").onclick = () => economicAction("stop");
el("scenario-mode").onchange = () => {
  el("scenario-reduction").disabled = el("scenario-mode").value !== "manual";
};
el("economic-form").addEventListener("input", () => {
  el("economic-save-status").textContent = "Modifiche non salvate: i risultati usano ancora i parametri precedenti.";
});
el("economic-form").onsubmit = async (event) => {
  event.preventDefault();
  if (demoActionPending) return;
  const settings = {};
  for (const [key, id] of Object.entries(economicFields)) {
    settings[key] = key === "reduction_mode" ? el(id).value : Number(el(id).value);
  }
  if (await economicAction("settings", settings)) {
    el("economic-save-status").textContent = "Parametri salvati sulla UNO Q.";
  }
};
el("power-session").onchange = (event) => {
  el("power-follow").checked = false;
  if (event.target.value) loadPowerSession(event.target.value);
};
el("power-follow").onchange = () => { if (el("power-follow").checked) { lastPowerListAt = 0; refreshPowerHistory(); } };
el("power-quantity").onchange = () => {
  const unit = {1: "V", 2: "mA", 3: "mW"}[el("power-quantity").value];
  el("power-chart").setAttribute("aria-label", `Storico elettrico in ${unit}`);
  drawPower();
};
async function pollPowerHistory() {
  // Lo storico su disco non ritarda l'aggiornamento delle carte live.
  try { await refreshPowerHistory(); }
  finally { setTimeout(pollPowerHistory, 3000); }
}
window.addEventListener("resize", () => { drawWaveform(); drawPower(); });
drawWaveform(); drawPower(); poll(); pollPowerHistory();
