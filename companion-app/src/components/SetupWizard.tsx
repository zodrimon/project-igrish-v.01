import { useState } from "react";

interface SetupWizardProps {
  onComplete: () => void;
}

export default function SetupWizard({ onComplete }: SetupWizardProps) {
  const [step, setStep] = useState(1);
  const [apiKey, setApiKey] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [consentMic, setConsentMic] = useState(true);
  const [consentWindow, setConsentWindow] = useState(true);
  const [consentClipboard, setConsentClipboard] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetch("http://127.0.0.1:8000/api/v1/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          settings: {
            "api_key": apiKey,
            "sensor.microphone.enabled": consentMic ? "true" : "false",
            "sensor.window.enabled": consentWindow ? "true" : "false",
            "sensor.clipboard.enabled": consentClipboard ? "true" : "false",
            "setup_complete": "true"
          }
        })
      });
      onComplete();
    } catch (err) {
      console.error("Failed to save settings", err);
      alert("Failed to save setup. Please check if backend is running.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <main className="container" style={{ padding: "2rem", maxWidth: "600px", margin: "0 auto", textAlign: "left" }}>
      <h1>Welcome to Melissa Companion</h1>
      <p>Let's get you set up so Melissa can help you stay productive.</p>
      
      <hr style={{ margin: "2rem 0" }} />

      {step === 1 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <h2>Step 1: LLM Provider Setup</h2>
          <p>Melissa requires an API Key (OpenAI, Anthropic, or Gemini) to process context and generate responses locally.</p>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <label htmlFor="apiKey"><strong>API Key:</strong></label>
            <input 
              id="apiKey" 
              type="password" 
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              style={{ padding: "0.5rem", marginTop: "0.5rem", width: "100%" }}
            />
          </div>
          <button onClick={() => setStep(2)} disabled={!apiKey.trim()} style={{ alignSelf: "flex-end" }}>
            Next
          </button>
        </div>
      )}

      {step === 2 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <h2>Step 2: Sensor Consents</h2>
          <p>Melissa works locally by observing your workspace. Choose what you allow it to see (all processing is local). You can change these later.</p>
          
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <input type="checkbox" id="micConsent" checked={consentMic} onChange={(e) => setConsentMic(e.target.checked)} />
            <label htmlFor="micConsent"><strong>Microphone (Wake Word)</strong> - Allows hands-free activation by saying "Melissa".</label>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <input type="checkbox" id="winConsent" checked={consentWindow} onChange={(e) => setConsentWindow(e.target.checked)} />
            <label htmlFor="winConsent"><strong>Window Tracking</strong> - Allows reading active window titles for context.</label>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <input type="checkbox" id="clipConsent" checked={consentClipboard} onChange={(e) => setConsentClipboard(e.target.checked)} />
            <label htmlFor="clipConsent"><strong>Clipboard Monitoring</strong> - Reads your clipboard to assist with coding and context.</label>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "1rem" }}>
            <button onClick={() => setStep(1)} className="secondary">Back</button>
            <button onClick={handleSave} disabled={isSaving}>
              {isSaving ? "Saving..." : "Finish Setup"}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
