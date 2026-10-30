const assetVersion = new URL(import.meta.url).search;
const {
  MAIN_PRAYER_KEYS,
  MIMBAR_COURTYARD_BACKGROUND_URL,
  assertMimbarConfig,
  backgroundVeilOpacity,
  buildLowerRail,
  buildPrayerView,
  formatCountdown,
  formatPrayerTime,
  resolveMimbarBackground,
  resolveMimbarTheme,
  resolveMimbarTimeFormat,
  resolveIntegrationBackgroundImages,
  resolveLifecycle,
  SCHEDULE_PRAYER_ICONS,
  splitDayPeriod,
} = await import(`./mimbar-model.mjs${assetVersion}`);
await import(`./mimbar-editor.js${assetVersion}`);

const CARD_TYPE = "solat-my-mimbar-card";
const PRAYER_LABELS = {
  imsak: "Imsak",
  subuh: "Subuh",
  syuruk: "Syuruk",
  dhuha: "Dhuha",
  zohor: "Zohor",
  asar: "Asar",
  maghrib: "Maghrib",
  isyak: "Isyak",
};
const BACKGROUND_POSITIONS = {
  center: "is-position-center",
  top: "is-position-top",
  bottom: "is-position-bottom",
  left: "is-position-left",
  right: "is-position-right",
};

export class MimbarPrayerScreenCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._backgroundIndex = 0;
    this._slideIndex = 0;
    this._lifecycle = { kind: "normal" };
    this._isIntersecting = true;
    this._onVisibilityChange = () => this._syncMotionState();
  }

  setConfig(config) {
    assertMimbarConfig(config);
    this._config = structuredClone(config);
    this._mimbarSettingsEntities = undefined;
    this._mimbarSettingsDiscovery = undefined;
    this._buildDomOnce();
    this._restartRotationTimers();
    this._render(new Date());
    this._discoverMimbarSettings();
  }

  set hass(hass) {
    const shouldRender = !this._hass || this._hasRelevantStateChange(this._hass, hass);
    this._hass = hass;
    this._discoverMimbarSettings();
    if (shouldRender) {
      this._applyBackground(this._backgroundIndex);
      this._render(new Date());
    }
  }

  connectedCallback() {
    document.addEventListener("visibilitychange", this._onVisibilityChange);
    this._observeMotionVisibility();
    if (!this._tickId) {
      this._tickId = window.setInterval(() => this._render(new Date()), 1_000);
    }
  }

  disconnectedCallback() {
    document.removeEventListener("visibilitychange", this._onVisibilityChange);
    this._motionObserver?.disconnect();
    this._motionObserver = undefined;
    window.clearInterval(this._tickId);
    window.clearInterval(this._backgroundId);
    window.clearInterval(this._slideId);
    this._tickId = undefined;
    this._backgroundId = undefined;
    this._slideId = undefined;
  }

  getCardSize() {
    return 12;
  }

  getGridOptions() {
    return { columns: 12 };
  }

  static getConfigElement() {
    return document.createElement("solat-my-mimbar-card-editor");
  }

  static getStubConfig() {
    return {
      type: `custom:${CARD_TYPE}`,
      title: "",
      location: "",
      message: "",
      time_format: "24h",
      background: { mode: "courtyard", color: "forest" },
      entities: {
        subuh: "",
        syuruk: "",
        zohor: "",
        asar: "",
        maghrib: "",
        isyak: "",
        hijri: "",
        current: "",
      },
    };
  }

  _buildDomOnce() {
    if (this._nodes) {
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      :host {
        container-type: inline-size;
        block-size: calc(100dvh - var(--header-height, 0px));
        display: block;
        max-block-size: calc(100dvh - var(--header-height, 0px));
        min-height: 0;
        overflow: hidden;
        --mimbar-accent: oklch(0.88 0.08 151);
        --mimbar-accent-strong: oklch(0.96 0.035 151);
        --mimbar-accent-soft: oklch(0.58 0.07 151 / 0.16);
        --mimbar-accent-line: oklch(0.76 0.08 151 / 0.34);
        --mimbar-glass-start: oklch(0.5 0.09 151 / 0.34);
        --mimbar-glass-mid: oklch(0.32 0.07 151 / 0.4);
        --mimbar-glass-deep: oklch(0.15 0.04 151 / 0.75);
        --mimbar-glass-glow: oklch(0.66 0.1 151 / 0.18);
        --mimbar-glass-sheen: oklch(0.98 0.02 151 / 0.28);
        --mimbar-glass-sheen-accent: oklch(0.88 0.08 151 / 0.18);
        --mimbar-current-fill: oklch(0.4 0.055 151 / 0.27);
        --mimbar-next-fill: oklch(0.49 0.08 151 / 0.28);
        --mimbar-ambient-start: oklch(0.45 0.07 151 / 0.28);
        --mimbar-ambient-end: oklch(0.28 0.045 151 / 0.08);
        --mimbar-rail-surface: oklch(0.13 0.035 151 / 0.9);
        --mimbar-countdown-hours: oklch(0.8 0.1 151);
        --mimbar-countdown-minutes: oklch(0.9 0.04 151);
        --mimbar-countdown-seconds: oklch(0.74 0.09 178);
        --mimbar-ring-outer: oklch(0.72 0.09 151 / 0.5);
        --mimbar-ring-inner: oklch(0.82 0.05 151 / 0.42);
        --mimbar-gold: var(--mimbar-accent);
        --mimbar-gold-strong: var(--mimbar-accent-strong);
        --mimbar-ink: #f7f1e6;
        --mimbar-muted: #b7c6b8;
        --mimbar-deep: #05120d;
        --mimbar-surface: #0b1d15;
        --mimbar-line: var(--mimbar-accent-line);
        --mimbar-ease: 760ms cubic-bezier(0.16, 1, 0.3, 1);
        --mimbar-background-opacity: 0.76;
        --mimbar-background-veil-opacity: 1;
        color: var(--mimbar-ink);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      *, *::before, *::after { box-sizing: border-box; }
      ::selection { background: var(--mimbar-gold); color: var(--mimbar-deep); }
      .mimbar-screen { --mimbar-gold: var(--mimbar-accent); --mimbar-gold-strong: var(--mimbar-accent-strong); background: radial-gradient(ellipse at 6% 52%, var(--mimbar-ambient-start), transparent 42%), radial-gradient(ellipse at 87% 12%, var(--mimbar-ambient-end), transparent 34%), #04120c; block-size: 100%; isolation: isolate; min-height: 0; overflow: hidden; position: relative; }
      .mimbar-screen[data-background-mode="color"][data-background-color="midnight"] { background: radial-gradient(ellipse at 7% 80%, rgba(45, 83, 145, 0.34), transparent 44%), radial-gradient(ellipse at 90% 15%, rgba(104, 156, 222, 0.16), transparent 32%), #061225; }
      .mimbar-screen[data-background-mode="color"][data-background-color="slate"] { background: radial-gradient(ellipse at 6% 52%, rgba(86, 111, 108, 0.25), transparent 44%), radial-gradient(ellipse at 87% 12%, rgba(205, 190, 148, 0.08), transparent 34%), #111716; }
      .mimbar-screen[data-background-mode="color"][data-background-color="burgundy"] { background: radial-gradient(ellipse at 8% 78%, rgba(126, 30, 49, 0.34), transparent 45%), radial-gradient(ellipse at 87% 12%, var(--mimbar-ambient-end), transparent 34%), #26090e; }
      .mimbar-screen[data-background-mode="color"][data-background-color="indigo"] { background: radial-gradient(ellipse at 5% 70%, rgba(67, 54, 145, 0.34), transparent 45%), radial-gradient(ellipse at 88% 12%, rgba(181, 166, 235, 0.1), transparent 34%), #12102d; }
      .mimbar-screen::before { background: radial-gradient(ellipse at center, var(--mimbar-ambient-start), var(--mimbar-ambient-end) 36%, transparent 70%); content: ""; filter: blur(2px); height: 68vh; left: -16vw; opacity: var(--mimbar-background-opacity); pointer-events: none; position: absolute; top: 16%; transform: translate3d(0, 0, 0) scale(0.96); width: 68vw; z-index: 2; }
      .mimbar-screen::after { background: linear-gradient(106deg, rgba(2, 8, 9, 0.90) 0%, rgba(3, 10, 11, 0.82) 44%, rgba(2, 7, 8, 0.68) 100%); content: ""; inset: 0; opacity: var(--mimbar-background-veil-opacity); pointer-events: none; position: absolute; z-index: 1; }
      .mimbar-screen.is-motion-paused .hero-time::after { animation-play-state: paused; }
      .background { inset: 0; overflow: hidden; position: absolute; z-index: 0; }
      .background-image { height: 100%; inset: 0; object-fit: cover; opacity: 0; position: absolute; transition: opacity var(--mimbar-ease); width: 100%; }
      .background-image.is-visible { opacity: var(--mimbar-background-opacity); }
      .background-image.is-position-center { object-position: center; }
      .background-image.is-position-top { object-position: center top; }
      .background-image.is-position-bottom { object-position: center bottom; }
      .background-image.is-position-left { object-position: left center; }
      .background-image.is-position-right { object-position: right center; }
      .mimbar-layout { block-size: 100%; display: grid; grid-template-areas: "hero schedule" "rail rail"; grid-template-columns: minmax(0, 0.96fr) minmax(0, 1.04fr); grid-template-rows: minmax(0, 1fr) auto; min-height: 0; position: relative; z-index: 3; }
      .hero-region { display: grid; gap: clamp(20px, 2.6vw, 36px); grid-area: hero; grid-template-rows: auto auto minmax(0, 1fr); min-height: 0; padding: clamp(30px, 4.4vw, 76px); }
      .identity { display: grid; gap: 7px; max-width: 52ch; }
      .identity-title { font-size: clamp(18px, 1.8vw, 27px); font-weight: 730; letter-spacing: 0.045em; line-height: 1.12; margin: 0; text-transform: uppercase; }
      .identity-location { color: var(--mimbar-muted); font-size: 14px; font-weight: 650; line-height: 1.45; margin: 0; }
      .clock-block { border-bottom: 1px solid var(--mimbar-accent-line); display: grid; gap: 12px; margin-top: clamp(20px, 3vw, 54px); padding-bottom: 18px; }
      .local-clock { font-feature-settings: "tnum"; font-size: clamp(32px, 4.5vw, 72px); font-variant-numeric: tabular-nums; font-weight: 710; letter-spacing: -0.035em; line-height: 0.9; margin: 0; }
      .calendar { color: var(--mimbar-muted); display: grid; font-size: clamp(15px, 1.3vw, 20px); font-weight: 600; gap: 3px; line-height: 1.4; margin: 0; }
      .calendar span:last-child { color: var(--mimbar-gold); }
      .day-period { font-size: 0.4em; font-weight: 700; letter-spacing: 0.06em; margin-left: 0.12em; opacity: 0.66; }
      .hero-panel { align-content: center; display: grid; gap: 12px; justify-items: center; min-height: 0; overflow: hidden; padding: clamp(28px, 3.5vw, 52px); position: relative; text-align: center; }
      .hero-panel::before { background: radial-gradient(circle, var(--mimbar-glass-glow), transparent 66%); content: ""; height: min(100%, 520px); pointer-events: none; position: absolute; top: 50%; transform: translateY(-50%); width: min(100%, 520px); }
      .hero-panel::after { border: 1px solid var(--mimbar-ring-outer); border-radius: 50%; content: ""; height: min(92%, 490px); pointer-events: none; position: absolute; top: 50%; transform: translateY(-50%); width: min(92%, 490px); }
      .hero-panel > * { position: relative; z-index: 1; }
      .hero-signal { color: var(--mimbar-gold-strong); font-size: 12px; font-weight: 720; letter-spacing: 0.12em; line-height: 1.25; margin: 0; text-transform: uppercase; }
      .hero-time { display: grid; font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; margin: 0; min-height: clamp(260px, 31vw, 390px); place-items: center; position: relative; width: min(100%, 480px); }
      .hero-time::before { -webkit-backdrop-filter: blur(18px) saturate(1.35); backdrop-filter: blur(18px) saturate(1.35); background: linear-gradient(142deg, var(--mimbar-glass-start) 0%, var(--mimbar-glass-mid) 28%, var(--mimbar-glass-deep) 54%, var(--mimbar-glass-deep)), radial-gradient(circle at 34% 24%, var(--mimbar-glass-glow), transparent 31%); border: 1px solid var(--mimbar-ring-outer); border-radius: 50%; border-right-color: var(--mimbar-ring-inner); border-top-color: var(--mimbar-ring-inner); box-shadow: inset 0 1px 0 rgba(247, 241, 230, 0.26), inset 0 -22px 48px rgba(0, 0, 0, 0.24), 0 18px 42px rgba(0, 0, 0, 0.2); content: ""; height: min(100%, 390px); left: 50%; pointer-events: none; position: absolute; top: 50%; transform: translate(-50%, -50%) rotate(-42deg); width: min(100%, 390px); z-index: 0; }
      .hero-time::after { animation: mimbar-glass-sheen 9s cubic-bezier(0.16, 1, 0.3, 1) infinite; background: linear-gradient(118deg, transparent 26%, var(--mimbar-glass-sheen) 43%, var(--mimbar-glass-sheen-accent) 52%, transparent 67%); border: 1px solid var(--mimbar-ring-inner); border-bottom-color: var(--mimbar-ring-outer); border-left-color: var(--mimbar-ring-outer); border-radius: 50%; clip-path: circle(50%); content: ""; height: min(80%, 304px); left: 50%; pointer-events: none; position: absolute; top: 50%; width: min(80%, 304px); z-index: 0; }
      .countdown-digits { align-items: flex-start; display: flex; gap: clamp(3px, 0.8vw, 12px); position: relative; z-index: 1; }
      .countdown-segment { display: grid; gap: 7px; isolation: isolate; justify-items: center; min-width: 0; position: relative; }
      .countdown-segment::before { background: radial-gradient(circle, var(--mimbar-segment-color) 0%, transparent 70%); content: ""; filter: blur(8px); inset: -24px -12px; opacity: 0.14; pointer-events: none; position: absolute; z-index: 0; }
      .countdown-segment:nth-child(1) { --mimbar-segment-color: var(--mimbar-countdown-hours); }
      .countdown-segment:nth-child(3) { --mimbar-segment-color: var(--mimbar-countdown-minutes); }
      .countdown-segment:nth-child(5) { --mimbar-segment-color: var(--mimbar-countdown-seconds); }
      .countdown-value { color: var(--mimbar-segment-color, var(--mimbar-gold-strong)); font-size: clamp(44px, 7vw, 96px); font-weight: 720; letter-spacing: -0.035em; line-height: 0.82; position: relative; text-shadow: 0 10px 24px rgba(0, 0, 0, 0.28); z-index: 1; }
      .countdown-unit { color: var(--mimbar-segment-color, var(--mimbar-muted)); font-size: 12px; font-weight: 700; letter-spacing: 0.1em; line-height: 1.25; opacity: 0.82; position: relative; text-transform: uppercase; z-index: 1; }
      .countdown-separator { align-self: center; color: var(--mimbar-countdown-minutes); font-size: clamp(36px, 5.4vw, 68px); font-weight: 650; line-height: 0.7; margin-top: -23px; }
      .countdown-status { color: var(--mimbar-gold-strong); display: none; font-size: clamp(34px, 6vw, 72px); font-weight: 760; letter-spacing: -0.035em; line-height: 1; margin: 0; position: relative; text-align: center; z-index: 1; }
      .hero-time.is-status .countdown-digits { display: none; }
      .hero-time.is-status .countdown-status { display: block; }
      .hero-label { color: var(--mimbar-ink); font-size: clamp(20px, 2.2vw, 30px); font-weight: 700; line-height: 1.15; margin: 0; }
      .hero-detail { color: var(--mimbar-muted); font-size: 14px; font-weight: 620; line-height: 1.45; margin: 0; }
      .schedule-region { align-self: stretch; display: grid; grid-area: schedule; min-height: 0; padding: clamp(30px, 4.4vw, 76px) clamp(30px, 5vw, 96px); }
      .schedule-shell { align-content: stretch; display: grid; gap: 24px; grid-template-rows: auto minmax(0, 1fr); min-height: 0; }
      .schedule-heading { color: var(--mimbar-ink); font-size: clamp(18px, 1.7vw, 25px); font-weight: 690; line-height: 1.2; margin: 0; }
      .schedule-list { border-bottom: 1px solid rgba(183, 198, 184, 0.18); border-top: 1px solid rgba(183, 198, 184, 0.18); display: grid; grid-template-rows: repeat(6, minmax(clamp(62px, 6.4vw, 88px), 1fr)); list-style: none; margin: 0; min-height: 0; padding: 0; }
      .schedule-row { align-items: center; border-bottom: 1px solid rgba(183, 198, 184, 0.15); display: grid; gap: 0 14px; grid-template-areas: "icon name state time"; grid-template-columns: clamp(28px, 2.1vw, 34px) auto minmax(0, 1fr) auto; min-height: clamp(62px, 6.4vw, 88px); padding: 13px 16px; transition: background-color 240ms ease, color 240ms ease; }
      .schedule-row:last-child { border-bottom: 0; }
      .schedule-row.is-current { background: linear-gradient(90deg, var(--mimbar-current-fill), transparent 78%); }
      .schedule-row.is-next { background: linear-gradient(90deg, var(--mimbar-next-fill), var(--mimbar-next-fill) 62%, var(--mimbar-accent-soft) 82%, transparent); }
      .schedule-name { font-size: clamp(17px, 1.65vw, 25px); font-weight: 680; grid-area: name; line-height: 1.15; }
      .schedule-icon { --mimbar-icon-size: clamp(24px, 1.85vw, 28px); --mdc-icon-size: var(--mimbar-icon-size); align-self: center; color: var(--mimbar-muted); grid-area: icon; height: var(--mimbar-icon-size); width: var(--mimbar-icon-size); }
      .schedule-time { align-self: center; color: var(--mimbar-ink); font-feature-settings: "tnum"; font-size: clamp(22px, 2.5vw, 39px); font-variant-numeric: tabular-nums; font-weight: 700; grid-area: time; letter-spacing: -0.025em; line-height: 1; text-align: right; }
      .schedule-state { align-self: center; border: 1px solid var(--mimbar-accent-line); border-radius: 999px; color: var(--mimbar-muted); font-size: 12px; font-weight: 760; grid-area: state; justify-self: start; letter-spacing: 0.055em; line-height: 1.25; padding: 3px 10px; text-transform: uppercase; }
      .schedule-state:empty { display: none; }
      .schedule-row.is-current .schedule-state { color: var(--mimbar-muted); }
      .schedule-row.is-next .schedule-state { background: var(--mimbar-accent-soft); border-color: var(--mimbar-gold); color: var(--mimbar-gold-strong); }
      .schedule-row.is-past .schedule-name, .schedule-row.is-past .schedule-time { color: var(--mimbar-muted); }
      .schedule-row.is-past .schedule-icon { opacity: 0.62; }
      .schedule-row.is-current .schedule-name, .schedule-row.is-current .schedule-time { color: var(--mimbar-ink); }
      .schedule-row.is-next .schedule-name, .schedule-row.is-next .schedule-time { color: var(--mimbar-gold-strong); }
      .schedule-row.is-next .schedule-icon { color: var(--mimbar-gold-strong); filter: drop-shadow(0 4px 8px var(--mimbar-accent-soft)); }
      .lower-rail { align-items: center; background: var(--mimbar-rail-surface); border-top: 1px solid var(--mimbar-line); display: grid; gap: 24px; grid-area: rail; grid-template-columns: minmax(0, 0.85fr) minmax(0, 1fr) minmax(0, 1.5fr); padding: 22px clamp(30px, 4.4vw, 76px) 24px; }
      .rail-block { align-content: start; display: grid; gap: 7px; min-height: 44px; }
      .rail-block + .rail-block { border-left: 1px solid rgba(183, 198, 184, 0.18); padding-left: 24px; }
      .rail-items { display: grid; gap: 7px; }
      .rail-item { align-items: baseline; display: flex; flex-wrap: wrap; gap: 8px; }
      .rail-label { color: var(--mimbar-muted); font-size: 12px; font-weight: 760; letter-spacing: 0.055em; line-height: 1.25; text-transform: uppercase; }
      .rail-value { color: var(--mimbar-ink); font-feature-settings: "tnum"; font-size: 15px; font-variant-numeric: tabular-nums; font-weight: 680; line-height: 1.35; }
      .rail-item.is-current .rail-label, .rail-item.is-current .rail-value { color: var(--mimbar-gold-strong); }
      .rail-message { color: var(--mimbar-ink); font-size: 15px; font-weight: 590; line-height: 1.45; margin: 0; max-width: 64ch; }
      .rail-image { border-radius: 10px; display: block; max-height: 92px; max-width: 100%; object-fit: contain; object-position: left center; }
      .is-hidden { display: none; }
      @container (max-width: 700px) {
        .mimbar-screen { block-size: 100%; max-block-size: 100%; min-height: 0; overflow: hidden; }
        .mimbar-layout { block-size: 100%; grid-template-areas: "hero" "schedule" "rail"; grid-template-columns: 1fr; grid-template-rows: minmax(0, 0.9fr) minmax(0, 1.1fr) auto; min-height: 0; }
        .hero-region { gap: 10px; grid-template-rows: auto auto minmax(0, 1fr); padding: 16px 18px 8px; }
        .clock-block { align-items: end; display: flex; flex-wrap: wrap; gap: 16px; margin-top: 0; padding-bottom: 10px; }
        .calendar { font-size: 14px; }
        .hero-panel { gap: 6px; min-height: 0; padding: 8px; }
        .hero-time { min-height: clamp(156px, 26vh, 220px); }
        .schedule-region { padding: 8px 18px 12px; }
        .schedule-shell { align-content: stretch; gap: 10px; grid-template-rows: auto minmax(0, 1fr); }
        .schedule-list { grid-template-rows: repeat(6, minmax(0, 1fr)); }
        .schedule-row { min-height: 0; padding: 6px 4px; }
        .lower-rail { gap: 12px; grid-template-columns: minmax(0, 0.85fr) minmax(0, 1fr) minmax(0, 1.5fr); padding: 10px 18px 12px; }
        .rail-block { gap: 3px; min-height: 0; }
        .rail-block + .rail-block { border-left: 1px solid rgba(183, 198, 184, 0.18); border-top: 0; padding-left: 12px; padding-top: 0; }
        .rail-items { gap: 3px; }
        .rail-label { font-size: 10px; }
        .rail-value { font-size: 12px; }
        .rail-message { font-size: 12px; line-height: 1.3; }
      }
      @container (max-width: 620px) {
        .hero-region { gap: 8px; padding: 14px 16px 6px; }
        .schedule-region { padding: 6px 16px 10px; }
        .identity { gap: 3px; }
        .identity-title { font-size: 18px; }
        .identity-location { font-size: 11px; }
        .clock-block { gap: 8px; padding-bottom: 8px; }
        .local-clock { font-size: clamp(28px, 8vw, 40px); }
        .calendar { font-size: 12px; }
        .hero-panel { gap: 4px; min-height: 0; padding: 4px; }
        .hero-signal { font-size: 10px; }
        .hero-time { min-height: clamp(146px, 42vw, 184px); }
        .countdown-digits { gap: 3px; }
        .countdown-value { font-size: clamp(38px, 12.2vw, 64px); }
        .countdown-separator { font-size: clamp(32px, 9vw, 48px); margin-top: -20px; }
        .countdown-unit { font-size: 10px; }
        .hero-label { font-size: 18px; }
        .hero-detail { font-size: 12px; }
        .schedule-row { grid-template-columns: 28px auto minmax(0, 1fr) auto; padding: 5px 4px; }
        .schedule-shell { gap: 8px; }
        .schedule-name { font-size: 16px; }
        .schedule-time { font-size: 22px; }
        .schedule-state { font-size: 10px; padding: 1px 7px; }
        .schedule-icon { --mimbar-icon-size: 22px; }
        .lower-rail { gap: 8px; padding: 8px 16px 10px; }
        .rail-block + .rail-block { padding-left: 8px; }
        .rail-item { gap: 4px; }
      }
      @keyframes mimbar-glass-sheen {
        0%, 100% { opacity: 0.28; transform: translate3d(-56%, -48%, 0) rotate(8deg); }
        50% { opacity: 0.86; transform: translate3d(-44%, -52%, 0) rotate(8deg); }
      }
      @media (prefers-reduced-motion: reduce) {
        .hero-time::after { animation: none; }
        .background-image, .schedule-row { transition: none; }
      }
    `;

    const screen = document.createElement("section");
    screen.className = "mimbar-screen";
    const background = document.createElement("div");
    background.className = "background";
    const backgroundLayers = [this._createBackgroundLayer(), this._createBackgroundLayer()];
    background.append(...backgroundLayers);

    const layout = document.createElement("div");
    layout.className = "mimbar-layout";
    const heroRegion = document.createElement("section");
    heroRegion.className = "hero-region";
    const identity = document.createElement("div");
    identity.className = "identity";
    const title = document.createElement("h1");
    title.className = "identity-title";
    const location = document.createElement("p");
    location.className = "identity-location";
    identity.append(title, location);

    const clockBlock = document.createElement("div");
    clockBlock.className = "clock-block";
    const localClock = document.createElement("p");
    localClock.className = "local-clock";
    const calendar = document.createElement("p");
    calendar.className = "calendar";
    const gregorianDate = document.createElement("span");
    const hijriDate = document.createElement("span");
    calendar.append(gregorianDate, hijriDate);
    clockBlock.append(localClock, calendar);

    const heroPanel = document.createElement("section");
    heroPanel.className = "hero-panel";
    const heroSignal = document.createElement("p");
    heroSignal.className = "hero-signal";
    const heroTime = document.createElement("div");
    heroTime.className = "hero-time";
    heroTime.setAttribute("role", "timer");
    const heroDigits = document.createElement("div");
    heroDigits.className = "countdown-digits";
    const hours = this._createCountdownSegment("Jam");
    const firstSeparator = document.createElement("span");
    firstSeparator.className = "countdown-separator";
    firstSeparator.setAttribute("aria-hidden", "true");
    firstSeparator.textContent = ":";
    const minutes = this._createCountdownSegment("Minit");
    const secondSeparator = document.createElement("span");
    secondSeparator.className = "countdown-separator";
    secondSeparator.setAttribute("aria-hidden", "true");
    secondSeparator.textContent = ":";
    const seconds = this._createCountdownSegment("Saat");
    heroDigits.append(hours.root, firstSeparator, minutes.root, secondSeparator, seconds.root);
    const heroStatus = document.createElement("p");
    heroStatus.className = "countdown-status";
    heroTime.append(heroDigits, heroStatus);
    const heroLabel = document.createElement("p");
    heroLabel.className = "hero-label";
    const heroDetail = document.createElement("p");
    heroDetail.className = "hero-detail";
    heroPanel.append(heroSignal, heroTime, heroLabel, heroDetail);
    heroRegion.append(identity, clockBlock, heroPanel);

    const scheduleRegion = document.createElement("section");
    scheduleRegion.className = "schedule-region";
    const scheduleShell = document.createElement("div");
    scheduleShell.className = "schedule-shell";
    const scheduleHeading = document.createElement("h2");
    scheduleHeading.className = "schedule-heading";
    scheduleHeading.textContent = "Waktu Solat Hari Ini";
    const scheduleList = document.createElement("ul");
    scheduleList.className = "schedule-list";
    const scheduleRows = new Map();
    for (const key of ["subuh", "syuruk", "zohor", "asar", "maghrib", "isyak"]) {
      const row = this._createScheduleRow(key);
      scheduleRows.set(key, row);
      scheduleList.append(row.root);
    }
    scheduleShell.append(scheduleHeading, scheduleList);
    scheduleRegion.append(scheduleShell);

    const lowerRail = document.createElement("aside");
    lowerRail.className = "lower-rail";
    const secondaryBlock = this._createRailBlock();
    const fastingBlock = this._createRailBlock();
    const contentBlock = this._createRailBlock();
    lowerRail.append(secondaryBlock, fastingBlock, contentBlock);

    layout.append(heroRegion, scheduleRegion, lowerRail);
    screen.append(background, layout);
    this.shadowRoot.append(style, screen);
    this._nodes = {
      screen,
      backgroundLayers,
      title,
      location,
      localClock,
      gregorianDate,
      hijriDate,
      heroSignal,
      heroTime,
      heroStatus,
      heroHours: hours.value,
      heroMinutes: minutes.value,
      heroSeconds: seconds.value,
      heroLabel,
      heroDetail,
      scheduleRows,
      secondaryBlock,
      fastingBlock,
      contentBlock,
    };
    this._syncMotionState();
    if (this.isConnected) {
      this._observeMotionVisibility();
    }
  }

  _observeMotionVisibility() {
    if (!this._nodes?.screen || this._motionObserver || !("IntersectionObserver" in window)) {
      return;
    }

    this._motionObserver = new IntersectionObserver(([entry]) => {
      this._isIntersecting = entry.isIntersecting;
      this._syncMotionState();
    }, { threshold: 0.01 });
    this._motionObserver.observe(this._nodes.screen);
    this._syncMotionState();
  }

  _syncMotionState() {
    if (!this._nodes?.screen) {
      return;
    }

    const documentIsHidden = typeof document !== "undefined" && document.visibilityState === "hidden";
    this._nodes.screen.classList.toggle("is-motion-paused", documentIsHidden || !this._isIntersecting);
  }

  _createBackgroundLayer() {
    const image = document.createElement("img");
    image.className = "background-image";
    image.alt = "";
    image.setAttribute("aria-hidden", "true");
    return image;
  }

  _createCountdownSegment(unit) {
    const root = document.createElement("span");
    root.className = "countdown-segment";
    const value = document.createElement("span");
    value.className = "countdown-value";
    const label = document.createElement("span");
    label.className = "countdown-unit";
    label.textContent = unit;
    root.append(value, label);
    return { root, value };
  }

  _createScheduleRow(key) {
    const root = document.createElement("li");
    root.className = "schedule-row";
    const icon = document.createElement("ha-icon");
    icon.className = "schedule-icon";
    icon.setAttribute("icon", SCHEDULE_PRAYER_ICONS[key]);
    const name = document.createElement("span");
    name.className = "schedule-name";
    const time = document.createElement("time");
    time.className = "schedule-time";
    const state = document.createElement("span");
    state.className = "schedule-state";
    root.append(icon, name, time, state);
    return { root, icon, name, time, state, key };
  }

  _createRailBlock() {
    const block = document.createElement("div");
    block.className = "rail-block";
    return block;
  }

  _restartRotationTimers() {
    window.clearInterval(this._backgroundId);
    window.clearInterval(this._slideId);
    this._backgroundId = undefined;
    this._slideId = undefined;
    this._backgroundIndex = 0;
    this._slideIndex = 0;
    this._applyBackground(0);

    const images = this._backgroundImages();
    if (images.length > 1) {
      const seconds = this._config.background.rotation_seconds ?? 60;
      this._backgroundId = window.setInterval(() => {
        this._backgroundIndex = (this._backgroundIndex + 1) % images.length;
        this._applyBackground(this._backgroundIndex);
      }, seconds * 1_000);
    }

    const slides = this._config?.slides ?? [];
    if (slides.length > 1) {
      const seconds = this._config.slide_interval_seconds ?? 60;
      this._slideId = window.setInterval(() => {
        this._slideIndex = (this._slideIndex + 1) % slides.length;
        this._render(new Date());
      }, seconds * 1_000);
    }
  }

  _applyBackground(index) {
    if (!this._nodes) {
      return;
    }

    const background = this._effectiveBackground();
    this._nodes.screen.dataset.backgroundMode = background.mode;
    this._nodes.screen.dataset.backgroundColor = background.color;
    for (const [name, value] of Object.entries(resolveMimbarTheme(background.color))) {
      const property = name.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);
      this._nodes.screen.style.setProperty(`--mimbar-${property}`, value);
    }
    this._nodes.screen.style.setProperty("--mimbar-background-opacity", String(background.opacity / 100));
    this._nodes.screen.style.setProperty("--mimbar-background-veil-opacity", String(backgroundVeilOpacity(background.opacity)));
    const images = this._backgroundImages();
    const source = images[index];
    const incomingIndex = index % this._nodes.backgroundLayers.length;
    const positionClass = BACKGROUND_POSITIONS[this._config?.background?.position] ?? "is-position-center";

    for (const [layerIndex, layer] of this._nodes.backgroundLayers.entries()) {
      layer.className = `background-image ${positionClass}`;
      if (layerIndex === incomingIndex && source) {
        layer.src = source;
        layer.classList.add("is-visible");
      } else {
        layer.classList.remove("is-visible");
        if (!source) {
          layer.removeAttribute("src");
        }
      }
    }
  }

  _backgroundImages() {
    const background = this._config?.background;
    const effective = this._effectiveBackground();
    if (background?.source === "integration") {
      return resolveIntegrationBackgroundImages({
        visibility: this._hass?.states?.[this._mimbarSettingsEntities?.visibility]?.state,
        image: this._hass?.states?.[this._mimbarSettingsEntities?.image]?.state,
      });
    }
    if (effective.mode === "courtyard") {
      return [MIMBAR_COURTYARD_BACKGROUND_URL];
    }
    if (effective.mode !== "image") {
      return [];
    }
    return background?.images ?? [];
  }

  _effectiveBackground() {
    return resolveMimbarBackground(this._config?.background, {
      theme: this._hass?.states?.[this._mimbarSettingsEntities?.theme]?.state,
      opacity: this._hass?.states?.[this._mimbarSettingsEntities?.opacity]?.state,
    });
  }

  _discoverMimbarSettings() {
    if (
      this._mimbarSettingsDiscovery
      || !this._hass?.callWS
    ) {
      return;
    }

    const config = this._config;
    const hass = this._hass;
    this._mimbarSettingsDiscovery = hass.callWS({ type: "config/entity_registry/list" })
      .then((registry) => {
        if (this._config !== config) {
          return;
        }
        const prayerEntry = registry.find((entry) => entry.entity_id === config.entities.subuh);
        const configEntryId = prayerEntry?.config_entry_id;
        if (!configEntryId) {
          return;
        }
        const findSetting = (suffix) => registry.find(
          (entry) => entry.unique_id === `${configEntryId}_${suffix}`,
        )?.entity_id;
        this._mimbarSettingsEntities = {
          theme: findSetting("mimbar_background"),
          visibility: findSetting("mimbar_background_visibility"),
          opacity: findSetting("mimbar_background_opacity"),
          image: findSetting("mimbar_background_image"),
          timeFormat: findSetting("mimbar_time_format"),
        };
        this._applyBackground(this._backgroundIndex);
        this._render(new Date());
      })
      .catch(() => undefined);
  }

  _hasRelevantStateChange(previousHass, nextHass) {
    if (previousHass?.config?.time_zone !== nextHass?.config?.time_zone) {
      return true;
    }

    const watchedEntityIds = [
      ...Object.values(this._config?.entities ?? {}),
      ...Object.values(this._mimbarSettingsEntities ?? {}),
    ].filter(Boolean);
    return watchedEntityIds.some(
      (entityId) => previousHass?.states?.[entityId] !== nextHass?.states?.[entityId],
    );
  }

  _render(now) {
    if (!this._config || !this._hass || !this._nodes) {
      return;
    }

    const states = this._hass.states ?? {};
    const timeZone = this._hass.config?.time_zone ?? "Asia/Kuala_Lumpur";
    const timeFormat = resolveMimbarTimeFormat(
      this._config.time_format,
      states[this._mimbarSettingsEntities?.timeFormat]?.state,
    );
    const view = buildPrayerView({
      config: { ...this._config, time_format: timeFormat },
      states,
      now,
      timeZone,
    });
    this._setText(this._nodes.title, this._config.title || "Waktu Solat");
    this._setClockText(this._nodes.localClock, view.localClock ?? "");
    this._setText(this._nodes.gregorianDate, view.gregorianDate ?? "");
    this._setText(this._nodes.hijriDate, view.hijriDate ?? "");
    this._setText(this._nodes.location, this._config.location || view.location || "Malaysia");

    if (view.status === "fault") {
      this._renderFault(view.message);
      return;
    }

    const prayerTimes = Object.fromEntries(
      view.schedule
        .filter((row) => MAIN_PRAYER_KEYS.includes(row.key))
        .map((row) => [row.key, row.at]),
    );
    const iqama = { ...this._config.iqama };
    if (this._isFriday(now, timeZone) && iqama.jumaat !== undefined) {
      iqama.zohor = iqama.jumaat;
    }
    this._lifecycle = resolveLifecycle({
      prayerTimes,
      iqama,
      adhanDurationMinutes: this._config.adhan_duration ?? 2,
      silenceDurationMinutes: this._config.silence_duration ?? 15,
      now,
    });

    this._renderSchedule(view, timeZone, now);
    this._renderHero(view, now);
    this._renderRail(view, states, now, timeZone, timeFormat);
  }

  _renderFault(message) {
    this._setHeroStatus(message);
    this._setText(this._nodes.heroSignal, "Data waktu solat");
    this._setText(this._nodes.heroLabel, "Waktu tidak dikemas kini");
    this._setText(this._nodes.heroDetail, "Semak entiti waktu solat yang dipetakan.");
    for (const row of this._nodes.scheduleRows.values()) {
      row.root.classList.remove("is-current", "is-next", "is-past");
      this._setText(row.name, PRAYER_LABELS[row.key]);
      this._setText(row.state, "");
      this._setText(row.time, "—");
    }
    this._replaceRailWithMessage("Paparan akan bersambung apabila waktu solat tersedia.");
  }

  _renderSchedule(view, timeZone, now) {
    const isFriday = this._isFriday(now, timeZone);
    for (const rowData of view.schedule) {
      const row = this._nodes.scheduleRows.get(rowData.key);
      const current = view.current?.location === "schedule" && view.current.key === rowData.key;
      const next = view.next.key === rowData.key;
      const label = rowData.key === "zohor" && isFriday && this._config.iqama?.jumaat !== undefined
        ? "Jumaat"
        : rowData.label;

      row.root.classList.toggle("is-current", current);
      row.root.classList.toggle("is-next", !current && next);
      row.root.classList.toggle("is-past", !current && !next && rowData.isPast);
      this._setText(row.name, label);
      this._setClockText(row.time, rowData.time);
      this._setText(row.state, current ? "Sekarang" : next ? "Seterusnya" : "");
      row.time.dateTime = rowData.at.toISOString();
    }
  }

  _renderHero(view, now) {
    if (this._lifecycle.kind === "adhan") {
      const label = this._prayerLabel(this._lifecycle.key, now);
      this._setHeroStatus(label);
      this._setText(this._nodes.heroSignal, "Waktu solat");
      this._setText(this._nodes.heroLabel, "Waktu solat telah masuk");
      this._setText(this._nodes.heroDetail, "Sila bersedia untuk menunaikan solat.");
      return;
    }

    if (this._lifecycle.kind === "iqamah") {
      const seconds = (this._lifecycle.at.valueOf() - now.valueOf()) / 1_000;
      this._setHeroCountdown(seconds);
      this._setText(this._nodes.heroSignal, "Iqamah");
      this._setText(this._nodes.heroLabel, `Iqamah ${this._prayerLabel(this._lifecycle.key, now)}`);
      this._setText(this._nodes.heroDetail, "Sila rapatkan saf dan bersedia.");
      return;
    }

    if (this._lifecycle.kind === "silence") {
      this._setHeroStatus("Sila Tenang");
      this._setText(this._nodes.heroSignal, "Waktu solat");
      this._setText(this._nodes.heroLabel, "Waktu solat sedang berlangsung");
      this._setText(this._nodes.heroDetail, "Matikan nada telefon dan beri ruang kepada jemaah.");
      return;
    }

    this._setHeroCountdown(view.countdownSeconds);
    this._setText(this._nodes.heroSignal, "Waktu seterusnya");
    this._setText(this._nodes.heroLabel, `Ke ${this._prayerLabel(view.next.key, now)}`);
    this._setText(this._nodes.heroDetail, "Waktu seterusnya");
  }

  _renderRail(view, states, now, timeZone, timeFormat) {
    if (this._lifecycle.kind !== "normal") {
      this._replaceRailWithMessage("Sila rapatkan saf, senyapkan telefon dan beri perhatian kepada solat.");
      return;
    }

    const rail = buildLowerRail({ config: this._config, states, now, timeZone });
    this._renderSecondaryRail(rail.secondary, view.current, timeZone, timeFormat);
    this._renderFastingRail(rail.fasting, timeZone, timeFormat);
    this._renderContentRail(rail.content);
  }

  _renderSecondaryRail(secondary, current, timeZone, timeFormat) {
    this._nodes.secondaryBlock.replaceChildren();
    const container = document.createElement("div");
    container.className = "rail-items";
    for (const item of secondary) {
      const row = this._createRailItem(
        item.label,
        formatPrayerTime(item.at, timeFormat, timeZone),
        current?.location === "rail" && current.key === item.key,
      );
      container.append(row);
    }
    if (secondary.length === 0) {
      container.append(this._createRailMessage("Imsak dan Dhuha boleh ditambah dalam YAML."));
    }
    this._nodes.secondaryBlock.append(container);
  }

  _renderFastingRail(fasting, timeZone, timeFormat) {
    this._nodes.fastingBlock.replaceChildren();
    if (!fasting) {
      this._nodes.fastingBlock.append(this._createRailMessage("Maklumat Ramadan akan muncul secara automatik."));
      return;
    }

    const label = fasting.kind === "sahur" ? "Sahur berakhir" : "Berbuka";
    this._nodes.fastingBlock.append(
      this._createRailItem(label, formatPrayerTime(fasting.at, timeFormat, timeZone), false),
    );
  }

  _renderContentRail(content) {
    this._nodes.contentBlock.replaceChildren();
    if (content.type === "slides" && content.slides.length > 0) {
      const slide = content.slides[this._slideIndex % content.slides.length];
      if (slide.type === "image") {
        const image = document.createElement("img");
        image.className = "rail-image";
        image.src = slide.src;
        image.alt = slide.alt;
        this._nodes.contentBlock.append(image);
        return;
      }
      this._nodes.contentBlock.append(this._createRailMessage(slide.ms));
      return;
    }

    this._nodes.contentBlock.append(
      this._createRailMessage(content.message || "Sila rapatkan saf dan matikan nada telefon."),
    );
  }

  _replaceRailWithMessage(message) {
    for (const block of [this._nodes.secondaryBlock, this._nodes.fastingBlock, this._nodes.contentBlock]) {
      block.replaceChildren();
    }
    this._nodes.contentBlock.append(this._createRailMessage(message));
  }

  _createRailItem(label, value, current) {
    const row = document.createElement("div");
    row.className = "rail-item";
    row.classList.toggle("is-current", current);
    const labelNode = document.createElement("span");
    labelNode.className = "rail-label";
    const valueNode = document.createElement("span");
    valueNode.className = "rail-value";
    this._setText(labelNode, label);
    this._setText(valueNode, value);
    row.append(labelNode, valueNode);
    return row;
  }

  _createRailMessage(message) {
    const paragraph = document.createElement("p");
    paragraph.className = "rail-message";
    this._setText(paragraph, message);
    return paragraph;
  }

  _prayerLabel(key, now) {
    const isFriday = this._isFriday(now, this._hass.config?.time_zone ?? "Asia/Kuala_Lumpur");
    if (key === "zohor" && isFriday && this._config.iqama?.jumaat !== undefined) {
      return "Jumaat";
    }
    return PRAYER_LABELS[key] ?? "Waktu Solat";
  }

  _isFriday(now, timeZone) {
    return new Intl.DateTimeFormat("en-US", { timeZone, weekday: "short" }).format(now) === "Fri";
  }

  _setHeroCountdown(seconds) {
    const [hours, minutes, remainingSeconds] = formatCountdown(seconds).split(":");
    this._nodes.heroTime.classList.remove("is-status");
    this._nodes.heroTime.setAttribute("aria-label", `${hours} jam ${minutes} minit ${remainingSeconds} saat`);
    this._setText(this._nodes.heroHours, hours);
    this._setText(this._nodes.heroMinutes, minutes);
    this._setText(this._nodes.heroSeconds, remainingSeconds);
  }

  _setHeroStatus(message) {
    this._nodes.heroTime.classList.add("is-status");
    this._nodes.heroTime.setAttribute("aria-label", message);
    this._setText(this._nodes.heroStatus, message);
  }

  _setText(node, value) {
    node.textContent = String(value ?? "");
  }

  _setClockText(node, value) {
    const { clock, period } = splitDayPeriod(String(value ?? ""));
    if (node.textContent === (period ? `${clock} ${period}` : clock)) {
      return;
    }
    node.replaceChildren(clock);
    if (period) {
      const suffix = document.createElement("span");
      suffix.className = "day-period";
      suffix.textContent = ` ${period}`;
      node.append(suffix);
    }
  }
}

if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, MimbarPrayerScreenCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === CARD_TYPE)) {
  window.customCards.push({
    type: CARD_TYPE,
    name: "Paparan Mimbar Waktu Solat",
    description: "Paparan skrin penuh waktu solat Malaysia",
    preview: false,
  });
}
