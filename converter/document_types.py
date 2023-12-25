import dataclasses
from datetime import datetime, timedelta

from typing import List


@dataclasses.dataclass
class ScattDocument:
    event_name: str
    event_name_short: str
    caliber: str
    shooter: str
    date: datetime
    comments: str
    rings: List[float]
    shots: List["ScattShot"]

    @classmethod
    def from_json(cls, json_data: dict):
        event_name = json_data["event_name"]
        event_name_short = json_data["event_short_name"]
        caliber = json_data["caliber"]
        shooter = json_data["shooter"]
        date = datetime.strptime(json_data["date"], "%d.%m.%Y %H:%M:%S")
        comments = json_data["comments"]
        rings = json_data["rings"]
        shots = [ScattShot.from_json(shot) for shot in json_data["shots"]]

        return cls(event_name, event_name_short, caliber, shooter, date, comments, rings, shots)

    def to_json(self):
        return {
            "event_name": self.event_name,
            "event_short_name": self.event_name_short,
            "caliber": self.caliber,
            "shooter": self.shooter,
            "date": self.date.strftime("%d.%m.%Y %H:%M:%S"),
            "comments": self.comments,
            "rings": self.rings,
            "shots": [shot.to_json() for shot in self.shots]
        }


@dataclasses.dataclass
class ScattShot:
    number: int
    f_coefficient: str
    enter_time: datetime
    shot_time: datetime
    result: float
    breach_x: float
    breach_y: float
    trace: List["ScattTraceElement"]

    @classmethod
    def from_json(cls, json_data: dict):
        number = json_data["number"]
        f_coefficient = json_data["f_coefficient"]
        enter_time = datetime.strptime(json_data["enter_time"], "%d.%m.%Y %H:%M:%S")
        shot_time = datetime.strptime(json_data["shot_time"], "%d.%m.%Y %H:%M:%S")
        result = json_data["result"]
        breach_x = json_data["breach_x"]
        breach_y = json_data["breach_y"]
        trace = [ScattTraceElement.from_json(element) for element in json_data["trace"]]

        return cls(number, f_coefficient, enter_time, shot_time, result, breach_x, breach_y, trace)

    def to_json(self):
        return {
            "number": self.number,
            "f_coefficient": self.f_coefficient,
            "enter_time": self.enter_time.strftime("%d.%m.%Y %H:%M:%S"),
            "shot_time": self.shot_time.strftime("%d.%m.%Y %H:%M:%S"),
            "result": self.result,
            "breach_x": self.breach_x,
            "breach_y": self.breach_y,
            "trace": [element.to_json() for element in self.trace]
        }

    def duration(self) -> float:
        if not self.trace:
            return 0

        return abs(self.trace[-1].t_relative) + abs(self.trace[0].t_relative)


TARGET_DIAMETER = 45.5
TARGET_RADIUS = TARGET_DIAMETER / 2


@dataclasses.dataclass
class ScattTraceElement:
    t_relative: float
    x: float
    y: float

    @classmethod
    def from_json(cls, json_data: dict):
        t_relative = json_data["t"]
        x = json_data["x"]
        y = json_data["y"]

        return cls(t_relative, x, y)

    def to_json(self):
        return {
            "t": self.t_relative,
            "x": self.x,
            "y": self.y
        }

    def absolute_datetime(self, shot_time: datetime) -> datetime:
        return shot_time + timedelta(seconds=self.t_relative)

    def absolute_time(self, shot_start: float) -> float:
        if self.t_relative < 0:
            return abs(shot_start) - abs(self.t_relative)
        else:
            return abs(shot_start) + self.t_relative

    def x_offset(self, width: int) -> int:
        # x is rectmode center
        x = self.x + TARGET_RADIUS
        return int((x / TARGET_DIAMETER) * width)

    def y_offset(self, height: int) -> int:
        # y is rectmode center
        y = self.y + TARGET_RADIUS
        return int((y / TARGET_DIAMETER) * height)
