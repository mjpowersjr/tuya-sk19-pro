/* SK19 Pro projector: app-style card (Projection / Lighting / Music) + sidebar panel.
 * Entities are discovered from the tuya-local device: find select.<base>_projection_scene,
 * then derive the sibling entities from <base>. Optional card config: { entity_base: "projector_light" }.
 */
const BASE_URL = "/sk19_pro";

const CSS = `
:host { display:block; --accent:#7b5cf0; --bg1:#3d4d6d; --bg2:#1b2436; --panel:#2a3550; --muted:#8895b3; }
.wrap { background:linear-gradient(180deg,var(--bg1),var(--bg2)); color:#fff; border-radius:16px; padding:12px; max-width:520px; margin:0 auto; box-sizing:border-box; font-family:var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
.title { text-align:center; font-weight:600; margin:2px 0 10px; }
.tabs { display:flex; background:#27324a; border-radius:12px; padding:4px; gap:4px; }
.tabs button { flex:1; background:none; border:0; color:#fff; padding:10px 0; border-radius:9px; font-size:15px; cursor:pointer; }
.tabs button.on { background:var(--accent); }
.cats { display:flex; justify-content:space-around; margin:12px 0 6px; }
.cat { text-align:center; font-size:13px; cursor:pointer; width:23%; }
.cat .ic { width:56px; height:56px; margin:0 auto 4px; border-radius:12px; background:#ffffff14; display:flex; align-items:center; justify-content:center; }
.cat.on .ic { background:var(--accent); }
.cat img { width:36px; height:36px; }
.grid { background:#ffffff10; border-radius:14px; padding:10px 6px; display:grid; grid-template-columns:repeat(4,1fr); gap:10px 4px; max-height:300px; overflow:auto; }
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
.btns button { background:#ffffff14; border:0; border-radius:10px; width:64px; height:54px; cursor:pointer; color:#fff; font-size:22px; }
.btns img { width:30px; height:30px; }
.bottom { display:flex; justify-content:space-between; align-items:center; margin-top:14px; padding:6px 18px 2px; }
.pwr { width:64px; height:64px; border-radius:50%; background:var(--accent); border:0; color:#fff; font-size:28px; cursor:pointer; }
.pwr.off { background:#657089; }
.wheel { width:230px; height:230px; border-radius:50%; margin:14px auto; position:relative; cursor:pointer;
  background:conic-gradient(from 90deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000);
  -webkit-mask:radial-gradient(circle, transparent 58%, #000 59%); mask:radial-gradient(circle, transparent 58%, #000 59%); }
.wheelbox { position:relative; width:230px; margin:0 auto; }
.wheelbox .mid { position:absolute; inset:0; margin:auto; width:96px; height:96px; border-radius:50%; background:#055; display:flex; align-items:center; justify-content:center; font-size:38px; }
.dots { display:flex; justify-content:space-around; margin:6px 0 10px; }
.dot { width:38px; height:38px; border-radius:50%; cursor:pointer; border:3px solid #ffffff55; }
.disc { width:180px; height:180px; border-radius:50%; margin:18px auto; background:linear-gradient(160deg,#f0a0ff,#8f6df5); display:flex; align-items:center; justify-content:center; font-size:64px; }
.badge { text-align:center; margin:12px auto 0; background:var(--accent); border-radius:22px; padding:10px 0; width:60%; font-weight:600; }
.badge.off { background:#657089; }
.err { padding:16px; color:#ffb4ab; }
`;

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
    this._tab = "projection";
    this._cat = null;
    this._cfg = {};
    this._cat_data = null;
    this._sig = "";
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
    try { this._cat_data = await (await fetch(`${BASE_URL}/catalogue.json`)).json(); }
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
      body = `<div class="cats">${cats}</div><div class="grid">${items}</div>
        <div class="row"><div class="hd">Brightness<div class="sw ${this._on("projection") ? "on" : ""}" data-sw="projection"></div></div>
          <div class="sl"><input type="range" min="0" max="100" value="${br}" data-num="bright"><span>${br}%</span></div></div>
        <div class="row"><div class="hd">Music<div class="sw ${this._on("sound") ? "on" : ""}" data-sw="sound"></div></div>
          <div class="sl"><input type="range" min="0" max="100" value="${vol}" data-num="volume"><span>${vol}%</span></div></div>
        <div class="btns"><button data-order="1" title="Playback order">${this._orderIcon(d)}</button>
          <button data-sw="play">${this._on("play") ? `<img src="${img(d.ui.pause)}">` : "▶"}</button><button data-nav="next">⏭</button></div>`;
    } else if (this._tab === "lighting") {
      const L = this._s("colour"), h = L?.attributes?.hs_color?.[0] ?? 0;
      const bri = Math.round(((L?.attributes?.brightness ?? 0) / 255) * 100);
      const cs = this._s("cscene")?.state;
      const items = d.lighting.map((l) => `<div class="item ${l.name === cs ? "on" : ""}" data-lscene="${l.name}"><img src="${img(l.image)}"><div>${l.name}</div></div>`).join("");
      body = `<div class="row"><div class="hd">Color<div class="sw ${this._on("colour") ? "on" : ""}" data-sw="colour"></div></div>
        <div class="wheelbox"><div class="wheel" data-wheel></div><div class="mid" style="background:hsl(${h} 100% 30%)">💡</div></div>
        <div class="dots">${PRESETS.map(([hh, c]) => `<div class="dot" data-hue="${hh}" style="background:${c}"></div>`).join("")}</div>
        <div class="sl">☀<input type="range" min="1" max="100" value="${bri}" data-bri><span>${bri}%</span></div></div>
        <div class="grid light" style="margin-top:10px">${items}</div>`;
    } else {
      const vol = Number(this._s("volume")?.state ?? 0), conn = this._s("btconn")?.state === "on";
      body = `<div class="row"><div class="hd">Bluetooth<div class="sw ${this._on("bluetooth") ? "on" : ""}" data-sw="bluetooth"></div></div></div>
        <div class="badge ${conn ? "" : "off"}">${conn ? "Bluetooth Connected" : "Bluetooth Disconnected"}</div>
        <div class="disc">♪</div>
        <div class="row"><div class="btns" style="margin:0"><button data-nav="prev">⏮</button><button data-sw="play">⏯</button><button data-nav="next">⏭</button></div>
          <div class="sl" style="margin-top:10px">🔊<input type="range" min="0" max="100" value="${vol}" data-num="volume"><span>${vol}%</span></div></div>`;
    }
    const tab = (k, t) => `<button class="${this._tab === k ? "on" : ""}" data-tab="${k}">${t}</button>`;
    this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="wrap"><div class="title">Smart 3D Video Projector Light</div>
      <div class="tabs">${tab("projection", "Projection")}${tab("lighting", "Lighting")}${tab("music", "Music")}</div>${body}
      <div class="bottom"><span></span><button class="pwr ${this._on("master") ? "" : "off"}" data-sw="master">⏻</button><span></span></div></div>`;
    this._bind();
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
    this.style.cssText = "display:block;padding:16px;background:var(--primary-background-color);min-height:100vh;box-sizing:border-box";
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
