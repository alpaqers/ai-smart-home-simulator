from __future__ import annotations
import json
import os
from dataclasses import asdict
from ..models.device_storage import DeviceStorage
from ..models.device import Device
from ..models.events import StorageEvent
from .time_service import TimeService

STORAGE_FILE = "device_storage.json"

def save_event_to_file(event: StorageEvent) -> None:
    """Loads the list of historical events, appends a new event to the end, and saves the JSON file."""
    events_list = []
    
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                events_list = json.load(f)
        except json.JSONDecodeError:
            events_list = []

    events_list.append(asdict(event))

    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(events_list, f, indent=4)


def load_from_file(time_service: TimeService) -> DeviceStorage:
    """Replays the application state step-by-step based on the event history."""
    storage = DeviceStorage()
    
    if not os.path.exists(STORAGE_FILE):
        return storage

    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            events_list = json.load(f)
    except json.JSONDecodeError:
        return storage

    for ev in events_list:
        event_type = ev.get("event_type")
        
        # handle device registrations and state updates
        if event_type in ["device_registration", "state_update"]:
            dev_data = ev.get("device_data")
            if dev_data:
                dev_id = ev.get("device_id")
                device_obj = Device(**dev_data)
                
                # put object into storage containter
                dtype = device_obj.device_type.lower()
                if dtype == "lamp":
                    storage.lamps[dev_id] = device_obj
                elif dtype in ["thermometer", "sensor"]:
                    storage.thermometers[dev_id] = device_obj
                elif dtype in ["ac", "airconditioning"]:
                    storage.ACs[dev_id] = device_obj

        # handle system time shift events 
        elif event_type == "time_shift":
            duration = ev.get("duration")
            if duration is not None:
                # get current integer timestamp, add duration seconds, and update service
                current_timestamp = time_service.now()
                new_simulated_timestamp = current_timestamp + duration
                time_service.use_simulated_time(new_simulated_timestamp)
                print(f"[REPLAY] Application clock shifted by {duration} seconds. New timestamp: {new_simulated_timestamp}")

    return storage
