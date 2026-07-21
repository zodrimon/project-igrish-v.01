import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [wakeWordEnabled, setWakeWordEnabled] = useState(true);
  const [nudgeSensitivity, setNudgeSensitivity] = useState("normal");
  const [nudgeMuteCategories, setNudgeMuteCategories] = useState("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const toggleWakeWord = async () => {
    const newState = !wakeWordEnabled;
    try {
      await fetch("http://127.0.0.1:8000/api/v1/voice/wake-word/toggle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ enabled: newState })
      });
      setWakeWordEnabled(newState);
    } catch (err) {
      console.error("Failed to toggle wake word:", err);
    }
  };

  const startRecording = async () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = async (e) => {
        if (e.data.size > 0) {
          const formData = new FormData();
          formData.append("audio", e.data, "chunk.webm");
          try {
            const res = await fetch("http://127.0.0.1:8000/api/v1/voice/stream", {
              method: "POST",
              body: formData,
            });
            console.log("Audio chunk sent to server, status:", res.status);
            if (res.status === 200) {
              const blob = await res.blob();
              const audioUrl = URL.createObjectURL(blob);
              const audio = new Audio(audioUrl);
              audio.play().catch(e => console.error("Error playing audio:", e));
            }
          } catch (err) {
            console.error("Error sending audio chunk:", err);
          }
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Failed to get user media", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    }
  };

  useEffect(() => {
    const eventSource = new EventSource("http://127.0.0.1:8000/api/v1/voice/events");
    
    eventSource.onmessage = (event) => {
      console.log("Received SSE:", event.data);
      if (event.data === "WAKE_WORD_DETECTED") {
        console.log("Wake word detected! Starting 5-second recording...");
        startRecording();
        
        setTimeout(() => {
          stopRecording();
        }, 5000);
      } else if (event.data.startsWith("NUDGE_AUDIO:")) {
        const textToSpeak = encodeURIComponent(event.data.substring(12));
        const audio = new Audio(`http://127.0.0.1:8000/api/v1/voice/tts?text=${textToSpeak}`);
        audio.play().catch(e => console.error("Error playing nudge audio:", e));
      }
    };

    return () => {
      eventSource.close();
    };
  }, []);

  useEffect(() => {
    // Load settings on mount
    fetch("http://127.0.0.1:8000/api/v1/settings")
      .then(res => res.json())
      .then(data => {
        if (data["nudge.sensitivity"]) setNudgeSensitivity(data["nudge.sensitivity"]);
        if (data["nudge.mute_categories"]) setNudgeMuteCategories(data["nudge.mute_categories"]);
      })
      .catch(err => console.error("Failed to load settings", err));
  }, []);

  const saveSettings = async (key: string, value: string) => {
    try {
      await fetch("http://127.0.0.1:8000/api/v1/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ settings: { [key]: value } })
      });
    } catch (err) {
      console.error("Failed to save settings", err);
    }
  };

  const handleSensitivityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setNudgeSensitivity(e.target.value);
    saveSettings("nudge.sensitivity", e.target.value);
  };

  const handleMuteChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNudgeMuteCategories(e.target.value);
    saveSettings("nudge.mute_categories", e.target.value);
  };

  return (
    <main className="container">
      <h1>Melissa Companion</h1>
      <div style={{ marginTop: "2rem" }}>
        {isRecording && (
          <div className="listening-pulse">
            <span role="img" aria-label="microphone" style={{ fontSize: "2rem" }}>🎤</span>
          </div>
        )}
        <p>Status: <strong style={{ color: isRecording ? "red" : "green" }}>{isRecording ? "Listening..." : "Idle"}</strong></p>
        
        <div style={{ margin: "1rem 0", display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
          <label htmlFor="wakeWordToggle">Always-listening (Wake Word): </label>
          <input 
            type="checkbox" 
            id="wakeWordToggle" 
            checked={wakeWordEnabled} 
            onChange={toggleWakeWord}
          />
        </div>

        {!isRecording && wakeWordEnabled && <p>Say "Melissa" to wake up and start talking.</p>}
        {!isRecording && !wakeWordEnabled && <p>Wake word disabled.</p>}
        
        <button onMouseDown={startRecording} onMouseUp={stopRecording} onMouseLeave={stopRecording} style={{ marginTop: "1rem" }}>
          Manual Push to Talk
        </button>

        <hr style={{ margin: "2rem 0" }} />
        
        <h3>Nudge Settings</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", alignItems: "center" }}>
          <div>
            <label htmlFor="nudgeSensitivity">Sensitivity: </label>
            <select id="nudgeSensitivity" value={nudgeSensitivity} onChange={handleSensitivityChange}>
              <option value="normal">Normal</option>
              <option value="gentle">Gentle</option>
              <option value="off">Off</option>
            </select>
          </div>
          <div>
            <label htmlFor="nudgeMuteCategories">Mute Categories (comma-separated): </label>
            <input 
              type="text" 
              id="nudgeMuteCategories" 
              value={nudgeMuteCategories} 
              onChange={handleMuteChange}
              placeholder="e.g. social, news"
            />
          </div>
        </div>
      </div>
    </main>
  );
}

export default App;
