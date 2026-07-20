import sys
import os

# Add melissa-service to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import logging
from app.adapters.sensors.wake_word import WakeWordSensor

logging.basicConfig(level=logging.INFO)

def on_wake():
    print(">>> WAKE WORD TRIGGERED! <<<")

def main():
    print("Testing Wake Word Sensor...")
    print("Please say 'melissa' into your microphone.")
    
    sensor = WakeWordSensor(keyword="melissa", on_wake=on_wake)
    sensor.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        sensor.stop()

if __name__ == "__main__":
    main()
