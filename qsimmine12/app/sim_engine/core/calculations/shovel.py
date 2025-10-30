from typing import Tuple, Generator

import numpy as np

from app.sim_engine.core.coefficients import koef_vlazhnosti
from app.sim_engine.core.constants import koef_soprotivleniya, density_by_material
from app.sim_engine.core.props import ShovelProperties, TruckProperties


class ShovelCalc:

    @classmethod
    def calculate_cycle(
        cls,
        props: ShovelProperties,
        glubina_vrezki_m=0.3, dlina_drag_m=2.0,
        visota_podem_m=3.0, ugol_swing_rad=np.pi/2,
        ugol_dump_rad=np.pi/6, alpha_idle=0.3
    ) -> dict:
        """
        Расчёт времён всех стадий одного цикла работы Экскаватора
        ждём самосвал, наполняем ковш, поворачиваемся, грузим и всё с самого начала
        """
        k = cls.get_koef(props)
        # ВРЕЗКА КОВША (Глубина * Коэф. сопротивления * Коэф. влажности) / Скорость * Коэф. температуры
        t1 = (glubina_vrezki_m * k['K_r'] * k['K_w']) / props.skorost_vrezki_m_s * k['K_T']
        # 2. НАПОЛНЕНИЕ КОВША  (Длина хода * Коэф. сопротивления * Коэф. влажности) / (Скорость * Коэф. наполнения) * Коэф. температуры
        t2 = (dlina_drag_m * k['K_r'] * k['K_w']) / (props.skorost_napolneniya_m_s * k['K_f']) * k['K_T']
        # 3. ПОДЪЁМ КОВША Высота / Скорость * Коэф. инерции * Коэф. гидравлики * Коэф. температуры
        t3 = visota_podem_m / props.skorost_podem_m_s * k['K_i'] * k['K_h'] * k['K_T']
        # 4. ПОВОРОТ СТРЕЛЫ Угол / Скорость * Коэф. инерции * Коэф. гидравлики * Коэф. температуры
        t4 = ugol_swing_rad / props.skorost_povorot_rad_s * k['K_i'] * k['K_h'] * k['K_T']
        # 5. РАЗГРУЗКА Угол выгрузки / Скорость * Коэф. гидравлики * Коэф. температуры
        t5 = ugol_dump_rad / props.skorost_povorot_rad_s * k['K_h'] * k['K_T']
        # 6. ВОЗВРАТ Угол / Скорость * Коэф. возврата * Коэф. гидравлики * Коэф. температуры
        t6 = ugol_swing_rad / props.skorost_povorot_rad_s * k['K_ret'] * k['K_h'] * k['K_T']

        Kw = 1
        driver_rating = 1

        t1 *= Kw
        t2 *= Kw
        # Ожидания (idle) на каждой стадии  alpha_idle * t / driver_rating
        idle = lambda t: alpha_idle * t / driver_rating
        idles = [idle(t) for t in [t1, t2, t3, t4, t5, t6]]
        total_s = sum([t1, t2, t3, t4, t5, t6]) + sum(idles)
        return {
            'vrezka_s': t1, 'idle_vrezka_s': idles[0],
            'napolnenie_s': t2, 'idle_napoln_s': idles[1],
            'podem_s': t3, 'idle_podem_s': idles[2],
            'povorot_s': t4, 'idle_povorot_s': idles[3],
            'razgruzka_s': t5, 'idle_dump_s': idles[4],
            'vozvrat_s': t6, 'idle_vozv_s': idles[5],
            'K_wear': Kw, 'vsego_s': total_s
        }

    @classmethod
    def _calculate_load_cycles_generator(
            cls,
            shovel_props: ShovelProperties,
            truck_props: TruckProperties
    ) -> Generator[Tuple[int, float, float], None, None]:
        """
        Генератор циклов погрузки для заполнения самосвала.

        Последовательно рассчитывает циклы погрузки экскаватора до полного заполнения
        кузова самосвала, контролируя суммарный вес груза.

        Parameters
        ----------
        shovel_props : ShovelProperties
            Свойства экскаватора
        truck_props : TruckProperties
            Свойства самосвала

        Yields
        ------
        Tuple[int, float, float]
            Кортеж содержащий:
            - int: продолжительность цикла в секундах
            - float: вес груза в тоннах за текущий цикл
            - float: объем груза в м³ за текущий цикл

        Notes
        -----
        - Генератор останавливается, когда добавление следующего ковша превысит
          грузоподъемность самосвала
        - Используется плотность материала из глобального словаря density_by_material
        - Вес рассчитывается с учетом коэффициента заполнения ковша
        """
        density = density_by_material[shovel_props.tip_porody]
        weight = 0

        while True:
            cycle = cls.calculate_cycle(props=shovel_props)
            cycle_volume = shovel_props.obem_kovsha_m3 * shovel_props.koef_zapolneniya
            cycle_weight = cycle_volume * density

            # Проверяем, не приведёт ли добавление этого ковша к перевесу
            if weight + cycle_weight > truck_props.body_capacity:
                break

            weight += cycle_weight
            yield int(cycle["vsego_s"]), cycle_weight, cycle_volume

    @classmethod
    def calculate_load_cycles(
            cls,
            shovel_props: ShovelProperties,
            truck_props: TruckProperties
    ) -> Tuple[int, float, float]:
        """
            Рассчитывает суммарные показатели полного цикла погрузки самосвала.

            Агрегирует данные всех циклов погрузки, сгенерированных методом
            `_calculate_load_cycles_generator`, и возвращает общие итоги по времени,
            весу и объему за всю операцию погрузки одного самосвала.

            Parameters
            ----------
            shovel_props : ShovelProperties
                Свойства экскаватора
            truck_props : TruckProperties
                Свойства самосвала

            Returns
            -------
            Tuple[int, float, float]
                Кортеж содержащий:
                - int: общее время погрузки в секундах
                - float: суммарный вес груза в тоннах
                - float: суммарный объем груза в м³

            Notes
            -----
            - Метод использует генератор `_calculate_load_cycles_generator` для получения
              последовательности циклов погрузки
            - Суммирование прекращается при достижении максимальной грузоподъемности самосвала
            - Возвращаемые значения представляют полную загрузку одного самосвала
        """
        total_weight = 0
        total_volime = 0
        total_time = 0
        for time, weight, volume in cls._calculate_load_cycles_generator(shovel_props, truck_props):
            total_time += time
            total_volime += volume
            total_weight += weight
        return total_time, total_weight, total_volime

    @classmethod
    def calculate_load_cycles_cumulative_generator(
            cls,
            shovel_props: ShovelProperties,
            truck_props: TruckProperties
    ) -> Generator[Tuple[int, float, float], None, None]:
        """
            Генератор циклов погрузки с накопленными итогами.

            Последовательно выдает данные каждого цикла погрузки с кумулятивными
            (накопленными) значениями веса и объема. Позволяет отслеживать прогресс
            заполнения самосвала после каждого цикла.

            Parameters
            ----------
            shovel_props : ShovelProperties
                Свойства экскаватора для расчета циклов погрузки
            truck_props : TruckProperties
                Свойства самосвала, определяющие максимальную грузоподъемность

            Yields
            ------
            Tuple[int, float, float]
                Кортеж содержащий:
                - int: продолжительность ТЕКУЩЕГО ЦИКЛА в секундах
                - float: накопленный суммарный вес груза в тоннах (с учетом текущего цикла)
                - float: накопленный суммарный объем груза в м³ (с учетом текущего цикла)

            Notes
            -----
            - В отличие от `_calculate_load_cycles_generator`, возвращает накопленные значения
            - Полезен для анализа прогресса погрузки и построения графиков заполнения
            - ВРЕМЯ ВОЗВРАЩАЕТСЯ ДЛЯ ОТДЕЛЬНОГО ЦИКЛА, а вес и объем - кумулятивные
        """
        total_weight = 0
        total_volime = 0
        for time, weight, volume in cls._calculate_load_cycles_generator(shovel_props, truck_props):
            total_volime += volume
            total_weight += weight
            yield time, total_weight, total_volime



    @staticmethod
    def get_koef(props) -> dict:
        return {
            'K_f': props.koef_zapolneniya,
            'K_r': koef_soprotivleniya[props.tip_porody],
            'K_w': koef_vlazhnosti(props.vlazhnost_percent),
            'K_T': 1.25,
            'K_i': props.koef_inertsii,
            'K_h': props.koef_gidravliki,
            'K_ret': props.koef_vozvrata
        }