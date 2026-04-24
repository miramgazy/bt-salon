import { useState } from "react";

// ─── Mock Data ───────────────────────────────────────────────────────────────
const ORG = {
  name: "Студия красоты Lumière",
  greeting: "Добро пожаловать!",
  instagram: "https://instagram.com/lumiere_beauty",
};

const CATEGORIES = [
  { id: 1, icon: "✂️", name: { ru: "Стрижки", kz: "Шаштараз" } },
  { id: 2, icon: "💅", name: { ru: "Маникюр", kz: "Маникюр" } },
  { id: 3, icon: "💆", name: { ru: "Массаж", kz: "Массаж" } },
  { id: 4, icon: "🧖", name: { ru: "Уход за лицом", kz: "Бет күтімі" } },
  { id: 5, icon: "💇", name: { ru: "Окрашивание", kz: "Бояу" } },
  { id: 6, icon: "🪮", name: { ru: "Укладка", kz: "Үлгілеу" } },
];

const MASTERS = [
  { id: 1, name: "Аида Нурланова", photo: "👩‍🦱", rating: 4.9, categories: [1, 2, 5, 6], exp: "5 лет" },
  { id: 2, name: "Дмитрий Ким", photo: "👨‍🦰", rating: 4.8, categories: [1, 3, 6], exp: "7 лет" },
  { id: 3, name: "Жанна Сейткали", photo: "👩‍🦳", rating: 5.0, categories: [2, 4], exp: "3 года" },
  { id: 4, name: "Мадина Бекова", photo: "👩", rating: 4.7, categories: [3, 4, 5], exp: "4 года" },
];

const SERVICES_BY_CATEGORY = {
  1: [
    { id: 101, name: { ru: "Женская стрижка", kz: "Әйелдер шашы" }, price: 4500, duration: 60 },
    { id: 102, name: { ru: "Мужская стрижка", kz: "Ер шашы" }, price: 2500, duration: 40 },
    { id: 103, name: { ru: "Детская стрижка", kz: "Балалар шашы" }, price: 2000, duration: 30 },
  ],
  2: [
    { id: 201, name: { ru: "Маникюр классик", kz: "Классик маникюр" }, price: 3500, duration: 60 },
    { id: 202, name: { ru: "Гель-лак", kz: "Гель-лак" }, price: 5000, duration: 90 },
  ],
  3: [
    { id: 301, name: { ru: "Классический массаж", kz: "Классикалық массаж" }, price: 6000, duration: 60 },
    { id: 302, name: { ru: "Релакс массаж", kz: "Релакс массаж" }, price: 7500, duration: 90 },
  ],
  4: [
    { id: 401, name: { ru: "Чистка лица", kz: "Бет тазалау" }, price: 8000, duration: 60 },
    { id: 402, name: { ru: "Пилинг", kz: "Пилинг" }, price: 6500, duration: 45 },
  ],
  5: [
    { id: 501, name: { ru: "Окрашивание корней", kz: "Тамыр бояу" }, price: 5000, duration: 90 },
    { id: 502, name: { ru: "Полное окрашивание", kz: "Толық бояу" }, price: 9000, duration: 150 },
  ],
  6: [
    { id: 601, name: { ru: "Укладка", kz: "Үлгілеу" }, price: 3000, duration: 45 },
    { id: 602, name: { ru: "Вечерняя укладка", kz: "Кешкі үлгілеу" }, price: 4500, duration: 60 },
  ],
};

const SLOTS = ["09:00","09:30","10:00","10:30","11:00","11:30","12:00","12:30",
  "13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00"];
const BUSY = ["10:00","10:30","13:00","14:30","15:00","17:00"];

function getTodayStr() {
  return new Date().toISOString().slice(0,10);
}
function getTomorrowStr() {
  const d = new Date(); d.setDate(d.getDate()+1);
  return d.toISOString().slice(0,10);
}
function formatDate(str) {
  if (!str) return "";
  const d = new Date(str);
  return d.toLocaleDateString("ru-RU",{day:"numeric",month:"long"});
}

// ─── CSS ─────────────────────────────────────────────────────────────────────
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');
  
  :root {
    --bg: #0f0f0f;
    --bg2: #181818;
    --bg3: #222;
    --card: #1c1c1c;
    --gold: #c9a84c;
    --gold2: #e8c96a;
    --text: #f0ece4;
    --muted: #888;
    --border: #2e2e2e;
    --accent: #c9a84c22;
    --radius: 16px;
    --radius-sm: 10px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; }
  
  .app { max-width: 420px; margin: 0 auto; min-height: 100vh; background: var(--bg); position: relative; overflow-x: hidden; }
  
  /* Header */
  .header {
    background: linear-gradient(160deg, #1a1508 0%, #0f0f0f 60%);
    padding: 20px 16px 16px;
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
  }
  .header-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; }
  .header-greeting { font-family: 'DM Sans', sans-serif; font-size: 11px; color: var(--gold); text-transform: uppercase; letter-spacing: 1.5px; }
  .header-name { font-family: 'Cormorant Garamond', serif; font-size: 22px; font-weight: 700; color: var(--text); line-height: 1.2; }
  .header-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
  .icon-btn {
    width: 34px; height: 34px; border-radius: 50%; background: var(--bg3);
    border: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 15px; transition: all .2s; color: var(--text); flex-shrink: 0;
  }
  .icon-btn:hover { background: var(--accent); border-color: var(--gold); }
  .icon-btn.active { background: var(--gold); color: #000; border-color: var(--gold); }
  .lang-btn { font-size: 11px; font-weight: 600; letter-spacing: .5px; font-family: 'DM Sans', sans-serif; }
  
  /* Main content */
  .main { padding: 16px; padding-bottom: 80px; }
  
  /* Tabs */
  .tabs { display: flex; gap: 8px; margin-bottom: 16px; }
  .tab {
    flex: 1; padding: 12px 8px; border-radius: var(--radius-sm);
    background: var(--card); border: 1px solid var(--border);
    cursor: pointer; text-align: center; transition: all .2s;
    font-size: 13px; font-weight: 500; color: var(--muted);
  }
  .tab.active { background: var(--gold); color: #0f0f0f; border-color: var(--gold); font-weight: 600; }
  .tab-icon { font-size: 20px; display: block; margin-bottom: 4px; }
  
  /* Date selector */
  .date-bar { display: flex; gap: 6px; margin-bottom: 16px; }
  .date-chip {
    padding: 7px 14px; border-radius: 20px; background: var(--card);
    border: 1px solid var(--border); cursor: pointer; font-size: 12px;
    color: var(--muted); transition: all .2s; white-space: nowrap;
  }
  .date-chip.active { background: var(--gold); color: #0f0f0f; border-color: var(--gold); font-weight: 600; }
  .date-input {
    flex: 1; padding: 7px 10px; border-radius: 20px;
    background: var(--card); border: 1px solid var(--border);
    color: var(--text); font-size: 12px; font-family: 'DM Sans', sans-serif;
    cursor: pointer; min-width: 0;
  }
  .date-input::-webkit-calendar-picker-indicator { filter: invert(0.6) sepia(1) saturate(3) hue-rotate(10deg); }

  /* Section title */
  .section-title { font-family: 'Cormorant Garamond', serif; font-size: 18px; font-weight: 600; color: var(--text); margin-bottom: 12px; }

  /* Category grid */
  .cat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 8px; margin-bottom: 24px; }
  .cat-tile {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-sm);
    padding: 14px 8px; text-align: center; cursor: pointer; transition: all .2s;
  }
  .cat-tile:hover { border-color: var(--gold); background: var(--accent); }
  .cat-tile-icon { font-size: 24px; margin-bottom: 6px; }
  .cat-tile-name { font-size: 11px; color: var(--muted); line-height: 1.3; }
  
  /* Services list */
  .service-list { display: flex; flex-direction: column; gap: 8px; }
  .service-card {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-sm);
    padding: 14px; cursor: pointer; transition: all .2s; display: flex; justify-content: space-between; align-items: center;
  }
  .service-card:hover { border-color: var(--gold); }
  .service-card.selected { border-color: var(--gold); background: var(--accent); }
  .service-name { font-size: 14px; font-weight: 500; margin-bottom: 3px; }
  .service-meta { font-size: 11px; color: var(--muted); }
  .service-price { font-family: 'Cormorant Garamond', serif; font-size: 18px; font-weight: 700; color: var(--gold); }

  /* Master grid */
  .master-grid { display: flex; flex-direction: column; gap: 10px; }
  .master-card {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 14px; display: flex; align-items: center; gap: 14px; cursor: pointer; transition: all .2s;
  }
  .master-card:hover { border-color: var(--gold); }
  .master-photo { width: 56px; height: 56px; border-radius: 50%; background: var(--bg3); display: flex; align-items: center; justify-content: center; font-size: 30px; flex-shrink: 0; border: 2px solid var(--border); }
  .master-info { flex: 1; min-width: 0; }
  .master-name { font-size: 14px; font-weight: 500; margin-bottom: 3px; }
  .master-meta { font-size: 11px; color: var(--muted); }
  .master-rating { font-size: 11px; color: var(--gold); }
  .master-actions { display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; }
  .btn-sm {
    padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500;
    cursor: pointer; border: 1px solid; transition: all .2s; white-space: nowrap;
    font-family: 'DM Sans', sans-serif;
  }
  .btn-gold { background: var(--gold); color: #0f0f0f; border-color: var(--gold); }
  .btn-ghost { background: transparent; color: var(--text); border-color: var(--border); }
  .btn-ghost:hover { border-color: var(--gold); color: var(--gold); }

  /* Category filter pills */
  .filter-pills { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 4px; margin-bottom: 14px; scrollbar-width: none; }
  .filter-pills::-webkit-scrollbar { display: none; }
  .pill {
    padding: 5px 12px; border-radius: 20px; background: var(--card);
    border: 1px solid var(--border); cursor: pointer; font-size: 11px;
    color: var(--muted); white-space: nowrap; transition: all .2s; flex-shrink: 0;
  }
  .pill.active { background: var(--gold); color: #0f0f0f; border-color: var(--gold); font-weight: 600; }

  /* Slot grid */
  .slot-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; margin-bottom: 20px; }
  .slot {
    padding: 10px 0; border-radius: var(--radius-sm); text-align: center;
    font-size: 13px; cursor: pointer; border: 1px solid var(--border);
    background: var(--card); transition: all .2s; font-family: 'DM Sans', sans-serif;
  }
  .slot.busy { background: var(--bg3); color: #555; cursor: not-allowed; border-color: var(--bg3); text-decoration: line-through; }
  .slot.selected { background: var(--gold); color: #0f0f0f; border-color: var(--gold); font-weight: 600; }
  .slot:not(.busy):not(.selected):hover { border-color: var(--gold); color: var(--gold); }

  /* Modal */
  .modal-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,.8); z-index: 200;
    display: flex; align-items: flex-end; justify-content: center;
    animation: fadeIn .2s ease;
  }
  .modal {
    background: var(--bg2); border-radius: 24px 24px 0 0; width: 100%; max-width: 420px;
    padding: 24px 20px 32px; border-top: 1px solid var(--border);
    animation: slideUp .25s ease;
  }
  @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
  @keyframes slideUp { from { transform: translateY(40px); opacity: 0 } to { transform: translateY(0); opacity: 1 } }
  .modal-title { font-family: 'Cormorant Garamond', serif; font-size: 22px; font-weight: 700; margin-bottom: 20px; text-align: center; }
  .modal-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
  .modal-row:last-of-type { border-bottom: none; }
  .modal-label { color: var(--muted); }
  .modal-value { font-weight: 500; text-align: right; }
  .modal-value.gold { color: var(--gold); font-family: 'Cormorant Garamond', serif; font-size: 17px; }
  .btn-confirm {
    width: 100%; margin-top: 20px; padding: 15px; border-radius: var(--radius-sm);
    background: var(--gold); color: #0f0f0f; border: none; font-size: 15px;
    font-weight: 600; cursor: pointer; font-family: 'DM Sans', sans-serif;
    transition: all .2s;
  }
  .btn-confirm:hover { background: var(--gold2); }
  
  /* Page header */
  .page-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
  .back-btn { width: 34px; height: 34px; border-radius: 50%; background: var(--card); border: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; transition: all .2s; }
  .back-btn:hover { border-color: var(--gold); }
  .page-title { font-family: 'Cormorant Garamond', serif; font-size: 20px; font-weight: 700; }
  
  /* Master detail card */
  .master-detail-header { display: flex; gap: 16px; align-items: center; background: var(--card); border-radius: var(--radius); padding: 16px; margin-bottom: 16px; border: 1px solid var(--border); }
  .master-detail-photo { width: 72px; height: 72px; border-radius: 50%; background: var(--bg3); display: flex; align-items: center; justify-content: center; font-size: 40px; border: 2px solid var(--gold); flex-shrink: 0; }
  
  /* Success screen */
  .success { text-align: center; padding: 40px 20px; }
  .success-icon { font-size: 60px; margin-bottom: 16px; }
  .success-title { font-family: 'Cormorant Garamond', serif; font-size: 28px; font-weight: 700; margin-bottom: 8px; color: var(--gold); }
  .success-sub { font-size: 14px; color: var(--muted); }
  
  /* Gold divider */
  .gold-line { height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); margin: 16px 0; opacity: .4; }
  
  .empty { text-align: center; padding: 30px; color: var(--muted); font-size: 13px; }
`;

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [lang, setLang] = useState("ru");
  const [page, setPage] = useState("home"); // home | services-flow | masters-flow | master-detail | slots | master-slots
  const [activeTab, setActiveTab] = useState("services"); // services | masters
  const [selectedDate, setSelectedDate] = useState(getTodayStr());
  const [selectedCat, setSelectedCat] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  const [selectedMaster, setSelectedMaster] = useState(null);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [masterFilter, setMasterFilter] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showMasterDetail, setShowMasterDetail] = useState(null);
  const [showSuccess, setShowSuccess] = useState(false);

  const t = (obj) => (typeof obj === "object" ? obj[lang] : obj);

  // ── Navigation helpers ──────────────────────────────────────────────────
  const goHome = () => {
    setPage("home"); setSelectedCat(null); setSelectedService(null);
    setSelectedMaster(null); setSelectedSlot(null); setShowSuccess(false);
  };

  const handleCatClick = (cat) => {
    setSelectedCat(cat); setPage("service-list");
  };

  const handleServiceSelect = (svc) => {
    setSelectedService(svc); setPage("master-select");
  };

  const handleMasterSelect = (master) => {
    setSelectedMaster(master); setPage("slots");
  };

  const handleSlotSelect = (slot) => {
    if (BUSY.includes(slot)) return;
    setSelectedSlot(slot); setShowModal(true);
  };

  const handleConfirm = () => {
    setShowModal(false); setShowSuccess(true);
    setTimeout(() => { goHome(); }, 2500);
  };

  // ── Masters-first flow ────────────────────────────────────────────────
  const handleMasterFirstSelect = (master) => {
    setSelectedMaster(master); setPage("master-services");
  };

  const handleMasterServiceSelect = (svc) => {
    setSelectedService(svc); setPage("master-slots");
  };

  // ── Render ────────────────────────────────────────────────────────────
  const allServices = Object.values(SERVICES_BY_CATEGORY).flat();
  const catServices = selectedCat ? SERVICES_BY_CATEGORY[selectedCat.id] || [] : [];
  const catMasters = selectedCat
    ? MASTERS.filter(m => m.categories.includes(selectedCat.id))
    : MASTERS;
  const masterServices = selectedMaster
    ? Object.entries(SERVICES_BY_CATEGORY)
        .filter(([catId]) => selectedMaster.categories.includes(Number(catId)))
        .flatMap(([, svcs]) => svcs)
    : [];
  const filteredMasters = masterFilter
    ? MASTERS.filter(m => m.categories.includes(masterFilter))
    : MASTERS;

  return (
    <>
      <style>{css}</style>
      <div className="app">
        {/* ── Header ── */}
        <div className="header">
          <div className="header-top">
            <div>
              <div className="header-greeting">{ORG.greeting}</div>
              <div className="header-name">{ORG.name}</div>
            </div>
            <div className="header-actions">
              <button className="icon-btn lang-btn" onClick={() => setLang(l => l === "ru" ? "kz" : "ru")}>
                {lang === "ru" ? "ҚЗ" : "РУ"}
              </button>
              <button className="icon-btn" onClick={() => window.open(ORG.instagram, "_blank")} title="Instagram">
                📷
              </button>
            </div>
          </div>
        </div>

        {/* ── Main ── */}
        <div className="main">

          {/* ══ HOME PAGE ══ */}
          {page === "home" && !showSuccess && (
            <>
              {/* Tabs */}
              <div className="tabs">
                <div className={`tab ${activeTab === "services" ? "active" : ""}`} onClick={() => setActiveTab("services")}>
                  <span className="tab-icon">✨</span>
                  {lang === "ru" ? "Услуги" : "Қызметтер"}
                </div>
                <div className={`tab ${activeTab === "masters" ? "active" : ""}`} onClick={() => setActiveTab("masters")}>
                  <span className="tab-icon">👤</span>
                  {lang === "ru" ? "Мастера" : "Шеберлер"}
                </div>
              </div>

              {/* Date bar */}
              <div className="date-bar">
                <div className={`date-chip ${selectedDate === getTodayStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTodayStr())}>
                  {lang === "ru" ? "Сегодня" : "Бүгін"}
                </div>
                <div className={`date-chip ${selectedDate === getTomorrowStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTomorrowStr())}>
                  {lang === "ru" ? "Завтра" : "Ертең"}
                </div>
                <input type="date" className="date-input" value={selectedDate} min={getTodayStr()}
                  onChange={e => setSelectedDate(e.target.value)} />
              </div>

              {/* Services tab */}
              {activeTab === "services" && (
                <>
                  <div className="section-title">
                    {lang === "ru" ? "Категории услуг" : "Қызмет санаттары"}
                  </div>
                  <div className="cat-grid">
                    {CATEGORIES.map(cat => (
                      <div key={cat.id} className="cat-tile" onClick={() => handleCatClick(cat)}>
                        <div className="cat-tile-icon">{cat.icon}</div>
                        <div className="cat-tile-name">{t(cat.name)}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {/* Masters tab */}
              {activeTab === "masters" && (
                <>
                  <div className="filter-pills">
                    <div className={`pill ${!masterFilter ? "active" : ""}`} onClick={() => setMasterFilter(null)}>
                      {lang === "ru" ? "Все" : "Барлық"}
                    </div>
                    {CATEGORIES.map(cat => (
                      <div key={cat.id} className={`pill ${masterFilter === cat.id ? "active" : ""}`} onClick={() => setMasterFilter(cat.id)}>
                        {cat.icon} {t(cat.name)}
                      </div>
                    ))}
                  </div>
                  <div className="master-grid">
                    {filteredMasters.map(m => (
                      <div key={m.id} className="master-card">
                        <div className="master-photo">{m.photo}</div>
                        <div className="master-info">
                          <div className="master-name">{m.name}</div>
                          <div className="master-rating">★ {m.rating} · {m.exp}</div>
                        </div>
                        <div className="master-actions">
                          <button className="btn-sm btn-gold" onClick={() => handleMasterFirstSelect(m)}>
                            {lang === "ru" ? "Выбрать" : "Таңдау"}
                          </button>
                          <button className="btn-sm btn-ghost" onClick={() => setShowMasterDetail(m)}>
                            {lang === "ru" ? "Подробнее" : "Толығырақ"}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}

          {/* ══ SUCCESS ══ */}
          {showSuccess && (
            <div className="success">
              <div className="success-icon">✅</div>
              <div className="success-title">{lang === "ru" ? "Запись подтверждена!" : "Жазылу расталды!"}</div>
              <div className="success-sub">{lang === "ru" ? "Ждём вас!" : "Сізді күтеміз!"}</div>
            </div>
          )}

          {/* ══ SERVICE LIST (category → services) ══ */}
          {page === "service-list" && (
            <>
              <div className="page-header">
                <button className="back-btn" onClick={goHome}>←</button>
                <div className="page-title">{selectedCat && t(selectedCat.name)}</div>
              </div>
              <div className="service-list">
                {catServices.map(svc => (
                  <div key={svc.id} className="service-card" onClick={() => handleServiceSelect(svc)}>
                    <div>
                      <div className="service-name">{t(svc.name)}</div>
                      <div className="service-meta">⏱ {svc.duration} {lang === "ru" ? "мин" : "мин"}</div>
                    </div>
                    <div className="service-price">{svc.price.toLocaleString()} ₸</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* ══ MASTER SELECT (after service chosen) ══ */}
          {page === "master-select" && (
            <>
              <div className="page-header">
                <button className="back-btn" onClick={() => setPage("service-list")}>←</button>
                <div className="page-title">{lang === "ru" ? "Выберите мастера" : "Шебер таңдаңыз"}</div>
              </div>
              {selectedService && (
                <div style={{ background:"var(--accent)", border:"1px solid var(--gold)", borderRadius:"var(--radius-sm)", padding:"10px 14px", marginBottom:14, fontSize:13 }}>
                  <span style={{color:"var(--gold)"}}>✨ {t(selectedService.name)}</span>
                  <span style={{color:"var(--muted)", marginLeft:8}}>{selectedService.price.toLocaleString()} ₸</span>
                </div>
              )}
              <div className="master-grid">
                {catMasters.map(m => (
                  <div key={m.id} className="master-card">
                    <div className="master-photo">{m.photo}</div>
                    <div className="master-info">
                      <div className="master-name">{m.name}</div>
                      <div className="master-rating">★ {m.rating}</div>
                    </div>
                    <button className="btn-sm btn-gold" onClick={() => handleMasterSelect(m)}>
                      {lang === "ru" ? "Выбрать" : "Таңдау"}
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* ══ SLOTS (service→master→slots) ══ */}
          {page === "slots" && (
            <>
              <div className="page-header">
                <button className="back-btn" onClick={() => setPage("master-select")}>←</button>
                <div className="page-title">{lang === "ru" ? "Выберите время" : "Уақыт таңдаңыз"}</div>
              </div>
              {selectedMaster && (
                <div className="master-detail-header" style={{marginBottom:14}}>
                  <div className="master-photo" style={{width:44,height:44,fontSize:24}}>{selectedMaster.photo}</div>
                  <div>
                    <div className="master-name">{selectedMaster.name}</div>
                    <div className="master-rating">★ {selectedMaster.rating}</div>
                  </div>
                </div>
              )}
              <div className="date-bar" style={{marginBottom:14}}>
                <div className={`date-chip ${selectedDate === getTodayStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTodayStr())}>
                  {lang === "ru" ? "Сегодня" : "Бүгін"}
                </div>
                <div className={`date-chip ${selectedDate === getTomorrowStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTomorrowStr())}>
                  {lang === "ru" ? "Завтра" : "Ертең"}
                </div>
                <input type="date" className="date-input" value={selectedDate} min={getTodayStr()} onChange={e => setSelectedDate(e.target.value)} />
              </div>
              <div style={{fontSize:12, color:"var(--muted)", marginBottom:10}}>
                <span style={{display:"inline-block",width:12,height:12,background:"var(--bg3)",borderRadius:3,marginRight:5,verticalAlign:"middle"}}></span>
                {lang === "ru" ? "Занято" : "Бос емес"}
                <span style={{display:"inline-block",width:12,height:12,background:"var(--gold)",borderRadius:3,marginLeft:12,marginRight:5,verticalAlign:"middle"}}></span>
                {lang === "ru" ? "Выбрано" : "Таңдалған"}
              </div>
              <div className="slot-grid">
                {SLOTS.map(s => (
                  <div key={s} className={`slot ${BUSY.includes(s) ? "busy" : ""} ${selectedSlot === s ? "selected" : ""}`}
                    onClick={() => handleSlotSelect(s)}>{s}</div>
                ))}
              </div>
            </>
          )}

          {/* ══ MASTER SERVICES (master→services) ══ */}
          {page === "master-services" && (
            <>
              <div className="page-header">
                <button className="back-btn" onClick={() => setPage("home")}>←</button>
                <div className="page-title">{lang === "ru" ? "Выберите услугу" : "Қызмет таңдаңыз"}</div>
              </div>
              {selectedMaster && (
                <div className="master-detail-header">
                  <div className="master-detail-photo">{selectedMaster.photo}</div>
                  <div>
                    <div className="master-name" style={{fontSize:16}}>{selectedMaster.name}</div>
                    <div className="master-rating">★ {selectedMaster.rating} · {selectedMaster.exp}</div>
                  </div>
                </div>
              )}
              <div className="date-bar" style={{marginBottom:14}}>
                <div className={`date-chip ${selectedDate === getTodayStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTodayStr())}>
                  {lang === "ru" ? "Сегодня" : "Бүгін"}
                </div>
                <div className={`date-chip ${selectedDate === getTomorrowStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTomorrowStr())}>
                  {lang === "ru" ? "Завтра" : "Ертең"}
                </div>
                <input type="date" className="date-input" value={selectedDate} min={getTodayStr()} onChange={e => setSelectedDate(e.target.value)} />
              </div>
              <div className="service-list">
                {masterServices.map(svc => (
                  <div key={svc.id} className="service-card" onClick={() => handleMasterServiceSelect(svc)}>
                    <div>
                      <div className="service-name">{t(svc.name)}</div>
                      <div className="service-meta">⏱ {svc.duration} мин</div>
                    </div>
                    <div className="service-price">{svc.price.toLocaleString()} ₸</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* ══ MASTER SLOTS (master→service→slots) ══ */}
          {page === "master-slots" && (
            <>
              <div className="page-header">
                <button className="back-btn" onClick={() => setPage("master-services")}>←</button>
                <div className="page-title">{lang === "ru" ? "Выберите время" : "Уақыт таңдаңыз"}</div>
              </div>
              {selectedService && (
                <div style={{background:"var(--accent)", border:"1px solid var(--gold)", borderRadius:"var(--radius-sm)", padding:"10px 14px", marginBottom:14, fontSize:13}}>
                  <span style={{color:"var(--gold)"}}>✨ {t(selectedService.name)}</span>
                  <span style={{color:"var(--muted)", marginLeft:8}}>{selectedService.price.toLocaleString()} ₸</span>
                </div>
              )}
              <div className="date-bar" style={{marginBottom:14}}>
                <div className={`date-chip ${selectedDate === getTodayStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTodayStr())}>
                  {lang === "ru" ? "Сегодня" : "Бүгін"}
                </div>
                <div className={`date-chip ${selectedDate === getTomorrowStr() ? "active" : ""}`} onClick={() => setSelectedDate(getTomorrowStr())}>
                  {lang === "ru" ? "Завтра" : "Ертең"}
                </div>
                <input type="date" className="date-input" value={selectedDate} min={getTodayStr()} onChange={e => setSelectedDate(e.target.value)} />
              </div>
              <div style={{fontSize:12, color:"var(--muted)", marginBottom:10}}>
                <span style={{display:"inline-block",width:12,height:12,background:"var(--bg3)",borderRadius:3,marginRight:5,verticalAlign:"middle"}}></span>
                {lang === "ru" ? "Занято" : "Бос емес"}
              </div>
              <div className="slot-grid">
                {SLOTS.map(s => (
                  <div key={s} className={`slot ${BUSY.includes(s) ? "busy" : ""} ${selectedSlot === s ? "selected" : ""}`}
                    onClick={() => { if(!BUSY.includes(s)) { setSelectedSlot(s); setShowModal(true); } }}>{s}</div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* ══ MASTER DETAIL MODAL ══ */}
        {showMasterDetail && (
          <div className="modal-overlay" onClick={() => setShowMasterDetail(null)}>
            <div className="modal" onClick={e => e.stopPropagation()}>
              <div style={{textAlign:"center", marginBottom:16}}>
                <div style={{fontSize:64, marginBottom:8}}>{showMasterDetail.photo}</div>
                <div className="modal-title" style={{marginBottom:4}}>{showMasterDetail.name}</div>
                <div style={{color:"var(--gold)", fontSize:13}}>★ {showMasterDetail.rating} · {showMasterDetail.exp}</div>
              </div>
              <div className="gold-line" />
              <div style={{fontSize:13, color:"var(--muted)", marginBottom:12}}>{lang === "ru" ? "Специализации:" : "Мамандықтары:"}</div>
              <div className="filter-pills" style={{flexWrap:"wrap"}}>
                {showMasterDetail.categories.map(cid => {
                  const cat = CATEGORIES.find(c => c.id === cid);
                  return cat ? <div key={cid} className="pill active">{cat.icon} {t(cat.name)}</div> : null;
                })}
              </div>
              <button className="btn-confirm" onClick={() => { setShowMasterDetail(null); handleMasterFirstSelect(showMasterDetail); }}>
                {lang === "ru" ? "Записаться к этому мастеру" : "Осы шеберге жазылу"}
              </button>
            </div>
          </div>
        )}

        {/* ══ CONFIRMATION MODAL ══ */}
        {showModal && selectedService && selectedMaster && selectedSlot && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-title">{lang === "ru" ? "Подтверждение записи" : "Жазылуды растау"}</div>
              <div className="modal-row">
                <span className="modal-label">{lang === "ru" ? "Услуга" : "Қызмет"}</span>
                <span className="modal-value">{t(selectedService.name)}</span>
              </div>
              <div className="modal-row">
                <span className="modal-label">{lang === "ru" ? "Мастер" : "Шебер"}</span>
                <span className="modal-value">{selectedMaster.name}</span>
              </div>
              <div className="modal-row">
                <span className="modal-label">{lang === "ru" ? "Дата" : "Күн"}</span>
                <span className="modal-value">{formatDate(selectedDate)}</span>
              </div>
              <div className="modal-row">
                <span className="modal-label">{lang === "ru" ? "Время" : "Уақыт"}</span>
                <span className="modal-value">{selectedSlot}</span>
              </div>
              <div className="modal-row">
                <span className="modal-label">{lang === "ru" ? "Стоимость" : "Баға"}</span>
                <span className="modal-value gold">{selectedService.price.toLocaleString()} ₸</span>
              </div>
              <button className="btn-confirm" onClick={handleConfirm}>
                {lang === "ru" ? "✓ Подтвердить запись" : "✓ Жазылуды растау"}
              </button>
              <button className="btn-sm btn-ghost" style={{width:"100%", marginTop:8, padding:"10px", textAlign:"center", borderRadius:"var(--radius-sm)"}} onClick={() => setShowModal(false)}>
                {lang === "ru" ? "Отмена" : "Болдырмау"}
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
