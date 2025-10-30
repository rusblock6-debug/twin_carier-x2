from app.sim_engine.core.constants import koef_soprotivleniya, unloading_speed, density_by_material
from app.sim_engine.core.props import TruckProperties, UnlProperties


class UnloadCalc:

    @classmethod
    def unload_calculation(
            cls,
            props: UnlProperties,
            truck_volume
    ):
        """
        1. t_drive — подъезд (сек), фиксированно 30 сек
        2. t_stop — остановка и установка (15 сек)
        3. t_lift — подъем кузова (20 сек)
        4. t_dump — высыпание груза:
            t_dump = V / (speed * K_угол * K_мат * K_темп)
        5. t_down — опускание кузова (15 сек)
        6. t_leave — уход (30 сек)
        потом исправлю CHANGE
        длина участка для маневра
        средняя скорость маневра
        замедление
        """
        driver_rating = 1
        t_drive = 30 / driver_rating
        t_stop = 0  # было 15 / driver_rating, заменили на 0
        t_lift = 10
        t_down = 10
        t_leave = t_drive
        K_ugl = 1 + 0.01 * max(props.angle - 25, 0)
        K_temp = 1.25
        K_mat = koef_soprotivleniya[props.material_type]
        speed = unloading_speed[props.type_unloading]
        t_dump = truck_volume / (speed * K_ugl * K_mat * K_temp)
        total_time = t_drive + t_stop + t_lift + t_dump + t_down + t_leave
        return {
            't_drive': t_drive, 't_stop': t_stop, 't_lift': t_lift,
            't_dump': t_dump, 't_down': t_down, 't_leave': t_leave,
            't_total': total_time,
            'params': dict(K_ugl=K_ugl, K_temp=K_temp, K_mat=K_mat, speed=speed)
        }

    @classmethod
    def unload_calculation_by_norm(cls, unload_props: UnlProperties, truck_props: TruckProperties):
        """
        1. t_drive — подъезд (сек), фиксированно 30 сек
        2. t_stop — остановка и установка (15 сек)
        3. t_lift — подъем кузова (20 сек)
        4. t_dump — высыпание груза:
            t_dump = V / (speed * K_угол * K_мат * K_темп)
        5. t_down — опускание кузова (15 сек)
        6. t_leave — уход (30 сек)
        потом исправлю CHANGE
        длина участка для маневра
        средняя скорость маневра
        замедление
        """
        density = density_by_material[unload_props.material_type]
        truck_volume = truck_props.body_capacity / density

        driver_rating = 1
        t_drive = 30 / driver_rating
        t_stop = 15 / driver_rating
        t_lift = 20
        t_down = 15
        t_leave = t_drive
        K_ugl = 1 + 0.01 * max(unload_props.angle - 25, 0)
        K_temp = 1
        K_mat = koef_soprotivleniya[unload_props.material_type]
        speed = unloading_speed[unload_props.type_unloading]
        t_dump = truck_volume / (speed * K_ugl * K_mat * K_temp)
        total_time = t_drive + t_stop + t_lift + t_dump + t_down + t_leave
        return {
            't_drive': t_drive, 't_stop': t_stop, 't_lift': t_lift,
            't_dump': t_dump, 't_down': t_down, 't_leave': t_leave,
            't_total': total_time,
            'params': dict(K_ugl=K_ugl, K_temp=K_temp, K_mat=K_mat, speed=speed)
        }