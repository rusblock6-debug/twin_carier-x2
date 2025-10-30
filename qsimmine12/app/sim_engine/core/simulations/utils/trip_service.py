import math
import datetime
import logging
from collections import defaultdict

from app.sim_engine.core.props import ActualTrip, ShiftChangeArea, QuarryObject, TripData, IdleArea
from app.sim_engine.core.simulations.utils.helpers import sim_current_time, sim_start_time
from app.sim_engine.enums import ObjectType

logger = logging.getLogger(__name__)


class TripService:
    def __init__(self) -> None:
        self.__actual_trips: dict[int, ActualTrip] = {}
        self.__finished_trips: defaultdict[int, list[ActualTrip]] = defaultdict(list)

        self.total_trips = 0
        self.total_volume = 0
        self.total_weight = 0
        self.total_volume_round = 0
        self.total_weight_round = 0
        self.unique_truck_ids = set()
        self.unique_shovel_ids = set()
        self.hourly_volume = defaultdict(int)
        self.hourly_weight = defaultdict(int)
        self.hourly_trip = defaultdict(int)
        self.trips_table: list[dict] = []

        self.shift_change_area: IdleArea | None = None

    def set_shift_change_area(self, shift_change_area: IdleArea) -> None:
        self.shift_change_area = shift_change_area

    def begin(self, trip_data: TripData) -> None:
        truck_id = trip_data.truck_id

        if truck_id in self.__actual_trips:
            logger.debug(f"Trip для {truck_id} уже начат")
            return

        if truck_id in self.__finished_trips:
            object_id = trip_data.unload_id
            object_type = ObjectType.UNLOAD
        else:
            if self.shift_change_area is None:
                raise RuntimeError('Shift area is not set')

            object_id = self.shift_change_area.id
            object_type = ObjectType.IDLE_AREA

        current_time = sim_current_time()

        actual_trip = ActualTrip(
            start_trip_data=trip_data,
            start_object=QuarryObject(
                id=object_id,
                type=object_type,
            ),
            start_time=current_time,
        )

        self.__actual_trips[truck_id] = actual_trip

    def finish(self, trip_data: TripData) -> None:
        actual_trip = self.__finish_actual_trip(trip_data)

        self.__update_summary_metrics(actual_trip)

        self.trips_table.append(actual_trip.to_telemetry())

    def get_summary(self, end_time: datetime.datetime) -> dict:
        start_hour = sim_start_time().hour
        end_hour = end_time.hour

        if end_hour >= start_hour:
            hours = list(range(start_hour, end_hour + 1))
        else:
            hours = list(range(start_hour, 24)) + list(range(0, end_hour + 1))

        chart_volume_data = []
        chart_weight_data = []
        chart_trip_data = []
        for hour in hours:
            time_str = f"{hour}:00"
            volume_value = self.hourly_volume.get(hour, 0)
            if volume_value:
                chart_volume_data.append({'time': time_str, 'value': volume_value})

            weight_value = self.hourly_weight.get(hour, 0)
            if weight_value:
                chart_weight_data.append({'time': time_str, 'value': weight_value})

            trip_value = self.hourly_trip.get(hour, 0)
            if trip_value:
                chart_trip_data.append({'time': time_str, 'value': trip_value})

        """
            на фронте изначально график на не правильный параметр был подвязан
            'chart_volume_data': chart_weight_data,
        """
        summary = {
            'trips': self.total_trips,
            'volume': math.floor(self.total_volume_round),
            'weight': math.floor(self.total_weight_round),
            # Объем, пока оставим, мб потом понадобится
            # 'chart_volume_data': chart_volume_data,
            'chart_volume_data': chart_weight_data,  # TODO: согласовать изменения с фронтом
            'chart_trip_data': chart_trip_data,
            'trucks_count': len(self.unique_truck_ids),
            'shovels_count': len(self.unique_shovel_ids),
            'trips_table': self.trips_table
        }

        return summary

    def print_summary(self):
        logger.debug(
            f"\u2705 Завершено. Рейсов: {self.total_trips}, Объем: {self.total_volume:.1f} м3; Масса: {self.total_weight:.1f} т")
        for h in sorted(self.hourly_volume):
            logger.debug(f"  Час {h:02d}: {self.hourly_volume[h]:.1f} м3")

    def __finish_actual_trip(self, trip_data: TripData) -> ActualTrip:
        truck_id = trip_data.truck_id

        if truck_id not in self.__actual_trips:
            raise RuntimeError(f"Trip {truck_id} is not pending")

        current_time_value = sim_current_time()

        actual_trip = self.__actual_trips[truck_id]
        actual_trip.weight = trip_data.truck_weight
        actual_trip.volume = trip_data.truck_volume
        actual_trip.end_object = QuarryObject(
            id=trip_data.unload_id,
            type=ObjectType.UNLOAD,
        )
        actual_trip.end_time = current_time_value
        actual_trip.end_trip_data = trip_data

        self.__finished_trips[truck_id].append(actual_trip)
        del self.__actual_trips[truck_id]

        return actual_trip

    def __update_summary_metrics(self, finished_trip: ActualTrip) -> None:
        end_trip_data = finished_trip.end_trip_data

        volume = end_trip_data.truck_volume
        weight = end_trip_data.truck_weight

        round_volume = int(volume)
        round_weight = int(weight)

        self.total_trips += 1
        self.total_volume += volume
        self.total_weight += weight
        self.total_volume_round += round_volume
        self.total_weight_round += round_weight

        hour = finished_trip.end_time.hour
        # self.hourly_volume[hour] += volume
        # self.hourly_weight[hour] += weight

        # при округлении немного теряем в точности для сходимости с конечным результатом
        self.hourly_volume[hour] = int(self.hourly_volume[hour] + round_volume)
        self.hourly_weight[hour] = int(self.hourly_weight[hour] + round_weight)
        self.hourly_trip[hour] += 1

        self.unique_shovel_ids.add(end_trip_data.shovel_id)
        self.unique_truck_ids.add(end_trip_data.truck_id)
