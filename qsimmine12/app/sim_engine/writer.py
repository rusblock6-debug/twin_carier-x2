from abc import ABC, abstractmethod

from app.sim_engine.events import Event


class IWriter(ABC):

    @abstractmethod
    def update_data(self, key: str, **kwargs) -> None:
        pass

    @abstractmethod
    def push_event(self, evt: Event) -> None:
        pass

    @abstractmethod
    def writerow(self, row: dict) -> None:
        pass

    @abstractmethod
    def finalize(self):
        pass


class DictSimpleWriter(IWriter):
    def __init__(self) -> None:
        self.data: dict = {
            "telemetry": [],
            "summary": {},
            "events": [],
            "meta": {},
        }

    def update_data(self, key, **kwargs) -> None:
        self.data[key].update(kwargs)

    def push_event(self, evt: Event) -> None:
        self.data["events"].append(evt.to_dict())

    def writerow(self, row: dict) -> None:
        self.data["telemetry"].append(row)

    def finalize(self) -> dict:
        return self.data


class DictReliabilityWriter(DictSimpleWriter):
    def __init__(self) -> None:
        super().__init__()
        self.data.pop("telemetry", None)
        self.data.pop("events", None)

    def push_event(self, evt: Event) -> None:
        pass

    def writerow(self, row: dict) -> None:
        pass


class BatchWriter(IWriter):
    def __init__(self, batch_size_seconds: int = 60) -> None:
        self.batch_size_seconds = batch_size_seconds
        self.batches: dict = {}  # Хранит батчи с последовательной нумерацией 0,1,2...
        self.events: list = []
        self.next_batch_index = 0  # Счётчик батчей
        self.batch_time_map: dict = {}  # Соответствие timestamp → batch_index
        self.meta = {
            "start_timestamp": None,
            "end_timestamp": None,
            "frame_interval": 1,
            "batch_size_seconds": batch_size_seconds,
            "total_frames": 0,
        }

    def update_data(self, key, **kwargs) -> None:
        getattr(self, key).update(kwargs)

    def push_event(self, evt: Event) -> None:
        self.events.append(evt.to_dict())

    def writerow(self, row: dict) -> None:
        timestamp = row["timestamp"]

        # Определяем временной интервал
        time_slot = int(timestamp // self.batch_size_seconds)

        # Находим или создаём batch_index для этого временного интервала
        if time_slot not in self.batch_time_map:
            self.batch_time_map[time_slot] = self.next_batch_index
            self.batches[self.next_batch_index] = {
                "start_time": timestamp,
                "end_time": timestamp,
                "time_slot": time_slot,
                "frames": []
            }
            self.next_batch_index += 1

        batch_index = self.batch_time_map[time_slot]
        batch = self.batches[batch_index]

        # Обновляем границы батча
        if timestamp < batch["start_time"]:
            batch["start_time"] = timestamp
        if timestamp > batch["end_time"]:
            batch["end_time"] = timestamp

        batch["frames"].append(row)
        self.meta["total_frames"] += 1

        # Обновляем общие метаданные
        if self.meta["start_timestamp"] is None or timestamp < self.meta["start_timestamp"]:
            self.meta["start_timestamp"] = timestamp
        if self.meta["end_timestamp"] is None or timestamp > self.meta["end_timestamp"]:
            self.meta["end_timestamp"] = timestamp

    def finalize(self) -> dict:
        return {
            "meta": {
                **self.meta,
                "total_batches": len(self.batches),
                "batch_keys": list(self.batches.keys()),
            },
            "batches": self.batches,
            "events": self.events,
            "summary": {},
        }
