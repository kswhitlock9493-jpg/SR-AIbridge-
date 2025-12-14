import { useState, useEffect } from "react";
import { apiClient } from "../api";

export default function IndoctrinationPanel() {
  const [agents, setAgents] = useState([]);
  const [form, setForm] = useState({name:"", role:"", specialties:""});

  const refresh = async () => {
    try {
      const r = await apiClient.get("/engines/indoctrination/agents");
      setAgents(r || []);
    } catch (error) {
      console.error("Failed to fetch agents:", error);
    }
  };

  const onboard = async () => {
    try {
      await apiClient.post("/engines/indoctrination/onboard", {
        ...form, 
        specialties: form.specialties.split(",").map(s=>s.trim())
      });
      setForm({name:"", role:"", specialties:""});
      refresh();
    } catch (error) {
      console.error("Failed to onboard agent:", error);
    }
  };

  useEffect(()=>{ refresh(); },[]);

  return (
    <div className="panel">
      <h3>⚔️ Indoctrination Engine</h3>
      <div style={{display:"flex", gap:8, marginBottom:12}}>
        <input placeholder="Name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/>
        <input placeholder="Role" value={form.role} onChange={e=>setForm({...form,role:e.target.value})}/>
        <input placeholder="Specialties (comma)" value={form.specialties} onChange={e=>setForm({...form,specialties:e.target.value})}/>
        <button onClick={onboard}>Onboard</button>
      </div>
      <ul>
        {agents.map(a=>(
          <li key={a.id}>
            <b>{a.name}</b> — {a.role} ({a.status})  
            {a.certified ? " ✅" : " ⏳"}
          </li>
        ))}
      </ul>
    </div>
  );
}
