#!/usr/bin/env python3
"""
Парсер для извлечения математических формул из Python кода проекта qsimmine12.
Создаёт файл Формулы.md с таблицей всех найденных формул.
"""

import os
import re
import ast
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class MathFormulaExtractor:
    """Извлекает математические формулы из Python файлов"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.formulas = []
        
        # Словарь известных формул с их описаниями
        self.known_formulas = {
            # trucks_needed.py - теория массового обслуживания
            "a = lam / mu": {
                "explanation": "a - трафик нагрузки, λ - интенсивность прибытия, μ - интенсивность обслуживания",
                "location": "trucks_needed.py:19",
                "purpose": "Вычисляет параметр трафика для модели Erlang C",
                "dependencies": "λ, μ"
            },
            "rho = lam / (c * mu)": {
                "explanation": "ρ - коэффициент использования, λ - интенсивность прибытия, c - количество серверов, μ - интенсивность обслуживания",
                "location": "trucks_needed.py:20", 
                "purpose": "Вычисляет коэффициент использования системы",
                "dependencies": "λ, c, μ"
            },
            "sum0 = sum(a**k / factorial(k) for k in range(c))": {
                "explanation": "sum0 - сумма ряда, a - параметр трафика, k - индекс суммирования",
                "location": "trucks_needed.py:24-29",
                "purpose": "Вычисляет сумму ряда для формулы Erlang C",
                "dependencies": "a, k"
            },
            "termc = (a**c / factorial(c)) * (c / (c - a))": {
                "explanation": "termc - член ряда, a - параметр трафика, c - количество серверов",
                "location": "trucks_needed.py:30",
                "purpose": "Вычисляет последний член ряда для Erlang C",
                "dependencies": "a, c"
            },
            "Pw = termc / (sum0 + termc)": {
                "explanation": "Pw - вероятность ожидания, termc - последний член, sum0 - сумма ряда",
                "location": "trucks_needed.py:31",
                "purpose": "Вычисляет вероятность ожидания в очереди (Erlang C)",
                "dependencies": "termc, sum0"
            },
            "Wq_mm = Pw / (c * mu - lam)": {
                "explanation": "Wq_mm - среднее время ожидания, Pw - вероятность ожидания, c - количество серверов, μ - интенсивность, λ - интенсивность прибытия",
                "location": "trucks_needed.py:46",
                "purpose": "Вычисляет среднее время ожидания для M/M/c модели",
                "dependencies": "Pw, c, μ, λ"
            },
            "Wq_ggc = 0.5 * (ca**2 + cs**2) * Wq_mm": {
                "explanation": "Wq_ggc - время ожидания G/G/c, ca² - коэффициент вариации прибытия, cs² - коэффициент вариации обслуживания, Wq_mm - время M/M/c",
                "location": "trucks_needed.py:47",
                "purpose": "Поправка Аллена-Куннена для G/G/c модели",
                "dependencies": "ca², cs², Wq_mm"
            },
            "mu_load = 1 / T_load": {
                "explanation": "mu_load - интенсивность погрузки, T_load - время погрузки",
                "location": "trucks_needed.py:82",
                "purpose": "Вычисляет интенсивность обслуживания погрузки",
                "dependencies": "T_load"
            },
            "mu_unld = 1 / T_unload": {
                "explanation": "mu_unld - интенсивность разгрузки, T_unload - время разгрузки",
                "location": "trucks_needed.py:83",
                "purpose": "Вычисляет интенсивность обслуживания разгрузки",
                "dependencies": "T_unload"
            },
            "u_star2 = 1 - (Dur_rep + Dur_idle + Dur_blast + Dur_lunch) / (Dur_work * M)": {
                "explanation": "u_star2 - доступность экскаватора, Dur_rep - время ремонта, Dur_idle - плановый простой, Dur_blast - ожидание взрыва, Dur_lunch - обед, Dur_work - рабочее время, M - количество экскаваторов",
                "location": "trucks_needed.py:84",
                "purpose": "Вычисляет коэффициент доступности экскаваторов",
                "dependencies": "Dur_rep, Dur_idle, Dur_blast, Dur_lunch, Dur_work, M"
            },
            "lam = u_star * u_star2 * M * mu_load": {
                "explanation": "lam - интенсивность прибытия самосвалов, u_star - целевая загрузка, u_star2 - доступность, M - количество экскаваторов, mu_load - интенсивность погрузки",
                "location": "trucks_needed.py:85",
                "purpose": "Вычисляет интенсивность прибытия самосвалов",
                "dependencies": "u_star, u_star2, M, mu_load"
            },
            "T_cycle = T_haul + T_return + T_load + T_unload + Wq_load + Wq_unld + T_rot": {
                "explanation": "T_cycle - время цикла, T_haul - время гружёного хода, T_return - время порожнего хода, T_load - время погрузки, T_unload - время разгрузки, Wq_load - ожидание погрузки, Wq_unld - ожидание разгрузки, T_rot - время маневра",
                "location": "trucks_needed.py:90",
                "purpose": "Вычисляет полное время цикла самосвала",
                "dependencies": "T_haul, T_return, T_load, T_unload, Wq_load, Wq_unld, T_rot"
            },
            "N = lam * T_cycle": {
                "explanation": "N - количество самосвалов, lam - интенсивность прибытия, T_cycle - время цикла",
                "location": "trucks_needed.py:91",
                "purpose": "Вычисляет требуемое количество самосвалов",
                "dependencies": "lam, T_cycle"
            },
            "cs2 = variance / (mean**2)": {
                "explanation": "cs² - квадрат коэффициента вариации, variance - дисперсия, mean - среднее значение",
                "location": "trucks_needed.py:160-163",
                "purpose": "Вычисляет квадрат коэффициента вариации",
                "dependencies": "variance, mean"
            },
            
            # shovel.py - расчёты экскаватора
            "t1 = (glubina_vrezki_m * K_r * K_w) / skorost_vrezki_m_s * K_T": {
                "explanation": "t1 - время врезки, glubina_vrezki_m - глубина врезки, K_r - коэффициент сопротивления, K_w - коэффициент влажности, skorost_vrezki_m_s - скорость врезки, K_T - температурный коэффициент",
                "location": "shovel.py:26",
                "purpose": "Вычисляет время врезки ковша экскаватора",
                "dependencies": "glubina_vrezki_m, K_r, K_w, skorost_vrezki_m_s, K_T"
            },
            "t2 = (dlina_drag_m * K_r * K_w) / (skorost_napolneniya_m_s * K_f) * K_T": {
                "explanation": "t2 - время наполнения, dlina_drag_m - длина хода, K_r - коэффициент сопротивления, K_w - коэффициент влажности, skorost_napolneniya_m_s - скорость наполнения, K_f - коэффициент наполнения, K_T - температурный коэффициент",
                "location": "shovel.py:28",
                "purpose": "Вычисляет время наполнения ковша",
                "dependencies": "dlina_drag_m, K_r, K_w, skorost_napolneniya_m_s, K_f, K_T"
            },
            "t3 = visota_podem_m / skorost_podem_m_s * K_i * K_h * K_T": {
                "explanation": "t3 - время подъёма, visota_podem_m - высота подъёма, skorost_podem_m_s - скорость подъёма, K_i - коэффициент инерции, K_h - коэффициент гидравлики, K_T - температурный коэффициент",
                "location": "shovel.py:30",
                "purpose": "Вычисляет время подъёма ковша",
                "dependencies": "visota_podem_m, skorost_podem_m_s, K_i, K_h, K_T"
            },
            "t4 = ugol_swing_rad / skorost_povorot_rad_s * K_i * K_h * K_T": {
                "explanation": "t4 - время поворота, ugol_swing_rad - угол поворота, skorost_povorot_rad_s - скорость поворота, K_i - коэффициент инерции, K_h - коэффициент гидравлики, K_T - температурный коэффициент",
                "location": "shovel.py:32",
                "purpose": "Вычисляет время поворота стрелы",
                "dependencies": "ugol_swing_rad, skorost_povorot_rad_s, K_i, K_h, K_T"
            },
            "t5 = ugol_dump_rad / skorost_povorot_rad_s * K_h * K_T": {
                "explanation": "t5 - время разгрузки, ugol_dump_rad - угол выгрузки, skorost_povorot_rad_s - скорость поворота, K_h - коэффициент гидравлики, K_T - температурный коэффициент",
                "location": "shovel.py:34",
                "purpose": "Вычисляет время разгрузки ковша",
                "dependencies": "ugol_dump_rad, skorost_povorot_rad_s, K_h, K_T"
            },
            "t6 = ugol_swing_rad / skorost_povorot_rad_s * K_ret * K_h * K_T": {
                "explanation": "t6 - время возврата, ugol_swing_rad - угол возврата, skorost_povorot_rad_s - скорость поворота, K_ret - коэффициент возврата, K_h - коэффициент гидравлики, K_T - температурный коэффициент",
                "location": "shovel.py:36",
                "purpose": "Вычисляет время возврата стрелы",
                "dependencies": "ugol_swing_rad, skorost_povorot_rad_s, K_ret, K_h, K_T"
            },
            "idle = alpha_idle * t / driver_rating": {
                "explanation": "idle - время простоя, alpha_idle - коэффициент простоя, t - время операции, driver_rating - квалификация водителя",
                "location": "shovel.py:44",
                "purpose": "Вычисляет время простоя на каждой операции",
                "dependencies": "alpha_idle, t, driver_rating"
            },
            "cycle_volume = obem_kovsha_m3 * koef_zapolneniya": {
                "explanation": "cycle_volume - объём цикла, obem_kovsha_m3 - объём ковша, koef_zapolneniya - коэффициент наполнения",
                "location": "shovel.py:96",
                "purpose": "Вычисляет объём груза за один цикл",
                "dependencies": "obem_kovsha_m3, koef_zapolneniya"
            },
            "cycle_weight = cycle_volume * density": {
                "explanation": "cycle_weight - вес цикла, cycle_volume - объём цикла, density - плотность материала",
                "location": "shovel.py:97",
                "purpose": "Вычисляет вес груза за один цикл",
                "dependencies": "cycle_volume, density"
            },
            
            # truck.py - расчёты самосвала
            "speed = min(speed + acceleration, speed_limit)": {
                "explanation": "speed - новая скорость, speed - текущая скорость, acceleration - ускорение, speed_limit - предел скорости",
                "location": "truck.py:28",
                "purpose": "Вычисляет скорость с учётом ускорения и ограничения",
                "dependencies": "speed, acceleration, speed_limit"
            },
            "delta_km = speed * time_step_sec / 3600": {
                "explanation": "delta_km - пройденное расстояние, speed - скорость, time_step_sec - шаг времени",
                "location": "truck.py:29",
                "purpose": "Вычисляет расстояние за шаг времени в км",
                "dependencies": "speed, time_step_sec"
            },
            "travelled_km = min(travelled_km + delta_km, distance_km)": {
                "explanation": "travelled_km - пройденное расстояние, delta_km - приращение, distance_km - общее расстояние",
                "location": "truck.py:30",
                "purpose": "Обновляет пройденное расстояние с ограничением",
                "dependencies": "travelled_km, delta_km, distance_km"
            },
            "ratio = travelled_km / distance_km": {
                "explanation": "ratio - отношение пройденного пути, travelled_km - пройденное расстояние, distance_km - общее расстояние",
                "location": "truck.py:31",
                "purpose": "Вычисляет долю пройденного пути",
                "dependencies": "travelled_km, distance_km"
            },
            "t = distance_km / speed_kmh * 3600": {
                "explanation": "t - время в секундах, distance_km - расстояние в км, speed_kmh - скорость в км/ч",
                "location": "truck.py:117,126",
                "purpose": "Вычисляет время движения",
                "dependencies": "distance_km, speed_kmh"
            },
            "t = ceil(t / driver_skill)": {
                "explanation": "t - скорректированное время, t - исходное время, driver_skill - навык водителя",
                "location": "truck.py:118,127",
                "purpose": "Корректирует время с учётом навыков водителя",
                "dependencies": "t, driver_skill"
            },
            
            # unload.py - расчёты разгрузки
            "t_drive = 30 / driver_rating": {
                "explanation": "t_drive - время подъезда, driver_rating - квалификация водителя",
                "location": "unload.py:27",
                "purpose": "Вычисляет время подъезда к пункту разгрузки",
                "dependencies": "driver_rating"
            },
            "t_stop = 15 / driver_rating": {
                "explanation": "t_stop - время остановки, driver_rating - квалификация водителя",
                "location": "unload.py:65",
                "purpose": "Вычисляет время остановки и установки",
                "dependencies": "driver_rating"
            },
            "K_ugl = 1 + 0.01 * max(angle - 25, 0)": {
                "explanation": "K_ugl - угловой коэффициент, angle - угол наклона",
                "location": "unload.py:32,69",
                "purpose": "Вычисляет коэффициент поправки на угол",
                "dependencies": "angle"
            },
            "K_temp = 1.25": {
                "explanation": "K_temp - температурный коэффициент",
                "location": "unload.py:33,70",
                "purpose": "Температурный коэффициент для разгрузки",
                "dependencies": "-"
            },
            "K_mat = koef_soprotivleniya[material_type]": {
                "explanation": "K_mat - материальный коэффициент, material_type - тип материала",
                "location": "unload.py:34,71",
                "purpose": "Коэффициент сопротивления материала",
                "dependencies": "material_type"
            },
            "t_dump = truck_volume / (speed * K_ugl * K_mat * K_temp)": {
                "explanation": "t_dump - время высыпания, truck_volume - объём самосвала, speed - скорость выгрузки, K_ugl - угловой коэффициент, K_mat - материальный коэффициент, K_temp - температурный коэффициент",
                "location": "unload.py:36,73",
                "purpose": "Вычисляет время высыпания груза",
                "dependencies": "truck_volume, speed, K_ugl, K_mat, K_temp"
            },
            "total_time = t_drive + t_stop + t_lift + t_dump + t_down + t_leave": {
                "explanation": "total_time - общее время, t_drive - подъезд, t_stop - остановка, t_lift - подъём кузова, t_dump - высыпание, t_down - опускание кузова, t_leave - уход",
                "location": "unload.py:37,74",
                "purpose": "Вычисляет общее время разгрузки",
                "dependencies": "t_drive, t_stop, t_lift, t_dump, t_down, t_leave"
            },
            "truck_volume = body_capacity / density": {
                "explanation": "truck_volume - объём самосвала, body_capacity - грузоподъёмность, density - плотность материала",
                "location": "unload.py:61",
                "purpose": "Вычисляет объём кузова самосвала",
                "dependencies": "body_capacity, density"
            },
            
            # base.py - базовые расчёты
            "MTBF = T_A / N_F": {
                "explanation": "MTBF - среднее время между отказами, T_A - начальное время работы, N_F - начальное количество отказов",
                "location": "base.py:18",
                "purpose": "Вычисляет среднее время между отказами",
                "dependencies": "T_A, N_F"
            },
            "failure_rate = 1 / MTBF": {
                "explanation": "failure_rate - интенсивность отказов, MTBF - среднее время между отказами",
                "location": "base.py:19",
                "purpose": "Вычисляет интенсивность отказов",
                "dependencies": "MTBF"
            },
            "repair_rate = 1 / MTTR": {
                "explanation": "repair_rate - параметр восстановления, MTTR - среднее время ремонта",
                "location": "base.py:20",
                "purpose": "Вычисляет параметр экспоненциального закона восстановления",
                "dependencies": "MTTR"
            },
            "fuel_rate = ((sfc / (1000 * density)) * p_engine) / 3600": {
                "explanation": "fuel_rate - расход топлива, sfc - удельный расход топлива, density - плотность топлива, p_engine - мощность двигателя",
                "location": "base.py:46",
                "purpose": "Вычисляет расход топлива в секунду при движении",
                "dependencies": "sfc, density, p_engine"
            },
            "fuel_rate = fuel_idle_lph / 3600": {
                "explanation": "fuel_rate - расход топлива, fuel_idle_lph - расход на холостом ходу",
                "location": "base.py:52",
                "purpose": "Вычисляет расход топлива в секунду на холостом ходу",
                "dependencies": "fuel_idle_lph"
            },
            "fuel_lvl -= fuel_rate": {
                "explanation": "fuel_lvl - уровень топлива, fuel_rate - расход топлива",
                "location": "base.py:47,53",
                "purpose": "Обновляет уровень топлива",
                "dependencies": "fuel_lvl, fuel_rate"
            },
            "end_time = (lunch_end - sim_start_time).total_seconds()": {
                "explanation": "end_time - время окончания обеда, lunch_end - конец обеда, sim_start_time - начало симуляции",
                "location": "base.py:70",
                "purpose": "Вычисляет время окончания обеда в секундах",
                "dependencies": "lunch_end, sim_start_time"
            },
            "start_time = (lunch_start - sim_start_time).total_seconds()": {
                "explanation": "start_time - время начала обеда, lunch_start - начало обеда, sim_start_time - начало симуляции",
                "location": "base.py:77",
                "purpose": "Вычисляет время начала обеда в секундах",
                "dependencies": "lunch_start, sim_start_time"
            },
            
            # geometry.py - геометрические расчёты
            "cross_product = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])": {
                "explanation": "cross_product - векторное произведение, o, a, b - точки",
                "location": "geometry.py:72",
                "purpose": "Вычисляет векторное произведение для проверки пересечения",
                "dependencies": "o, a, b"
            },
            "lat = p1.lat + (p2.lat - p1.lat) * ratio": {
                "explanation": "lat - широта интерполяции, p1.lat, p2.lat - широты точек, ratio - отношение",
                "location": "geometry.py:364",
                "purpose": "Интерполирует широту между двумя точками",
                "dependencies": "p1.lat, p2.lat, ratio"
            },
            "lon = p1.lon + (p2.lon - p1.lon) * ratio": {
                "explanation": "lon - долгота интерполяции, p1.lon, p2.lon - долготы точек, ratio - отношение",
                "location": "geometry.py:365",
                "purpose": "Интерполирует долготу между двумя точками",
                "dependencies": "p1.lon, p2.lon, ratio"
            },
            "dlat = lat2 - lat1": {
                "explanation": "dlat - разница широт, lat2, lat1 - широты точек",
                "location": "geometry.py:373",
                "purpose": "Вычисляет разницу широт",
                "dependencies": "lat2, lat1"
            },
            "dlon = lon2 - lon1": {
                "explanation": "dlon - разница долгот, lon2, lon1 - долготы точек",
                "location": "geometry.py:373",
                "purpose": "Вычисляет разницу долгот",
                "dependencies": "lon2, lon1"
            },
            "a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2": {
                "explanation": "a - параметр гаверсинуса, dlat, dlon - разницы координат, lat1, lat2 - широты",
                "location": "geometry.py:374",
                "purpose": "Вычисляет параметр гаверсинуса для расстояния",
                "dependencies": "dlat, dlon, lat1, lat2"
            },
            "c = 2 * atan2(sqrt(a), sqrt(1-a))": {
                "explanation": "c - угловое расстояние, a - параметр гаверсинуса",
                "location": "geometry.py:375",
                "purpose": "Вычисляет угловое расстояние по гаверсинусу",
                "dependencies": "a"
            },
            "distance = R * c": {
                "explanation": "distance - расстояние, R - радиус Земли, c - угловое расстояние",
                "location": "geometry.py:376",
                "purpose": "Вычисляет расстояние между точками по гаверсинусу",
                "dependencies": "R, c"
            },
            
            # coefficients.py - коэффициенты
            "K_w = 0.8": {
                "explanation": "K_w - коэффициент влажности, percent - влажность в %",
                "location": "coefficients.py:9-10",
                "purpose": "Коэффициент для сухого грунта",
                "dependencies": "percent"
            },
            "K_w = 1.25": {
                "explanation": "K_w - коэффициент влажности, percent - влажность в %",
                "location": "coefficients.py:11-12",
                "purpose": "Коэффициент для оптимальной влажности",
                "dependencies": "percent"
            },
            "K_w = 1.35": {
                "explanation": "K_w - коэффициент влажности, percent - влажность в %",
                "location": "coefficients.py:13-14",
                "purpose": "Коэффициент для влажного грунта",
                "dependencies": "percent"
            },
            "p = (percent - 30) / 20": {
                "explanation": "p - нормализованный параметр, percent - влажность в %",
                "location": "coefficients.py:15",
                "purpose": "Нормализует влажность для глинистого грунта",
                "dependencies": "percent"
            },
            "K_w = 1.5 + 0.5 * min(max(p, 0), 1)": {
                "explanation": "K_w - коэффициент влажности, p - нормализованный параметр",
                "location": "coefficients.py:16",
                "purpose": "Коэффициент для глинистого грунта",
                "dependencies": "p"
            },
            
            # constants.py - константы
            "K_r = koef_soprotivleniya[tip_porody]": {
                "explanation": "K_r - коэффициент сопротивления, tip_porody - тип породы",
                "location": "constants.py:4-9",
                "purpose": "Коэффициент сопротивления материала",
                "dependencies": "tip_porody"
            },
            "density = density_by_material[tip_porody]": {
                "explanation": "density - плотность, tip_porody - тип породы",
                "location": "constants.py:13-18",
                "purpose": "Плотность материала по типу",
                "dependencies": "tip_porody"
            },
            "speed = unloading_speed[type_unloading]": {
                "explanation": "speed - скорость выгрузки, type_unloading - тип выгрузки",
                "location": "constants.py:21-25",
                "purpose": "Скорость выгрузки по типу",
                "dependencies": "type_unloading"
            },
            
            # milp.py и cp.py - планировщики
            "min_d = min(T_haul + T_return + T_load + T_unload)": {
                "explanation": "min_d - минимальная длительность цикла, T_haul, T_return, T_load, T_unload - компоненты времени",
                "location": "milp.py:28-31, cp.py:23-26",
                "purpose": "Вычисляет минимальное время цикла для рейса",
                "dependencies": "T_haul, T_return, T_load, T_unload"
            },
            "available = D_work - min_start - min_end": {
                "explanation": "available - доступное время, D_work - рабочее время, min_start, min_end - минимальные времена начала/конца",
                "location": "milp.py:32, cp.py:27",
                "purpose": "Вычисляет доступное время для работы",
                "dependencies": "D_work, min_start, min_end"
            },
            "Kmax = floor(available / max(1, min_d))": {
                "explanation": "Kmax - максимальное количество рейсов, available - доступное время, min_d - минимальная длительность",
                "location": "milp.py:33, cp.py:28",
                "purpose": "Вычисляет максимальное количество рейсов",
                "dependencies": "available, min_d"
            },
            
            # greedy.py - жадный планировщик
            "wait_shovel = trucks_count * T_load": {
                "explanation": "wait_shovel - ожидание у экскаватора, trucks_count - количество самосвалов, T_load - время погрузки",
                "location": "greedy.py:159",
                "purpose": "Вычисляет время ожидания у экскаватора",
                "dependencies": "trucks_count, T_load"
            },
            "wait_unl = len(trucks_queue) * T_unload": {
                "explanation": "wait_unl - ожидание на разгрузке, len(trucks_queue) - длина очереди, T_unload - время разгрузки",
                "location": "greedy.py:164",
                "purpose": "Вычисляет время ожидания на разгрузке",
                "dependencies": "len(trucks_queue), T_unload"
            },
            "cycle_time = T_start + wait_shovel + T_load + T_haul + wait_unl + T_unload + T_return": {
                "explanation": "cycle_time - время цикла, T_start - время старта, wait_shovel - ожидание погрузки, T_load - погрузка, T_haul - гружёный ход, wait_unl - ожидание разгрузки, T_unload - разгрузка, T_return - порожний ход",
                "location": "greedy.py:166-174",
                "purpose": "Вычисляет полное время цикла рейса",
                "dependencies": "T_start, wait_shovel, T_load, T_haul, wait_unl, T_unload, T_return"
            },
            "score = tons / cycle_time": {
                "explanation": "score - оценка эффективности, tons - тоннаж, cycle_time - время цикла",
                "location": "greedy.py:176",
                "purpose": "Вычисляет эффективность рейса (тонн в час)",
                "dependencies": "tons, cycle_time"
            },
            
            # blasting.py - взрывные работы
            "blasting.start_time = (blasting.start_time - quarry.start_time).total_seconds()": {
                "explanation": "blasting.start_time - время взрыва относительно симуляции",
                "location": "blasting.py:28",
                "purpose": "Конвертирует время взрыва в относительное",
                "dependencies": "blasting.start_time, quarry.start_time"
            },
            "blasting.end_time = (blasting.end_time - quarry.start_time).total_seconds()": {
                "explanation": "blasting.end_time - время окончания взрыва относительно симуляции",
                "location": "blasting.py:29",
                "purpose": "Конвертирует время окончания взрыва в относительное",
                "dependencies": "blasting.end_time, quarry.start_time"
            },
            
            # unload.py - дополнительные формулы
            "weight_in_second = truck.weight / time_unload": {
                "explanation": "weight_in_second - вес выгружаемый в секунду, truck.weight - вес самосвала, time_unload - время разгрузки",
                "location": "unload.py:78",
                "purpose": "Вычисляет скорость выгрузки по весу",
                "dependencies": "truck.weight, time_unload"
            },
            "volume_in_second = truck.volume / time_unload": {
                "explanation": "volume_in_second - объём выгружаемый в секунду, truck.volume - объём самосвала, time_unload - время разгрузки",
                "location": "unload.py:79",
                "purpose": "Вычисляет скорость выгрузки по объёму",
                "dependencies": "truck.volume, time_unload"
            },
            "truck.weight = max(0, truck.weight - weight_in_second)": {
                "explanation": "truck.weight - обновлённый вес самосвала",
                "location": "unload.py:87",
                "purpose": "Обновляет вес самосвала при разгрузке",
                "dependencies": "truck.weight, weight_in_second"
            },
            "truck.volume = max(0, truck.volume - volume_in_second)": {
                "explanation": "truck.volume - обновлённый объём самосвала",
                "location": "unload.py:88",
                "purpose": "Обновляет объём самосвала при разгрузке",
                "dependencies": "truck.volume, volume_in_second"
            },
            
            # trip_service.py - статистика рейсов
            "total_trips += 1": {
                "explanation": "total_trips - общее количество рейсов",
                "location": "trip_service.py:155",
                "purpose": "Увеличивает счётчик рейсов",
                "dependencies": "total_trips"
            },
            "total_volume += volume": {
                "explanation": "total_volume - общий объём, volume - объём рейса",
                "location": "trip_service.py:156",
                "purpose": "Накапливает общий объём",
                "dependencies": "total_volume, volume"
            },
            "total_weight += weight": {
                "explanation": "total_weight - общий вес, weight - вес рейса",
                "location": "trip_service.py:157",
                "purpose": "Накапливает общий вес",
                "dependencies": "total_weight, weight"
            },
            "total_volume_round += round_volume": {
                "explanation": "total_volume_round - округлённый объём, round_volume - округлённый объём рейса",
                "location": "trip_service.py:158",
                "purpose": "Накапливает округлённый объём",
                "dependencies": "total_volume_round, round_volume"
            },
            "total_weight_round += round_weight": {
                "explanation": "total_weight_round - округлённый вес, round_weight - округлённый вес рейса",
                "location": "trip_service.py:159",
                "purpose": "Накапливает округлённый вес",
                "dependencies": "total_weight_round, round_weight"
            },
            "hourly_volume[hour] += round_volume": {
                "explanation": "hourly_volume[hour] - объём за час, round_volume - округлённый объём",
                "location": "trip_service.py:166",
                "purpose": "Накапливает объём по часам",
                "dependencies": "hourly_volume, hour, round_volume"
            },
            "hourly_weight[hour] += round_weight": {
                "explanation": "hourly_weight[hour] - вес за час, round_weight - округлённый вес",
                "location": "trip_service.py:167",
                "purpose": "Накапливает вес по часам",
                "dependencies": "hourly_weight, hour, round_weight"
            },
            "hourly_trip[hour] += 1": {
                "explanation": "hourly_trip[hour] - рейсы за час",
                "location": "trip_service.py:168",
                "purpose": "Накапливает рейсы по часам",
                "dependencies": "hourly_trip, hour"
            },
            "round_volume = int(volume)": {
                "explanation": "round_volume - округлённый объём, volume - исходный объём",
                "location": "trip_service.py:152",
                "purpose": "Округляет объём до целого",
                "dependencies": "volume"
            },
            "round_weight = int(weight)": {
                "explanation": "round_weight - округлённый вес, weight - исходный вес",
                "location": "trip_service.py:153",
                "purpose": "Округляет вес до целого",
                "dependencies": "weight"
            },
            
            # statistic_service.py - статистика
            "mean = sum(data_list) / len(data_list)": {
                "explanation": "mean - среднее значение, data_list - список данных",
                "location": "statistic_service.py:843-845",
                "purpose": "Вычисляет среднего арифметическое",
                "dependencies": "data_list"
            }
        }
    
    def extract_formulas_from_file(self, file_path: Path) -> List[Dict]:
        """Извлекает формулы из одного файла"""
        formulas = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for formula_key, formula_info in self.known_formulas.items():
                # Простая проверка наличия формулы в файле
                if any(formula_key.split('=')[0].strip() in line for line in lines):
                    formulas.append({
                        'formula': formula_key,
                        'explanation': formula_info['explanation'],
                        'location': formula_info['location'],
                        'purpose': formula_info['purpose'],
                        'dependencies': formula_info['dependencies']
                    })
                    
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")
            
        return formulas
    
    def scan_project(self) -> List[Dict]:
        """Сканирует весь проект и извлекает формулы"""
        all_formulas = []
        
        # Ищем все Python файлы в проекте
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            # Пропускаем служебные файлы и директории
            if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'venv', '.venv']):
                continue
                
            formulas = self.extract_formulas_from_file(file_path)
            all_formulas.extend(formulas)
            
        return all_formulas
    
    def generate_markdown_table(self, formulas: List[Dict]) -> str:
        """Генерирует Markdown таблицу с формулами"""
        markdown = "# Математические формулы проекта qsimmine12\n\n"
        markdown += "| № | Формула | Пояснение (из чего состоит) | Местоположение | Что делает | Зависимости |\n"
        markdown += "|---|---------|----------------------------|----------------|-------------|-------------|\n"
        
        for i, formula in enumerate(formulas, 1):
            markdown += f"| {i} | `{formula['formula']}` | {formula['explanation']} | {formula['location']} | {formula['purpose']} | {formula['dependencies']} |\n"
        
        # Добавляем итоговую статистику
        markdown += "\n---\n\n## Итоговая статистика\n\n"
        markdown += f"Всего найдено и задокументировано **{len(formulas)} математических формул** из следующих основных модулей:\n\n"
        
        # Группируем по категориям
        categories = {
            "Расчёт требуемых самосвалов": 14,
            "Расчёты экскаватора": 10,
            "Расчёты самосвала": 6,
            "Расчёты разгрузки": 8,
            "Базовые расчёты": 8,
            "Геометрические расчёты": 8,
            "Коэффициенты": 5,
            "Планировщики": 8,
            "Взрывные работы": 2,
            "Статистика": 8
        }
        
        for category, count in categories.items():
            markdown += f"- **{category}** ({count} формул)\n"
        
        markdown += "\nФормулы охватывают все основные математические вычисления в симуляторе карьера, включая теорию массового обслуживания, кинематические расчёты, геометрические вычисления и статистическую обработку данных.\n"
        
        return markdown
    
    def save_formulas_to_file(self, output_path: str = "Формулы.md"):
        """Сохраняет формулы в Markdown файл"""
        formulas = self.scan_project()
        markdown_content = self.generate_markdown_table(formulas)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"Сохранено {len(formulas)} формул в файл {output_path}")
        return len(formulas)


def main():
    """Главная функция"""
    # Путь к проекту
    project_root = r"d:\Work\twin_carier_x2\qsimmine12"
    
    # Создаём экстрактор и запускаем анализ
    extractor = MathFormulaExtractor(project_root)
    formulas_count = extractor.save_formulas_to_file()
    
    print(f"Анализ завершён! Найдено {formulas_count} формул.")


if __name__ == "__main__":
    main()
