import React, { useEffect, useState } from "react";
import { getSchema, getCurrent, applyTier, saveSettings, sendConsent } from "../api/permissions";

export default function PermissionsConsole({ captain="Kyle" }) {
  const [schema, setSchema] = useState(null);
  const [settings, setSettings] = useState(null);
  const [busy, setBusy] = useState(false);
  const CONSENT_TEXT = `By enabling autonomy, location, voice, screen, or data access, you authorize the Bridge to operate within the selected limits. Logs are append-only under vault/ for audit.`;

  useEffect(() => {
    (async () => {
      const s = await getSchema(); setSchema(s.data || s);
      const c = await getCurrent(captain); setSettings((c.data || c).settings);
    })();
  }, [captain]);

  const onApplyTier = async (tier) => {
    setBusy(true);
    const r = await applyTier(captain, tier);
    setSettings((r.data || r).settings);
    setBusy(false);
  };

  const onToggle = (path, value) => {
    const copy = JSON.parse(JSON.stringify(settings));
    const segs = path.split(".");
    let cur = copy;
    for (let i=0;i<segs.length-1;i++) cur = cur[segs[i]];
    cur[segs[segs.length-1]] = value;
    setSettings(copy);
  };

  const onSave = async () => {
    setBusy(true);
    await saveSettings({ captain, settings });
    setBusy(false);
    alert("Permissions saved.");
  };

  const onConsent = async (accepted) => {
    setBusy(true);
    // Optional: sha256 of CONSENT_TEXT — handled server-side later if needed
    await sendConsent(captain, accepted, "v1.0", null);
    const c = await getCurrent(captain);
    setSettings((c.data || c).settings);
    setBusy(false);
  };

  if (!settings) return <div className="panel">Loading permissions…</div>;

  return (
    <div className="panel">
      <h3>Permissions Console</h3>
      <div style={{display:"flex", gap:8, marginBottom:8}}>
        <button disabled={busy} onClick={()=>onApplyTier("free")}>Apply Free</button>
        <button disabled={busy} onClick={()=>onApplyTier("pro")}>Apply Pro</button>
        <button disabled={busy} onClick={()=>onApplyTier("admiral")}>Apply Admiral</button>
        <div style={{marginLeft:"auto", opacity:.8}}>Tier: <b>{settings.tier}</b></div>
      </div>

      <section style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:16}}>
        <div className="card">
          <h4>Autonomy</h4>
          <label><input type="checkbox"
            checked={settings.autonomy.enabled}
            onChange={e=>onToggle("autonomy.enabled", e.target.checked)} /> Enabled</label>
          <div style={{marginTop:6}}>
            Max Hours/Day: <input type="number" min={0} max={24}
              value={settings.autonomy.max_hours_per_day}
              onChange={e=>onToggle("autonomy.max_hours_per_day", Number(e.target.value)||0)} />
          </div>
          <div style={{marginTop:6}}>
            Modes:
            {["screen","connector","hybrid"].map(m => (
              <label key={m} style={{marginLeft:10}}>
                <input type="checkbox"
                  checked={settings.autonomy.modes.includes(m)}
                  onChange={(e)=>{
                    const cur = new Set(settings.autonomy.modes);
                    e.target.checked ? cur.add(m) : cur.delete(m);
                    onToggle("autonomy.modes", Array.from(cur));
                  }} /> {m}
              </label>
            ))}
          </div>
        </div>

        <div className="card">
          <h4>Location</h4>
          {["none","approximate","precise"].map(opt => (
            <label key={opt} style={{marginRight:10}}>
              <input type="radio" name="loc" checked={settings.location.share===opt}
                onChange={()=>onToggle("location.share", opt)} /> {opt}
            </label>
          ))}
        </div>

        <div className="card">
          <h4>Screen</h4>
          {["share","mirror","overlay"].map(k=>(
            <label key={k} style={{display:"block"}}>
              <input type="checkbox"
                checked={settings.screen[k]}
                onChange={e=>onToggle(`screen.${k}`, e.target.checked)} /> {k}
            </label>
          ))}
        </div>

        <div className="card">
          <h4>Voice</h4>
          <label><input type="checkbox" checked={settings.voice.stt} onChange={e=>onToggle("voice.stt", e.target.checked)} /> STT</label>
          <label style={{display:"block"}}><input type="checkbox" checked={settings.voice.tts} onChange={e=>onToggle("voice.tts", e.target.checked)} /> TTS</label>
        </div>

        <div className="card">
          <h4>Data Access</h4>
          {["email","drive","docs","chats"].map(k=>(
            <label key={k} style={{display:"block"}}>
              <input type="checkbox" checked={settings.data[k]} onChange={e=>onToggle(`data.${k}`, e.target.checked)} /> {k}
            </label>
          ))}
        </div>

        <div className="card">
          <h4>Logging</h4>
          <div>
            Level:
            {["minimal","standard","verbose"].map(l=>(
              <label key={l} style={{marginLeft:10}}>
                <input type="radio" name="loglevel" checked={settings.logging.level===l} onChange={()=>onToggle("logging.level", l)} /> {l}
              </label>
            ))}
          </div>
          <div style={{marginTop:6}}>
            Retention (days): <input type="number" min={7} max={365}
              value={settings.logging.retention_days}
              onChange={e=>onToggle("logging.retention_days", Number(e.target.value)||30)} />
          </div>
        </div>
      </section>

      <div className="card" style={{marginTop:12}}>
        <h4>Consent</h4>
        <p style={{whiteSpace:"pre-wrap"}}>{CONSENT_TEXT}</p>
        <div style={{display:"flex", gap:8, alignItems:"center"}}>
          <button disabled={busy} onClick={()=>onConsent(true)}>I Agree</button>
          <button disabled={busy} onClick={()=>onConsent(false)}>I Do Not Agree</button>
          <span style={{marginLeft:"auto"}}>Status: <b>{settings.consent_given ? "Granted" : "Not granted"}</b></span>
        </div>
      </div>

      <div style={{marginTop:10, display:"flex", gap:8}}>
        <button disabled={busy} onClick={onSave}>Save</button>
      </div>
    </div>
  );
}
