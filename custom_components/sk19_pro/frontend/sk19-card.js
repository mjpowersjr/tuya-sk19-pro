/* SK19 Pro projector: app-style card (Projection / Lighting / Music) + sidebar panel.
 * Entities are discovered from the tuya-local device: find select.<base>_projection_scene,
 * then derive the sibling entities from <base>. Optional card config: { entity_base: "projector_light" }.
 */
const BASE_URL = "/sk19_pro";

const CSS = `
:host { display:block; container-type:inline-size; --wheel:230px; --accent:#7b5cf0; --bg1:#3d4d6d; --bg2:#1b2436; --panel:#2a3550; --muted:#8895b3; }
.wrap { background:linear-gradient(180deg,var(--bg1),var(--bg2)); color:#fff; border-radius:16px; padding:12px; max-width:520px; margin:0 auto; box-sizing:border-box; font-family:var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
.title { text-align:center; font-weight:600; margin:2px 0 10px; }
.tabs { display:flex; background:#27324a; border-radius:12px; padding:4px; gap:4px; }
.tabs button { flex:1; background:none; border:0; color:#fff; padding:10px 0; border-radius:9px; font-size:15px; cursor:pointer; }
.tabs button.on { background:var(--accent); }
.cats { display:flex; justify-content:space-around; margin:12px 0 6px; }
.cat { text-align:center; font-size:13px; cursor:pointer; width:23%; }
.cat .ic { width:56px; height:56px; margin:0 auto 4px; }
.cat img { width:56px; height:56px; display:block; border-radius:12px; }
.grid { background:#ffffff10; border-radius:14px; padding:10px 6px; display:grid; grid-template-columns:repeat(4,1fr); gap:10px 4px; overflow:auto; }
.item { text-align:center; font-size:12px; cursor:pointer; line-height:1.15; }
.item img { width:64px; height:64px; border-radius:50%; object-fit:cover; border:3px solid transparent; box-sizing:border-box; }
.item.on img { border-color:var(--accent); }
.grid.light { grid-template-columns:repeat(4,1fr); background:#0e1624; }
.grid.light img { background:#162235; padding:8px; border-radius:50%; }
.row { background:#ffffff10; border-radius:14px; padding:10px 12px; margin-top:10px; }
.row .hd { display:flex; justify-content:space-between; align-items:center; font-size:17px; margin-bottom:6px; }
.sl { display:flex; align-items:center; gap:10px; }
.sl input[type=range] { flex:1; accent-color:var(--accent); }
.sl span { min-width:42px; text-align:right; }
.sw { width:50px; height:28px; border-radius:14px; background:#657089; position:relative; cursor:pointer; flex:none; }
.sw::after { content:""; position:absolute; top:3px; left:3px; width:22px; height:22px; border-radius:50%; background:#fff; transition:.15s; }
.sw.on { background:var(--accent); } .sw.on::after { left:25px; }
.btns { display:flex; justify-content:space-around; margin-top:10px; }
.btns button { background:#ffffff14; border:0; border-radius:10px; width:64px; height:50px; cursor:pointer; color:#fff; display:flex; align-items:center; justify-content:center; }
.btns img { width:30px; height:30px; }
.bottom { display:flex; justify-content:center; align-items:center; margin-top:10px; padding:2px 0; }
.pwr { width:60px; height:60px; border-radius:50%; background:var(--accent); border:0; color:#fff; cursor:pointer; display:flex; align-items:center; justify-content:center; margin:0 auto; }
.pwr.off { background:#657089; }
.wheel { width:var(--wheel); height:var(--wheel); border-radius:50%; margin:14px auto; position:relative; cursor:pointer;
  background:conic-gradient(from 90deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000);
  -webkit-mask:radial-gradient(circle, transparent 58%, #000 59%); mask:radial-gradient(circle, transparent 58%, #000 59%); }
.wheelbox { position:relative; width:var(--wheel); margin:0 auto; }
.wheelbox .mid { position:absolute; inset:0; margin:auto; width:calc(var(--wheel)*.42); height:calc(var(--wheel)*.42); border-radius:50%; background:#055; display:flex; align-items:center; justify-content:center; color:#fff; }
.dots { display:flex; justify-content:space-around; margin:6px 0 10px; }
.dot { width:38px; height:38px; border-radius:50%; cursor:pointer; border:3px solid #ffffff55; }
.disc { width:170px; height:170px; border-radius:50%; margin:14px auto; background:linear-gradient(160deg,#f0a0ff,#8f6df5); display:flex; align-items:center; justify-content:center; color:#2a3550; }
.badge { text-align:center; margin:12px auto 0; background:var(--accent); border-radius:22px; padding:10px 0; width:60%; font-weight:600; }
.badge.off { background:#657089; }
.err { padding:16px; color:#ffb4ab; }
.body.lighting .b { margin-top:10px; }
/* fill the available height; only the scene list scrolls, controls stay in view */
.wrap { display:flex; flex-direction:column; min-height:0; }
.title, .tabs, .bottom { flex:none; }
.body { flex:1 1 auto; min-height:0; display:flex; flex-direction:column; }
.body > .a { flex:1 1 auto; min-height:0; display:flex; flex-direction:column; }
.body > .b { flex:none; }
.body .a .cats { flex:none; }
.body .a .grid { flex:1 1 0; min-height:140px; overflow:auto; }
.body.lighting > .a { flex:none; }
.body.lighting > .b { flex:1 1 0; min-height:0; overflow:auto; }
.body.music { overflow:auto; }
/* wider card (tablet): bigger touch targets; single column, grows taller in portrait */
@container (min-width: 640px) {
  :host { --wheel:300px; }
  .wrap { max-width:1040px; padding:20px; border-radius:20px; }
  .title { font-size:20px; margin:4px 0 14px; }
  .tabs button { font-size:17px; padding:14px 0; }
  .cats { margin-top:16px; }
  .cat { font-size:15px; }
  .cat .ic, .cat img { width:76px; height:76px; }
  .grid { grid-template-columns:repeat(5,1fr); gap:18px 8px; padding:14px 8px; }
  .item { font-size:14px; }
  .item img { width:92px; height:92px; }
  .grid.light { grid-template-columns:repeat(4,1fr); max-height:none; }
  .row .hd { font-size:20px; }
  .sw { width:58px; height:32px; border-radius:16px; }
  .sw::after { width:26px; height:26px; }
  .sw.on::after { left:29px; }
  .btns button { width:88px; height:64px; }
  .pwr { width:72px; height:72px; }
  .dot { width:46px; height:46px; }
  .disc { width:240px; height:240px; }
  .badge { width:40%; }
}
/* two columns only when the tablet is held landscape */
@media (orientation: landscape) {
  @container (min-width: 640px) {
    .body.projection, .body.lighting { display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:20px; align-items:stretch; grid-template-rows:minmax(0,1fr); }
    .body.lighting .b { margin-top:0; }
    .body.projection .b .row:first-child, .body.lighting .a .row { margin-top:0; }
    .body > .b { align-self:start; max-height:100%; overflow:auto; }
    .body.lighting > .a { overflow:auto; }
    .grid { grid-template-columns:repeat(4,1fr); }
    .grid.light { grid-template-columns:repeat(2,1fr); }
  }
  @container (min-width: 960px) {
    .grid { grid-template-columns:repeat(5,1fr); }
    .body.projection, .body.lighting { grid-template-columns:minmax(0,1.9fr) minmax(0,1fr); }
  }
}
`;

const PATHS = {
  play: "M8 5v14l11-7z",
  pause: "M6 19h4V5H6v14zm8-14v14h4V5h-4z",
  next: "M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z",
  prev: "M6 6h2v12H6zm3.5 6l8.5 6V6z",
  power: "M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42A6.92 6.92 0 0 1 19 12c0 3.87-3.13 7-7 7a6.995 6.995 0 0 1-4.42-12.42L6.17 5.17A8.932 8.932 0 0 0 3 12a9 9 0 0 0 18 0c0-2.74-1.23-5.18-3.17-6.83z",
  bulb: "M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z",
  note: "M12 3v10.55A4 4 0 1 0 14 17V7h4V3h-6z",
  volume: "M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 7.97v8.05c1.48-.73 2.5-2.25 2.5-4.02z",
  sun: "M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zM2 13h2v-2H2v2zm18 0h2v-2h-2v2zM11 2v2h2V2h-2zm0 18v2h2v-2h-2zM5.99 4.58L4.58 5.99l1.41 1.42 1.42-1.41-1.42-1.42zm12.02 12.02l-1.42 1.41 1.42 1.42 1.41-1.42-1.41-1.41zM4.58 18.01l1.41 1.41 1.42-1.41-1.42-1.42-1.41 1.42zM18.01 5.99l1.41-1.41-1.41-1.42-1.42 1.42 1.42 1.41z",
};
const ic = (n, px = 26) => `<svg viewBox="0 0 24 24" width="${px}" height="${px}" fill="currentColor" aria-hidden="true"><path d="${PATHS[n]}"/></svg>`;

const SLUGS = {
  master: "switch|master", colour: "light|colour", projection: "switch|projection",
  bright: "number|projection_brightness", play: "switch|play", sound: "switch|sound",
  volume: "number|volume", bluetooth: "switch|bluetooth", btconn: "binary_sensor|bluetooth_connected",
  order: "select|playback_order", cscene: "select|colour_scene", pscene: "select|projection_scene",
  next: "button|next", prev: "button|previous",
};
const ORDERS = ["Sequence", "Random", "Single cycle"];
const PRESETS = [[210, "#1e7bff"], [0, "#ff0000"], [280, "#a000e0"], [60, "#ffff00"]];

class SK19Card extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._onResize = () => { try { this._fit(); } catch (e) { console.error(e); } };
    this._tab = "projection";
    this._cat = null;
    this._cfg = {};
    this._cat_data = null;
    this._sig = "";
  }
  connectedCallback() {
    window.addEventListener("resize", this._onResize);
    requestAnimationFrame(() => { try { this._fit(); } catch (e) { this._showError(e); } });
  }
  disconnectedCallback() { window.removeEventListener("resize", this._onResize); }
  // nearest ancestor (crossing shadow roots) that is scrollable and currently overflowing
  _overflowingScroller() {
    const up = (n) => n.assignedSlot || n.parentElement || (n.getRootNode() instanceof ShadowRoot ? n.getRootNode().host : null);
    for (let n = up(this); n; n = up(n)) {
      if (n === document.documentElement || n === document.body) break;
      const oy = getComputedStyle(n).overflowY;
      if ((oy === "auto" || oy === "scroll") && n.scrollHeight > n.clientHeight + 1) return n;
    }
    const se = document.scrollingElement;
    return se && se.scrollHeight > se.clientHeight + 1 ? se : null;
  }
  _fit() {
    const w = this.shadowRoot && this.shadowRoot.querySelector(".wrap");
    if (!w) return;
    const top = w.getBoundingClientRect().top;
    let h = Math.max(440, Math.floor(window.innerHeight - top - 12));
    w.style.height = h + "px";
    // self-correct: if something below the card (e.g. a visible Android nav bar) still makes the page
    // scroll, shrink the card by exactly that overflow. No overflow -> no change (phones stay as is).
    for (let i = 0; i < 2; i++) {
      const sc = this._overflowingScroller();
      if (!sc) break;
      const over = sc.scrollHeight - sc.clientHeight;
      if (over <= 0 || h - over < 440) break;
      h -= over;
      w.style.height = h + "px";
    }
  }
  setConfig(c) { this._cfg = c || {}; }
  getCardSize() { return 8; }
  set hass(h) {
    this._hass = h;
    if (!this._cat_data && !this._loading) this._load();
    this._render();
  }
  async _load() {
    this._loading = true;
    try { this._cat_data = await (await fetch(`${BASE_URL}/catalogue.json`, { cache: "no-cache" })).json(); }
    catch (e) { this._error = "Could not load catalogue.json"; }
    this._loading = false; this._render(true);
  }
  _base() {
    if (this._cfg.entity_base) return this._cfg.entity_base;
    const k = Object.keys(this._hass.states).find((e) => e.startsWith("select.") && e.endsWith("_projection_scene"));
    return k ? k.slice("select.".length, -"_projection_scene".length) : null;
  }
  _e(key) {
    const [dom, slug] = SLUGS[key].split("|");
    return `${dom}.${this._base()}_${slug}`;
  }
  _s(key) { return this._hass.states[this._e(key)]; }
  _on(key) { const s = this._s(key); return !!s && s.state === "on"; }
  _call(dom, svc, data) { this._hass.callService(dom, svc, data); }
  _toggle(key) { this._call(this._e(key).split(".")[0], this._on(key) ? "turn_off" : "turn_on", { entity_id: this._e(key) }); }
  _select(key, option) { this._call("select", "select_option", { entity_id: this._e(key), option }); }
  _num(key, value) { this._call("number", "set_value", { entity_id: this._e(key), value }); }

  _render(force) {
    try { this._renderInner(force); } catch (e) { this._showError(e); }
  }
  _showError(e) {
    console.error("[sk19-projector-card]", e);
    const msg = String((e && (e.stack || e.message)) || e).replace(/[<&]/g, (c) => ({ "<": "&lt;", "&": "&amp;" }[c])).slice(0, 600);
    this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="wrap"><div class="err"><b>SK19 card error</b><br>${msg}<br><small>${navigator.userAgent}</small></div></div>`;
  }
  _renderInner(force) {
    if (!this._hass || !this._cat_data) { if (this._error) this.shadowRoot.innerHTML = `<div class="err">${this._error}</div>`; return; }
    const b = this._base();
    if (!b) { this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="wrap err">SK19 entities not found. Add the device in the Tuya Local integration first.</div>`; return; }
    const keys = Object.keys(SLUGS);
    const sig = this._tab + "|" + this._cat + "|" + keys.map((k) => { const s = this._s(k); return s ? s.state + (s.attributes.brightness ?? "") + (s.attributes.hs_color ?? "") : "-"; }).join(",");
    if (!force && sig === this._sig) return;
    if (this._dragging) return;
    this._sig = sig;
    const d = this._cat_data;
    const cur = this._s("pscene")?.state;
    const curP = d.projections.find((p) => p.name === cur);
    if (this._cat === null) this._cat = curP ? curP.category : d.categories[0].name;
    const img = (p) => `${BASE_URL}/${p}`;
    let body = "";
    if (this._tab === "projection") {
      const cats = d.categories.map((c) => `<div class="cat ${c.name === this._cat ? "on" : ""}" data-cat="${c.name}"><div class="ic"><img src="${img(c.name === this._cat ? c.icon_active : c.icon)}"></div>${c.name}</div>`).join("");
      const items = d.projections.filter((p) => p.category === this._cat).map((p) => `<div class="item ${p.name === cur ? "on" : ""}" data-scene="${p.name}"><img src="${img(p.image)}"><div>${p.name}</div></div>`).join("");
      const br = Number(this._s("bright")?.state ?? 0), vol = Number(this._s("volume")?.state ?? 0);
      body = `<div class="body projection"><div class="a"><div class="cats">${cats}</div><div class="grid">${items}</div></div><div class="b">
        <div class="row"><div class="hd">Brightness<div class="sw ${this._on("projection") ? "on" : ""}" data-sw="projection"></div></div>
          <div class="sl"><input type="range" min="0" max="100" value="${br}" data-num="bright"><span>${br}%</span></div></div>
        <div class="row"><div class="hd">Music<div class="sw ${this._on("sound") ? "on" : ""}" data-sw="sound"></div></div>
          <div class="sl"><input type="range" min="0" max="100" value="${vol}" data-num="volume"><span>${vol}%</span></div></div>
        <div class="btns"><button data-order="1" title="Playback order">${this._orderIcon(d)}</button>
          <button data-sw="play">${ic(this._on("play") ? "pause" : "play")}</button><button data-nextscene title="Next projection">${ic("next")}</button></div></div></div>`;
    } else if (this._tab === "lighting") {
      const L = this._s("colour"), h = L?.attributes?.hs_color?.[0] ?? 0;
      const bri = Math.round(((L?.attributes?.brightness ?? 0) / 255) * 100);
      const cs = this._s("cscene")?.state;
      const items = d.lighting.map((l) => `<div class="item ${l.name === cs ? "on" : ""}" data-lscene="${l.name}"><img src="${img(l.image)}"><div>${l.name}</div></div>`).join("");
      body = `<div class="body lighting"><div class="a"><div class="row"><div class="hd">Color<div class="sw ${this._on("colour") ? "on" : ""}" data-sw="colour"></div></div>
        <div class="wheelbox"><div class="wheel" data-wheel></div><div class="mid" style="background:hsl(${h} 100% 30%)">${ic("bulb", 40)}</div></div>
        <div class="dots">${PRESETS.map(([hh, c]) => `<div class="dot" data-hue="${hh}" style="background:${c}"></div>`).join("")}</div>
        <div class="sl">${ic("sun", 22)}<input type="range" min="1" max="100" value="${bri}" data-bri><span>${bri}%</span></div></div>
        </div><div class="b"><div class="grid light">${items}</div></div></div>`;
    } else {
      const vol = Number(this._s("volume")?.state ?? 0), conn = this._s("btconn")?.state === "on";
      body = `<div class="body music"><div class="row"><div class="hd">Bluetooth<div class="sw ${this._on("bluetooth") ? "on" : ""}" data-sw="bluetooth"></div></div></div>
        <div class="badge ${conn ? "" : "off"}">${conn ? "Bluetooth Connected" : "Bluetooth Disconnected"}</div>
        <div class="disc">${ic("note", 80)}</div>
        <div class="row"><div class="btns" style="margin:0"><button data-nav="prev">${ic("prev")}</button><button data-sw="play">${ic(this._on("play") ? "pause" : "play")}</button><button data-nav="next">${ic("next")}</button></div>
          <div class="sl" style="margin-top:10px">${ic("volume", 22)}<input type="range" min="0" max="100" value="${vol}" data-num="volume"><span>${vol}%</span></div></div></div>`;
    }
    const tab = (k, t) => `<button class="${this._tab === k ? "on" : ""}" data-tab="${k}">${t}</button>`;
    this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="wrap"><div class="title">Smart 3D Video Projector Light</div>
      <div class="tabs">${tab("projection", "Projection")}${tab("lighting", "Lighting")}${tab("music", "Music")}</div>${body}
      <div class="bottom"><span></span><button class="pwr ${this._on("master") ? "" : "off"}" data-sw="master">${ic("power", 30)}</button><span></span></div></div>`;
    this._bind();
    this._fit();
  }
  _orderIcon(d) {
    const o = this._s("order")?.state;
    const m = { "Sequence": d.ui.sequentialPlaybackImg, "Random": d.ui.shuffleImg, "Single cycle": d.ui.single_cycle };
    return `<img src="${BASE_URL}/${m[o] || d.ui.sequentialPlaybackImg}">`;
  }
  _bind() {
    const $ = (s) => this.shadowRoot.querySelectorAll(s);
    $("[data-tab]").forEach((el) => (el.onclick = () => { this._tab = el.dataset.tab; this._render(true); }));
    $("[data-cat]").forEach((el) => (el.onclick = () => { this._cat = el.dataset.cat; this._render(true); }));
    $("[data-scene]").forEach((el) => (el.onclick = () => this._select("pscene", el.dataset.scene)));
    $("[data-lscene]").forEach((el) => (el.onclick = () => this._select("cscene", el.dataset.lscene)));
    $("[data-sw]").forEach((el) => (el.onclick = () => this._toggle(el.dataset.sw)));
    $("[data-nav]").forEach((el) => (el.onclick = () => this._call("button", "press", { entity_id: this._e(el.dataset.nav) })));
    $("[data-nextscene]").forEach((el) => (el.onclick = () => {
      const names = this._cat_data.projections.map((p) => p.name);
      const i = names.indexOf(this._s("pscene")?.state);
      this._select("pscene", names[(i + 1) % names.length]);
    }));
    $("[data-order]").forEach((el) => (el.onclick = () => {
      const o = this._s("order")?.state; this._select("order", ORDERS[(ORDERS.indexOf(o) + 1) % ORDERS.length]);
    }));
    $("[data-num]").forEach((el) => {
      el.oninput = () => { this._dragging = true; el.nextElementSibling.textContent = el.value + "%"; };
      el.onchange = () => { this._dragging = false; this._num(el.dataset.num, Number(el.value)); };
    });
    $("[data-bri]").forEach((el) => {
      el.oninput = () => { this._dragging = true; el.nextElementSibling.textContent = el.value + "%"; };
      el.onchange = () => { this._dragging = false; this._call("light", "turn_on", { entity_id: this._e("colour"), brightness_pct: Number(el.value) }); };
    });
    $("[data-hue]").forEach((el) => (el.onclick = () =>
      this._call("light", "turn_on", { entity_id: this._e("colour"), hs_color: [Number(el.dataset.hue), 100] })));
    $("[data-wheel]").forEach((el) => (el.onclick = (ev) => {
      const r = el.getBoundingClientRect();
      const ang = Math.atan2(ev.clientY - (r.top + r.height / 2), ev.clientX - (r.left + r.width / 2));
      // conic gradient starts at 3 o'clock (red) and runs clockwise, same as atan2 on screen coords
      const hue = (Math.round((ang * 180) / Math.PI) + 360) % 360;
      this._call("light", "turn_on", { entity_id: this._e("colour"), hs_color: [hue, 100] });
    }));
  }
}

class SK19Panel extends HTMLElement {
  set hass(h) { this._hass = h; if (this._card) this._card.hass = h; }
  set narrow(_) {}
  set panel(_) {}
  connectedCallback() {
    if (this._card) return;
    this.style.cssText = "display:block;padding:12px;background:var(--primary-background-color);box-sizing:border-box";
    this._card = document.createElement("sk19-projector-card");
    this._card.setConfig({});
    this.appendChild(this._card);
    if (this._hass) this._card.hass = this._hass;
  }
}

if (!customElements.get("sk19-projector-card")) customElements.define("sk19-projector-card", SK19Card);
if (!customElements.get("sk19-panel")) customElements.define("sk19-panel", SK19Panel);
window.customCards = window.customCards || [];
window.customCards.push({ type: "sk19-projector-card", name: "SK19 Pro projector", description: "App-style projector controls" });

/* Field diagnostics: on the dashboard/panel URLs, report what this client sees to the HA log.
 * Everything here is read-only; it only emits one system_log entry per page load. */
(function sk19Diag() {
  const t0 = performance.now(), errors = [];
  window.addEventListener("error", (e) => errors.push(`${e.message || e.type} @${(e.filename || "").replace(location.origin, "")}:${e.lineno || 0}`), true);
  window.addEventListener("unhandledrejection", (e) => errors.push("rejection: " + String((e.reason && (e.reason.message || e.reason.type)) || e.reason)));
  const findAll = (root, sel, out = []) => {
    if (root.querySelectorAll) root.querySelectorAll(sel).forEach((x) => out.push(x));
    const all = root.querySelectorAll ? root.querySelectorAll("*") : [];
    for (const el of all) if (el.shadowRoot) findAll(el.shadowRoot, sel, out);
    return out;
  };
  const report = async (label) => {
    // path is checked now, not at load: a cold start into the default dashboard begins at "/"
    if (!/^\/sk19-(dashboard|projector)/.test(location.pathname)) return;
    const ha = document.querySelector("home-assistant");
    const hass = ha && ha.hass;
    const r = { label, path: location.pathname, ua: navigator.userAgent, loadedAtMs: Math.round(t0), nowMs: Math.round(performance.now()),
      user: hass && hass.user && hass.user.name, admin: hass && hass.user && hass.user.is_admin,
      defined: !!customElements.get("sk19-projector-card"), errors: errors.slice(0, 8) };
    try { r.perf = performance.getEntriesByType("resource").filter((e) => /sk19_pro/.test(e.name)).map((e) => ({ u: e.name.replace(location.origin, ""), ms: Math.round(e.duration), status: e.responseStatus, bytes: e.transferSize })); } catch (e) { r.perfErr = String(e); }
    try { r.cards = findAll(document, "sk19-projector-card").length; r.errorCards = findAll(document, "hui-error-card").map((x) => ((x.shadowRoot && x.shadowRoot.textContent) || x.textContent || "").trim().slice(0, 160)); } catch (e) { r.domErr = String(e); }
    if (hass) {
      try { r.resources = (await hass.callWS({ type: "lovelace/resources" })).map((x) => x.url).filter((u) => /sk19|button-card/.test(u)); } catch (e) { r.resErr = String((e && (e.message || e.code)) || JSON.stringify(e)); }
      try { r.cfg = JSON.stringify(await hass.callWS({ type: "lovelace/config", url_path: "sk19-dashboard", force: false })).slice(0, 260); } catch (e) { r.cfgErr = String((e && (e.message || e.code)) || JSON.stringify(e)); }
      try { await hass.callService("system_log", "write", { message: "SK19 DIAG " + JSON.stringify(r), level: "warning", logger: "sk19_pro.frontend" }); } catch (e) { /* nothing else we can do */ }
    }
  };
  setTimeout(() => report("t+5s"), 5000);
  setTimeout(() => report("t+15s"), 15000);
})();
