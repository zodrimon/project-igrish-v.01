import { useState, useEffect, useRef } from "react";
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
      }
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <main className="container">
      <h1>Melissa Companion</h1>
      <div style={{ marginTop: "2rem" }}>
        <p>Status: <strong style={{ color: isRecording ? "red" : "green" }}>{isRecording ? "Listening..." : "Idle"}</strong></p>
        <p>Say "Melissa" to wake up and start talking.</p>
        <button onMouseDown={startRecording} onMouseUp={stopRecording} onMouseLeave={stopRecording}>
          Manual Push to Talk
        </button>
      </div>
    </main>
  );
}

export default App;
