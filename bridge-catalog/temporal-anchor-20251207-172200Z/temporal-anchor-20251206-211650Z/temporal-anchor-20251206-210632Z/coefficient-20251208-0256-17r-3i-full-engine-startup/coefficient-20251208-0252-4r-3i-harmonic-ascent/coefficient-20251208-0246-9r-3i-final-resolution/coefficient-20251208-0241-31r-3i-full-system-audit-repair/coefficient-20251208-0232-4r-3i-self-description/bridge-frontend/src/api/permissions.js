import { apiClient } from "./index";

export const getSchema = () => apiClient.get("/permissions/schema");
export const getCurrent = (captain) => apiClient.get(`/permissions/current?captain=${encodeURIComponent(captain)}`);
export const applyTier = (captain, tier) => apiClient.post(`/permissions/apply-tier?captain=${encodeURIComponent(captain)}&tier=${encodeURIComponent(tier)}`);
export const saveSettings = (payload) => apiClient.post("/permissions/update", payload);
export const sendConsent = (captain, accepted, version="v1.0", text_digest=null) =>
  apiClient.post("/permissions/consent", { captain, accepted, version, text_digest });
