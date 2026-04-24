import { useState, useRef, useEffect } from "react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";

// ─── Mock Data ────────────────────────────────────────────────────────────────
const ORG = { name: "Студия красоты Lumière", greeting: "Панель мастера", lat: 51.1801, lng: 71.4460 };

const MASTER = {
  id: 1, name: "Аида", surname: "Нурланова",
  phone: "+7 701 234 56 78", bio: "Профессиональный стилист с 5-летним стажем. Специализируюсь на женских стрижках и окрашивании.",
  photo: null, rating: 4.9, completedToday: 3,
};

function getWeekRange(offset = 0) {
  const now = new Date();
  const day = now.getDay() || 7;
  const mon = new Date(now); mon.setDate(now.getDate() - day + 1 + offset * 7);
  const sun = new Date(mon); sun.setDate(mon.getDate() + 6);
  return { start: mon.toISOString().slice(0,10), end: sun.toISOString().slice(0,10) };
}
function getMonthRange(offset = 0) {
  const now = new Date();
  const y = now.getFullYear(), m = now.getMonth() + offset;
  const start = new Date(y, m, 1).toISOString().slice(0,10);
  const end = new Date(y, m + 1, 0).toISOString().slice(0,10);
  return { start, end };
}

const PERIODS = [
  { id: "this_week", label: "Текущая неделя", range: () => getWeekRange(0) },
  { id: "last_week", label: "Прошлая неделя", range: () => getWeekRange(-1) },
  { id: "this_month", label: "Текущий месяц", range: () => getMonthRange(0) },
  { id: "last_month", label: "Прошлый месяц", range: () => getMonthRange(-1) },
];

function genWeekData() {
  const days = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"];
  return days.map((d,i) => ({ day: d, income: Math.round((2000 + Math.random()*12000) / 100)*100, clients: Math.floor(1+Math.random()*6) }));
}
function genMonthData() {
  return Array.from({length:4},(_,i)=>({ week:`Нед ${i+1}`, income: Math.round((15000+Math.random()*40000)/100)*100, clients: Math.floor(8+Math.random()*20) }));
}

const SERVICES_INCOME = [
  { name: "Стрижки", amount: 28500, count: 9, color: "#c9a84c" },
  { name: "Окрашивание", amount: 45000, count: 5, color: "#e8c96a" },
  { name: "Укладка", amount: 12000, count: 4, color: "#a07830" },
  { name: "Маникюр", amount: 17500, count: 5, color: "#d4b060" },
];

// ─── Styles ───────────────────────────────────────────────────────────────────
const css = `
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Mulish:wght@300;400;500;600&display=swap');
:root {
  --bg:#0a0a0f; --bg2:#111118; --bg3:#18181f; --card:#1a1a22;
  --gold:#c9a84c; --gold2:#e8c96a; --gold3:#a07830;
  --text:#eeeaf0; --muted:#6b6b7a; --border:#252530;
  --green:#4caf7d; --red:#e05252;
  --r:14px; --rs:10px;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:'Mulish',sans-serif;-webkit-font-smoothing:antialiased;}
.app{max-width:420px;margin:0 auto;min-height:100vh;background:var(--bg);overflow-x:hidden;}

/* Header */
.hdr{
  background:linear-gradient(135deg,#12100a 0%,#0a0a0f 70%);
  padding:20px 16px 16px; border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:100;
}
.hdr-row{display:flex;align-items:center;justify-content:space-between;}
.hdr-left{display:flex;align-items:center;gap:12px;}
.avatar{width:42px;height:42px;border-radius:50%;background:var(--bg3);border:2px solid var(--gold);display:flex;align-items:center;justify-content:center;font-size:18px;overflow:hidden;flex-shrink:0;}
.avatar img{width:100%;height:100%;object-fit:cover;}
.hdr-sub{font-size:10px;color:var(--gold);text-transform:uppercase;letter-spacing:1.5px;font-weight:600;}
.hdr-name{font-family:'Playfair Display',serif;font-size:17px;font-weight:700;line-height:1.2;}
.status-dot{width:8px;height:8px;border-radius:50%;background:var(--muted);display:inline-block;margin-right:5px;transition:background .3s;}
.status-dot.open{background:var(--green);box-shadow:0 0 6px var(--green);}
.hdr-status{font-size:11px;color:var(--muted);margin-top:2px;}
.hdr-status.open{color:var(--green);}

/* Main */
.main{padding:16px;padding-bottom:80px;}

/* Tiles grid */
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:0;}
.tile{
  background:var(--card);border:1px solid var(--border);border-radius:var(--r);
  padding:18px 16px;cursor:pointer;transition:all .22s;position:relative;overflow:hidden;
}
.tile::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,var(--gold)08,transparent 60%);opacity:0;transition:opacity .22s;}
.tile:hover{border-color:var(--gold);transform:translateY(-1px);}
.tile:hover::before{opacity:1;}
.tile:active{transform:scale(.98);}
.tile-icon{font-size:28px;margin-bottom:10px;}
.tile-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:4px;}
.tile-value{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:var(--text);}
.tile-value.gold{color:var(--gold);}
.tile-arrow{position:absolute;bottom:14px;right:14px;color:var(--border);font-size:18px;transition:color .2s;}
.tile:hover .tile-arrow{color:var(--gold);}

/* Page header */
.phdr{display:flex;align-items:center;gap:10px;margin-bottom:20px;}
.back{width:36px;height:36px;border-radius:50%;background:var(--card);border:1px solid var(--border);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;transition:all .2s;}
.back:hover{border-color:var(--gold);}
.ptitle{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;}

/* Profile */
.photo-upload{display:flex;flex-direction:column;align-items:center;margin-bottom:24px;}
.pu-circle{
  width:90px;height:90px;border-radius:50%;border:2px dashed var(--gold);
  background:var(--card);display:flex;align-items:center;justify-content:center;
  cursor:pointer;overflow:hidden;font-size:36px;transition:all .2s;margin-bottom:10px;
}
.pu-circle:hover{background:var(--bg3);border-color:var(--gold2);}
.pu-circle img{width:100%;height:100%;object-fit:cover;}
.pu-hint{font-size:11px;color:var(--muted);}
.field{margin-bottom:14px;}
.field label{display:block;font-size:11px;color:var(--gold);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:6px;}
.field input,.field textarea{
  width:100%;background:var(--card);border:1px solid var(--border);
  border-radius:var(--rs);padding:11px 14px;color:var(--text);
  font-family:'Mulish',sans-serif;font-size:14px;outline:none;transition:border .2s;resize:none;
}
.field input:focus,.field textarea:focus{border-color:var(--gold);}
.btn-save{
  width:100%;padding:14px;border-radius:var(--rs);background:var(--gold);color:#0a0a0f;
  border:none;font-size:14px;font-weight:700;cursor:pointer;font-family:'Mulish',sans-serif;
  letter-spacing:.5px;transition:all .2s;
}
.btn-save:hover{background:var(--gold2);}

/* Shift modal */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:200;display:flex;align-items:flex-end;justify-content:center;animation:fi .2s;}
.sheet{background:var(--bg2);border-radius:24px 24px 0 0;width:100%;max-width:420px;padding:28px 20px 36px;border-top:1px solid var(--border);animation:su .25s;}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes su{from{transform:translateY(40px);opacity:0}to{transform:translateY(0);opacity:1}}
.sheet-icon{font-size:52px;text-align:center;margin-bottom:14px;}
.sheet-title{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;text-align:center;margin-bottom:8px;}
.sheet-sub{font-size:13px;color:var(--muted);text-align:center;line-height:1.6;padding:0 10px;}
.sheet-sub.success{color:var(--green);}
.btn-sheet{width:100%;margin-top:22px;padding:14px;border-radius:var(--rs);background:var(--gold);color:#0a0a0f;border:none;font-size:14px;font-weight:700;cursor:pointer;font-family:'Mulish',sans-serif;transition:all .2s;}
.btn-sheet:hover{background:var(--gold2);}
.btn-sheet-ghost{background:transparent;color:var(--muted);border:1px solid var(--border);margin-top:8px;}
.btn-sheet-ghost:hover{border-color:var(--border);color:var(--text);}
.loading-spin{display:inline-block;width:22px;height:22px;border:2px solid var(--border);border-top-color:var(--gold);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 12px;display:block;}
@keyframes spin{to{transform:rotate(360deg)}}

/* Income dashboard */
.period-select{
  width:100%;background:var(--card);border:1px solid var(--border);border-radius:var(--rs);
  padding:11px 14px;color:var(--text);font-family:'Mulish',sans-serif;font-size:13px;
  outline:none;cursor:pointer;margin-bottom:16px;appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' fill='none'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%236b6b7a' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 14px center;padding-right:36px;
}
.date-range-row{display:flex;gap:8px;margin-bottom:20px;}
.date-range-row input{flex:1;background:var(--card);border:1px solid var(--border);border-radius:var(--rs);padding:9px 12px;color:var(--text);font-family:'Mulish',sans-serif;font-size:12px;outline:none;}
.date-range-row input:focus{border-color:var(--gold);}
.date-range-row input::-webkit-calendar-picker-indicator{filter:invert(.4);}
.date-range-label{font-size:10px;color:var(--muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:.8px;}

/* KPI Cards */
.kpi-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:20px;}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:var(--rs);padding:14px;}
.kpi-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}
.kpi-val{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:var(--text);}
.kpi-val.gold{color:var(--gold);}
.kpi-change{font-size:11px;margin-top:4px;}
.kpi-change.up{color:var(--green);}
.kpi-change.down{color:var(--red);}

/* Chart block */
.chart-block{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:16px;margin-bottom:14px;}
.chart-title{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;font-weight:600;}

/* Services table */
.svc-row{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border);}
.svc-row:last-child{border-bottom:none;}
.svc-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.svc-name{flex:1;font-size:13px;}
.svc-count{font-size:12px;color:var(--muted);width:30px;text-align:center;}
.svc-amount{font-family:'Playfair Display',serif;font-size:15px;color:var(--gold);}
.svc-bar-wrap{height:3px;background:var(--border);border-radius:2px;margin-top:4px;}
.svc-bar{height:3px;border-radius:2px;background:var(--gold);transition:width .6s;}

/* Tooltip custom */
.ct{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:8px!important;font-family:'Mulish',sans-serif!important;font-size:12px!important;}

.gold-line{height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:16px 0;opacity:.3;}
.section-title{font-family:'Playfair Display',serif;font-size:17px;font-weight:700;margin-bottom:12px;}
`;

// ─── Custom Tooltip ───────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div style={{ background: "#111118", border: "1px solid #252530", borderRadius: 8, padding: "8px 12px", fontSize: 12, fontFamily: "Mulish" }}>
        <div style={{ color: "#6b6b7a", marginBottom: 4 }}>{label}</div>
        {payload.map((p, i) => (
          <div key={i} style={{ color: p.color || "#c9a84c", fontWeight: 600 }}>
            {p.name === "income" ? `${p.value.toLocaleString()} ₸` : `${p.value} клиентов`}
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [page, setPage] = useState("home");
  const [shiftOpen, setShiftOpen] = useState(false);
  const [shiftTime, setShiftTime] = useState(null);
  const [shiftModal, setShiftModal] = useState(null); // null | "loading" | "success" | "fail"
  const [masterData, setMasterData] = useState({ ...MASTER });
  const [photoPreview, setPhotoPreview] = useState(null);
  const fileRef = useRef();

  // Income state
  const [periodId, setPeriodId] = useState("this_week");
  const [customStart, setCustomStart] = useState(getWeekRange(0).start);
  const [customEnd, setCustomEnd] = useState(getWeekRange(0).end);
  const [chartData, setChartData] = useState(genWeekData());

  useEffect(() => {
    const p = PERIODS.find(x => x.id === periodId);
    if (p) { const r = p.range(); setCustomStart(r.start); setCustomEnd(r.end); }
    setChartData(periodId.includes("month") ? genMonthData() : genWeekData());
  }, [periodId]);

  const totalIncome = chartData.reduce((s, d) => s + d.income, 0);
  const totalClients = chartData.reduce((s, d) => s + d.clients, 0);
  const avgCheck = totalClients ? Math.round(totalIncome / totalClients) : 0;
  const maxIncome = Math.max(...chartData.map(d => d.income));

  // ── Shift logic ────────────────────────────────────────────────────────
  const handleOpenShift = () => {
    setShiftModal("loading");
    if (!navigator.geolocation) { setTimeout(() => setShiftModal("fail"), 1200); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const dist = getDistance(pos.coords.latitude, pos.coords.longitude, ORG.lat, ORG.lng);
        setTimeout(() => {
          if (dist <= 50) {
            const now = new Date();
            const time = now.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
            setShiftTime(time); setShiftOpen(true); setShiftModal("success");
          } else {
            setShiftModal("fail");
          }
        }, 1200);
      },
      () => setTimeout(() => setShiftModal("fail"), 1200),
      { timeout: 8000 }
    );
  };

  function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000, rad = Math.PI / 180;
    const dLat = (lat2 - lat1) * rad, dLon = (lon2 - lon1) * rad;
    const a = Math.sin(dLat/2)**2 + Math.cos(lat1*rad)*Math.cos(lat2*rad)*Math.sin(dLon/2)**2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  }

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) { const url = URL.createObjectURL(file); setPhotoPreview(url); }
  };

  return (
    <>
      <style>{css}</style>
      <div className="app">

        {/* ── Header ── */}
        <div className="hdr">
          <div className="hdr-row">
            <div className="hdr-left">
              <div className="avatar" onClick={() => page !== "profile" && setPage("profile")} style={{ cursor: "pointer" }}>
                {photoPreview ? <img src={photoPreview} alt="" /> : "👩‍🦱"}
              </div>
              <div>
                <div className="hdr-sub">{ORG.greeting}</div>
                <div className="hdr-name">{masterData.name} {masterData.surname}</div>
                <div className={`hdr-status ${shiftOpen ? "open" : ""}`}>
                  <span className={`status-dot ${shiftOpen ? "open" : ""}`} />
                  {shiftOpen ? `Смена открыта · ${shiftTime}` : "Смена закрыта"}
                </div>
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: 1 }}>{ORG.name}</div>
              <div style={{ fontSize: 11, color: "var(--gold)", marginTop: 2 }}>★ {masterData.rating}</div>
            </div>
          </div>
        </div>

        <div className="main">

          {/* ══ HOME ══ */}
          {page === "home" && (
            <>
              <div style={{ marginBottom: 20 }}>
                <div className="gold-line" style={{ margin: "0 0 16px" }} />
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>

                  {/* Profile tile */}
                  <div className="tile" onClick={() => setPage("profile")}>
                    <div className="tile-icon">👤</div>
                    <div className="tile-label">Профиль</div>
                    <div className="tile-value">{masterData.name}</div>
                    <span className="tile-arrow">›</span>
                  </div>

                  {/* Shift tile */}
                  <div className="tile" onClick={shiftOpen ? undefined : handleOpenShift}
                    style={shiftOpen ? { borderColor: "var(--green)", cursor: "default" } : {}}>
                    <div className="tile-icon">{shiftOpen ? "🟢" : "⏱"}</div>
                    <div className="tile-label">{shiftOpen ? "Смена" : "Открыть смену"}</div>
                    <div className="tile-value" style={shiftOpen ? { color: "var(--green)", fontSize: 14 } : {}}>
                      {shiftOpen ? `с ${shiftTime}` : "Начать"}
                    </div>
                    {!shiftOpen && <span className="tile-arrow">›</span>}
                  </div>

                  {/* Income tile — spans full width */}
                  <div className="tile" style={{ gridColumn: "1/-1" }} onClick={() => setPage("income")}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <div className="tile-icon" style={{ marginBottom: 6 }}>💰</div>
                        <div className="tile-label">Доход</div>
                        <div className="tile-value gold">
                          {totalIncome.toLocaleString()} ₸
                        </div>
                        <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>за текущую неделю</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ fontSize: 10, color: "var(--muted)", textTransform: "uppercase", letterSpacing: .8, marginBottom: 6 }}>Клиентов</div>
                        <div style={{ fontFamily: "Playfair Display", fontSize: 26, fontWeight: 700, color: "var(--text)" }}>{totalClients}</div>
                        <span className="tile-arrow" style={{ position: "static", marginTop: 4, display: "block" }}>›</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* ══ PROFILE ══ */}
          {page === "profile" && (
            <>
              <div className="phdr">
                <button className="back" onClick={() => setPage("home")}>←</button>
                <div className="ptitle">Мой профиль</div>
              </div>

              <div className="photo-upload">
                <div className="pu-circle" onClick={() => fileRef.current.click()}>
                  {photoPreview ? <img src={photoPreview} alt="" /> : "📷"}
                </div>
                <div className="pu-hint">Нажмите для загрузки фото</div>
                <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={handlePhotoChange} />
              </div>

              <div className="field">
                <label>Имя</label>
                <input value={masterData.name} onChange={e => setMasterData(p => ({ ...p, name: e.target.value }))} />
              </div>
              <div className="field">
                <label>Фамилия</label>
                <input value={masterData.surname} onChange={e => setMasterData(p => ({ ...p, surname: e.target.value }))} />
              </div>
              <div className="field">
                <label>Номер телефона</label>
                <input type="tel" value={masterData.phone} onChange={e => setMasterData(p => ({ ...p, phone: e.target.value }))} />
              </div>
              <div className="field">
                <label>О себе</label>
                <textarea rows={4} value={masterData.bio} onChange={e => setMasterData(p => ({ ...p, bio: e.target.value }))} />
              </div>
              <button className="btn-save" onClick={() => setPage("home")}>Сохранить изменения</button>
            </>
          )}

          {/* ══ INCOME DASHBOARD ══ */}
          {page === "income" && (
            <>
              <div className="phdr">
                <button className="back" onClick={() => setPage("home")}>←</button>
                <div className="ptitle">Мой доход</div>
              </div>

              {/* Period select */}
              <select className="period-select" value={periodId} onChange={e => setPeriodId(e.target.value)}>
                {PERIODS.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
              </select>

              {/* Date range inputs */}
              <div className="date-range-row">
                <div>
                  <div className="date-range-label">С</div>
                  <input type="date" value={customStart} onChange={e => { setCustomStart(e.target.value); setPeriodId("custom"); }} />
                </div>
                <div style={{ display: "flex", alignItems: "flex-end", paddingBottom: 2, color: "var(--muted)" }}>—</div>
                <div>
                  <div className="date-range-label">По</div>
                  <input type="date" value={customEnd} onChange={e => { setCustomEnd(e.target.value); setPeriodId("custom"); }} />
                </div>
              </div>

              {/* KPI grid */}
              <div className="kpi-grid">
                <div className="kpi">
                  <div className="kpi-label">Общий доход</div>
                  <div className="kpi-val gold">{totalIncome.toLocaleString()} ₸</div>
                  <div className="kpi-change up">↑ 12% к прошлому</div>
                </div>
                <div className="kpi">
                  <div className="kpi-label">Клиентов</div>
                  <div className="kpi-val">{totalClients}</div>
                  <div className="kpi-change up">↑ 3 к прошлому</div>
                </div>
                <div className="kpi">
                  <div className="kpi-label">Средний чек</div>
                  <div className="kpi-val">{avgCheck.toLocaleString()} ₸</div>
                  <div className="kpi-change down">↓ 4%</div>
                </div>
                <div className="kpi">
                  <div className="kpi-label">Макс. день</div>
                  <div className="kpi-val gold">{maxIncome.toLocaleString()} ₸</div>
                  <div className="kpi-change" style={{ color: "var(--muted)" }}>за период</div>
                </div>
              </div>

              {/* Area chart — income */}
              <div className="chart-block">
                <div className="chart-title">Динамика дохода</div>
                <ResponsiveContainer width="100%" height={150}>
                  <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="incGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#c9a84c" stopOpacity={0.35} />
                        <stop offset="95%" stopColor="#c9a84c" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252530" />
                    <XAxis dataKey="day" tick={{ fill: "#6b6b7a", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#6b6b7a", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1000).toFixed(0)}к`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="income" name="income" stroke="#c9a84c" strokeWidth={2} fill="url(#incGrad)" dot={{ fill: "#c9a84c", r: 3 }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Bar chart — clients */}
              <div className="chart-block">
                <div className="chart-title">Количество клиентов</div>
                <ResponsiveContainer width="100%" height={130}>
                  <BarChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#252530" />
                    <XAxis dataKey="day" tick={{ fill: "#6b6b7a", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#6b6b7a", fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="clients" name="clients" radius={[4, 4, 0, 0]}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={i === chartData.length - 1 ? "#c9a84c" : "#2a2a36"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Services breakdown */}
              <div className="chart-block">
                <div className="chart-title">Доход по услугам</div>
                {SERVICES_INCOME.map((s, i) => {
                  const maxAmt = Math.max(...SERVICES_INCOME.map(x => x.amount));
                  return (
                    <div key={i} className="svc-row">
                      <div className="svc-dot" style={{ background: s.color }} />
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                          <span className="svc-name">{s.name}</span>
                          <span className="svc-amount">{s.amount.toLocaleString()} ₸</span>
                        </div>
                        <div className="svc-bar-wrap">
                          <div className="svc-bar" style={{ width: `${(s.amount / maxAmt) * 100}%`, background: s.color }} />
                        </div>
                      </div>
                      <div className="svc-count">{s.count}</div>
                    </div>
                  );
                })}
              </div>

              {/* Top day */}
              <div className="chart-block" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div className="chart-title" style={{ marginBottom: 4 }}>Лучший день периода</div>
                  <div style={{ fontSize: 12, color: "var(--muted)" }}>
                    {chartData.find(d => d.income === maxIncome)?.day ?? "—"}
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontFamily: "Playfair Display", fontSize: 26, fontWeight: 700, color: "var(--gold)" }}>
                    {maxIncome.toLocaleString()} ₸
                  </div>
                  <div style={{ fontSize: 11, color: "var(--muted)" }}>
                    {chartData.find(d => d.income === maxIncome)?.clients ?? 0} клиентов
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* ══ SHIFT MODAL ══ */}
        {shiftModal && (
          <div className="overlay" onClick={() => shiftModal !== "loading" && setShiftModal(null)}>
            <div className="sheet" onClick={e => e.stopPropagation()}>

              {shiftModal === "loading" && (
                <>
                  <div className="loading-spin" />
                  <div className="sheet-title">Определение местоположения…</div>
                  <div className="sheet-sub">Проверяем ваше местоположение, пожалуйста подождите</div>
                </>
              )}

              {shiftModal === "success" && (
                <>
                  <div className="sheet-icon">✅</div>
                  <div className="sheet-title">Смена открыта</div>
                  <div className="sheet-sub success">
                    Ваша рабочая смена успешно начата в <strong>{shiftTime}</strong>.<br />
                    Удачного рабочего дня!
                  </div>
                  <button className="btn-sheet" onClick={() => setShiftModal(null)}>Отлично, начинаем!</button>
                </>
              )}

              {shiftModal === "fail" && (
                <>
                  <div className="sheet-icon">📍</div>
                  <div className="sheet-title">Вы вне зоны заведения</div>
                  <div className="sheet-sub">
                    Открытие смены возможно только находясь в радиусе <strong>50 метров</strong> от заведения.<br /><br />
                    Пожалуйста, убедитесь что вы пришли на рабочее место и повторите попытку.
                  </div>
                  <button className="btn-sheet" onClick={() => { setShiftModal(null); handleOpenShift(); }}>Повторить попытку</button>
                  <button className="btn-sheet btn-sheet-ghost" onClick={() => setShiftModal(null)}>Закрыть</button>
                </>
              )}

            </div>
          </div>
        )}

      </div>
    </>
  );
}
