from copy import deepcopy
from datetime import timedelta
from typing import List

from app.sim_engine.core.geometry import path_intersects_polygons, \
    find_all_route_edges_by_road_net_from_object_to_object
from app.sim_engine.core.props import Blasting
from app.sim_engine.core.simulations.behaviors.base import BaseBehavior
from app.sim_engine.enums import ObjectType
from app.sim_engine.events import EventType
from app.sim_engine.states import TruckState


class QuarryBlastingWatcher(BaseBehavior):
    """
    Класс для карьера (Quarry), отслеживающий периоды взрывных работ и формирующий активные зоны
    """

    def __init__(self, target):
        self.active_blasting_dict = {}
        self.trucks_in_idle: List[int] = []
        super().__init__(target)

    def generate_blasting_list(self) -> list[Blasting]:
        """Создаёт список взрывных работ временами относительно времени симуляции"""
        blasting_list = deepcopy(self.target.sim_data.blasting_list)
        for blasting in blasting_list:
            blasting.start_time = (blasting.start_time - self.target.start_time).total_seconds()
            blasting.end_time = (blasting.end_time - self.target.start_time).total_seconds()
        return blasting_list

    def check_trucks_state(self):
        """
            Проверяет состояние самосвалов карьера.
            Если попал в состояние ожидания проведения взрывных работ, перепланируем рейсы, исключив этот самосвал.
            Если вышел из состояния ожидания проведения взрывных работ, перепланируем рейсы, включив этот самосвал.
        """
        trucks_to_exclude = []
        trucks_to_include = []

        # Проверим, кого нужно добавить в перепланирование рейсов, а кого исключить
        for truck in self.target.truck_map.values():
            state = truck.state
            if state == TruckState.BLASTING_IDLE and truck.id not in self.trucks_in_idle:
                self.trucks_in_idle.append(truck.id)
                trucks_to_exclude.append(truck.id)
            elif state != TruckState.BLASTING_IDLE and truck.id in self.trucks_in_idle:
                self.trucks_in_idle.remove(truck.id)
                trucks_to_include.append(truck.id)
        return trucks_to_exclude, trucks_to_include

    def run(self):
        blasting_list = self.generate_blasting_list()

        while blasting_list:
            # Фильтруем актуальные и активные взрывные работы
            blasting_list = [b for b in blasting_list if self.env.now < b.end_time]
            active_blasting = [b for b in blasting_list if b.start_time <= self.env.now < b.end_time]

            self.target.active_blasting = active_blasting
            self.target.active_blasting_polygons = [zone for blasting in active_blasting for zone in blasting.zones]

            # Пауза, чтобы дать технике возможность изменить состояние перед генерацией событий
            yield self.env.timeout(1)

            # активные взрывные работы
            active_ids = {b.id for b in active_blasting}
            # завершившиеся взрывные работы
            completed_ids = set(self.active_blasting_dict.keys()) - active_ids

            # Обрабатываем завершение взрывных работ
            for blasting_id in completed_ids:
                blasting = self.active_blasting_dict.pop(blasting_id)
                self.target.push_event(
                    EventType.BLASTING_END,
                    **dict(
                        blasting_id=blasting.id,
                        blasting_start=self.target.start_time + timedelta(seconds=blasting.start_time),
                        blasting_end=self.target.start_time + timedelta(seconds=blasting.end_time),
                    )
                )

            # Обрабатываем начало новых взрывных работ
            for blasting in active_blasting:
                if blasting.id not in self.active_blasting_dict:
                    self.target.push_event(
                        EventType.BLASTING_BEGIN,
                        **dict(
                            blasting_id=blasting.id,
                            blasting_start=self.target.start_time + timedelta(seconds=blasting.start_time),
                            blasting_end=self.target.start_time + timedelta(seconds=blasting.end_time),
                        )
                    )
                    self.active_blasting_dict[blasting.id] = blasting


class TruckBlastingWatcher(BaseBehavior):
    """
        Класс для самосвала (Truck)
        Отслеживает ожидание проведения взрывных работ для самосвала.
        Если самосвал встал в ожидание - исключим его из планировщика.
        Если самосвал вышел из ожидания - добавим его в планировщик.
    """

    def __init__(self, target):
        super().__init__(target)

    def run(self):
        in_blasting_idle = False
        while True:
            if self.target.state == TruckState.BLASTING_IDLE and not in_blasting_idle:
                in_blasting_idle = True
                self.target.push_event(EventType.BLASTING_IDLE_BEGIN, write_event=False)
            elif self.target.state != TruckState.BLASTING_IDLE and in_blasting_idle:
                in_blasting_idle = False
                self.target.push_event(EventType.BLASTING_IDLE_END, write_event=False)

            yield self.env.timeout(1)


class ShovelBlastingWatcher(BaseBehavior):
    """
        Класс для экскаватора (Shovel).
        Отслеживает наличие хотя бы одного возможного маршрута хотя бы до одного ПРа.
        Если ни одного маршрута нет - исключаем экскаватора из планировщика.
        Как только появится хотя бы один маршрут - добавим экскаватор в планировщик.
    """

    def __init__(self, target):
        super().__init__(target)

    def wait_blasting_changing(self):
        # запоминаем активные зоны
        remember_zones = {blasting.id for blasting in self.target.quarry.active_blasting}

        # Если активные зоны взрывных работ не изменились,
        # тогда стоим и ждём, пока зоны поменяются, чтобы заново проверять возможность проезда
        while remember_zones == {blasting.id for blasting in self.target.quarry.active_blasting}:
            yield self.env.timeout(1)

    def run(self):
        while True:
            safe_path_exist = False  # существуют ли пути в объезд взрывных зон
            for unload in self.target.quarry.unload_map.values():
                polygons = [zone for blasting in self.target.quarry.active_blasting for zone in blasting.zones]

                # Сборка всех возможных маршрутов между пунктом отправления и пункт назначения
                paths = find_all_route_edges_by_road_net_from_object_to_object(
                    from_object_id=self.target.id,
                    from_object_type=ObjectType.SHOVEL,
                    to_object_id=unload.id,
                    to_object_type=ObjectType.UNLOAD,
                    road_net=self.target.quarry.sim_data.road_net,
                )

                # Маршруты отсортированы по длине, выберем первый, не попадающий в полигоны взрывных работ
                for path in paths:
                    if not path_intersects_polygons(path, polygons):
                        safe_path_exist = True
                        break

                if safe_path_exist:
                    break

            # Проверяем наличие безопасных маршрутов и факт нахождения в ожидании взрывных работ
            if not safe_path_exist and not self.target.in_blasting_idle:
                self.target.in_blasting_idle = True
                self.target.push_event(EventType.BLASTING_IDLE_BEGIN, write_event=False)
            elif safe_path_exist and self.target.in_blasting_idle:
                self.target.in_blasting_idle = False
                self.target.push_event(EventType.BLASTING_IDLE_END, write_event=False)

            yield from self.wait_blasting_changing()

            yield self.env.timeout(1)


class UnloadBlastingWatcher(BaseBehavior):
    """
        Класс для пункта разгрузки (Unload).
        Отслеживает наличие хотя бы одного возможного маршрута хотя бы до одного экскаватора.
        Если ни одного маршрута нет - исключаем пункт разгрузки из планировщика.
        Как только появится хотя бы один маршрут - добавим пункт разгрузки в планировщик.
    """

    def __init__(self, target):
        super().__init__(target)

    def wait_blasting_changing(self):
        # запоминаем активные зоны
        remember_zones = {blasting.id for blasting in self.target.quarry.active_blasting}

        # Если активные зоны взрывных работ не изменились,
        # тогда стоим и ждём, пока зоны поменяются, чтобы заново проверять возможность проезда
        while remember_zones == {blasting.id for blasting in self.target.quarry.active_blasting}:
            yield self.env.timeout(1)

    def run(self):
        while True:
            safe_path_exist = False  # существуют ли пути в объезд взрывных зон
            for shovel in self.target.quarry.shovel_map.values():
                polygons = [zone for blasting in self.target.quarry.active_blasting for zone in blasting.zones]

                # Сборка всех возможных маршрутов между пунктом отправления и пункт назнчения
                paths = find_all_route_edges_by_road_net_from_object_to_object(
                    from_object_id=self.target.id,
                    from_object_type=ObjectType.UNLOAD,
                    to_object_id=shovel.id,
                    to_object_type=ObjectType.SHOVEL,
                    road_net=self.target.quarry.sim_data.road_net,
                )

                # Маршруты отсортированы по длине, выберем первый, не попадающий в полигоны взрывных работ
                for path in paths:
                    if not path_intersects_polygons(path, polygons):
                        safe_path_exist = True
                        break

                if safe_path_exist:
                    break

            # Проверяем наличие безопасных маршрутов и факт нахождения в ожидании взрывных работ
            if not safe_path_exist and not self.target.in_blasting_idle:
                self.target.in_blasting_idle = True
                self.target.push_event(EventType.BLASTING_IDLE_BEGIN, write_event=False)
            elif safe_path_exist and self.target.in_blasting_idle:
                self.target.in_blasting_idle = False
                self.target.push_event(EventType.BLASTING_IDLE_END, write_event=False)

            yield from self.wait_blasting_changing()

            yield self.env.timeout(1)
