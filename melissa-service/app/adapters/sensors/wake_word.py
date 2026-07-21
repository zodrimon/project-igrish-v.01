import pyaudio
import logging
import threading
from pocketsphinx import Decoder

logger = logging.getLogger(__name__)

class WakeWordSensor:
    def __init__(self, keyword="melissa", threshold=1e-10, on_wake=None):
        self.keyword = keyword
        self.threshold = threshold
        self.on_wake = on_wake
        
        # Configure pocketsphinx for keyword spotting
        config = Decoder.default_config()
        # Must unset -lm if it was auto-populated by default_config
        config.set_string('-lm', None)
        config.set_string('-keyphrase', self.keyword)
        config.set_float('-kws_threshold', self.threshold)
        config.set_string('-logfn', 'nul') # suppress C level logs on windows
        
        self.decoder = Decoder(config)
        
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self._running = False
        self._thread = None
        
    def start(self):
        if self._running:
            return
            
        try:
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=2048
            )
            self.decoder.start_utt()
            self._running = True
            self._thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._thread.start()
            logger.info(f"Wake word sensor started. Listening for '{self.keyword}'")
        except Exception as e:
            logger.error(f"Failed to start wake word sensor: {e}")
            self._running = False
        
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.decoder.end_utt()
        logger.info("Wake word sensor stopped.")
        
    def _listen_loop(self):
        while self._running:
            buf = self.stream.read(2048, exception_on_overflow=False)
            self.decoder.process_raw(buf, False, False)
            
            if self.decoder.hyp() is not None:
                # Keyword detected
                logger.info(f"Wake word '{self.keyword}' detected!")
                if self.on_wake:
                    self.on_wake()
                
                # Reset decoder for next utterance
                self.decoder.end_utt()
                self.decoder.start_utt()
