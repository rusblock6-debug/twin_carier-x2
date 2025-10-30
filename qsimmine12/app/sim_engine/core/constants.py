from app.enums import PayloadType, UnloadType


koef_soprotivleniya = {
    PayloadType.GRAVEL:  1.0,  # Щебень
    PayloadType.SAND:    1.1,  # Песок
    PayloadType.CLAY:    1.4,  # Глина
    PayloadType.WET_ORE: 1.5   # Влажная руда
}


# Плотность породы
density_by_material = {
    PayloadType.SAND: 1.6,      # песок
    PayloadType.CLAY: 1.9,      # глина
    PayloadType.GRAVEL: 1.5,    # щебень
    PayloadType.WET_ORE: 2.7    # влажная руда
}

# Коэффициент скорости выгрузки
unloading_speed = {
    UnloadType.HYDRAULIC: 2.8,
    UnloadType.MECHANICAL: 0.35,
    UnloadType.GRAVITY: 0.25
}