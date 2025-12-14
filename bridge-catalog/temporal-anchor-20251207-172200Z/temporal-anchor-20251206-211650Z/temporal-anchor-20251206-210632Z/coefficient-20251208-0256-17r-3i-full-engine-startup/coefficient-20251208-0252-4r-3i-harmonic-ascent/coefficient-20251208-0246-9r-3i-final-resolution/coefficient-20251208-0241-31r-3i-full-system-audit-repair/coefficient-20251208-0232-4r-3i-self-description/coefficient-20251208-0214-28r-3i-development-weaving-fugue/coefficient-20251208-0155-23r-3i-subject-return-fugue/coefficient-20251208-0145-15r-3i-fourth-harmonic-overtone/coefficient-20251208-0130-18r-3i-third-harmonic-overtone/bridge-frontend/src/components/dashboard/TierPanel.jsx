import { useEffect, useState } from "react";
import { Card, CardContent } from "../ui/card.jsx";
import { Button } from "../ui/button.jsx";
import { Badge } from "../ui/badge.jsx";
import config from "../../config.js";

const API_BASE_URL = config.API_BASE_URL;

export default function TierPanel() {
  const [tier, setTier] = useState("loading");
  const [status, setStatus] = useState("checking");
  const [features, setFeatures] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/registry/tier/me`)
      .then(r => r.json())
      .then(data => {
        setTier(data.tier);
        setStatus(data.status);
        setFeatures(data.features || []);
      })
      .catch(() => {
        setTier("unknown");
        setStatus("error");
        setFeatures([]);
      });
  }, []);

  const manageBilling = () => {
    window.open("/payments/stripe/portal", "_blank");
  };

  return (
    <Card className="rounded-2xl shadow p-4 bg-slate-900 text-white" style={{
      backgroundColor: "#0f172a",
      color: "white",
      borderRadius: "1rem",
      padding: "1.5rem",
      boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    }}>
      <CardContent>
        <h2 className="text-xl font-semibold" style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "1rem" }}>
          Subscription Status
        </h2>
        <p style={{ marginTop: "0.5rem" }}>
          Tier: <span style={{ fontWeight: "bold" }}>{tier}</span>
        </p>
        <p>
          Status: <span style={{ fontStyle: "italic" }}>{status}</span>
        </p>

        <div style={{ marginTop: "1rem" }}>
          <h3 style={{ fontWeight: 600, marginBottom: "0.5rem" }}>Features</h3>
          <ul style={{ marginTop: "0.5rem", listStyle: "none", padding: 0 }}>
            {features.map((f, i) => (
              <li key={i} style={{ 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "space-between",
                marginBottom: "0.25rem",
                padding: "0.5rem",
                backgroundColor: "#1e293b",
                borderRadius: "0.5rem"
              }}>
                <span>{f.label}</span>
                {f.available ? (
                  <Badge className="bg-green-600" style={{ 
                    backgroundColor: "#16a34a", 
                    color: "white",
                    padding: "0.25rem 0.75rem",
                    borderRadius: "0.375rem",
                    fontSize: "0.875rem"
                  }}>
                    Enabled
                  </Badge>
                ) : (
                  <Badge className="bg-gray-600" style={{ 
                    backgroundColor: "#4b5563", 
                    color: "white",
                    padding: "0.25rem 0.75rem",
                    borderRadius: "0.375rem",
                    fontSize: "0.875rem"
                  }}>
                    Locked
                  </Badge>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div style={{ marginTop: "1.5rem" }}>
          {tier === "free" && (
            <Button onClick={manageBilling} style={{
              backgroundColor: "#3b82f6",
              color: "white",
              padding: "0.5rem 1rem",
              borderRadius: "0.5rem",
              border: "none",
              cursor: "pointer",
              fontWeight: 500
            }}>
              Upgrade to Paid
            </Button>
          )}
          {tier === "paid" && (
            <Button onClick={manageBilling} style={{
              backgroundColor: "#3b82f6",
              color: "white",
              padding: "0.5rem 1rem",
              borderRadius: "0.5rem",
              border: "none",
              cursor: "pointer",
              fontWeight: 500
            }}>
              Manage Billing
            </Button>
          )}
          {tier === "admiral" && (
            <Badge className="bg-yellow-500" style={{ 
              backgroundColor: "#eab308", 
              color: "white",
              padding: "0.5rem 1rem",
              borderRadius: "0.375rem",
              fontSize: "1rem",
              fontWeight: 600
            }}>
              Sovereign Access
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
