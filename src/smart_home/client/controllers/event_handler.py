import threading
import queue

class EventHandler(threading.Thread):
    def __init__(self):
        super().__init__(name="EventHandlerThread", daemon=True)
        self._queue = queue.Queue()
        self._subscribers = [] 
        self._running = True

    def subscribe(self, callback):
        """ DeviceStorage or AI"""
        self._subscribers.append(callback)

    def put_event(self, data):
        """raw data"""
        self._queue.put(data)

    def run(self):
        
        while self._running:
            try:
                event_data = self._queue.get(timeout=1.0)
                
                for callback in self._subscribers:
                    callback(event_data)
                
                self._queue.task_done()
            except queue.Empty:
                continue

    def stop(self):
        self._running = False