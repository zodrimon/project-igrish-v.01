import { useState, useEffect, useRef } from "react";
import { register } from "@tauri-apps/plugin-global-shortcut";
import "./App.css";

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

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
            await fetch("http://127.0.0.1:8000/api/v1/voice/stream", {
              method: "POST",
              body: formData,
            });
            console.log("Audio chunk sent to server.");
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
    let isRegistered = false;
    
    async function setupShortcut() {
      try {
        await register("CommandOrControl+Shift+Space", (event) => {
          console.log("Shortcut event:", event);
          // @ts-ignore
          if (event.state === "Pressed") {
            startRecording();
          // @ts-ignore
          } else if (event.state === "Released") {
            stopRecording();
          } else {
            // Toggle fallback if state is not provided
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
              stopRecording();
            } else {
              startRecording();
            }
          }
        });
        isRegistered = true;
      } catch (e) {
        console.error("Failed to register shortcut", e);
      }
    }
    setupShortcut();
  }, []);

  return (
    <main className="container">
      <h1>Melissa Companion</h1>
      <div style={{ marginTop: "2rem" }}>
        <p>Status: <strong style={{ color: isRecording ? "red" : "green" }}>{isRecording ? "Listening..." : "Idle"}</strong></p>
        <p>Hold <code>Ctrl+Shift+Space</code> to talk, or click the button below.</p>
        <button onMouseDown={startRecording} onMouseUp={stopRecording} onMouseLeave={stopRecording}>
          Push to Talk
        </button>
      </div>
    </main>
  );
}

export default App;
