import random
from datetime import datetime, timedelta

from app.sim_engine.enums import ObjectType


def generate_simulation_data():
    telemetry = []
    total_frames = 720
    start_time = datetime.now() - timedelta(hours=1)

    # Координаты объектов
    unloading_site1 = (55.754, 37.624)  # Для C1
    unloading_site2 = (55.752, 37.622)  # Для C2
    shovel_pos = (55.7515, 37.619)

    for frame_id in range(1, total_frames + 1):
        frame_time = start_time + timedelta(minutes=frame_id)

        # Экскаватор (неподвижный)
        telemetry.append((
            frame_id,
            102,  # 1: unit_id
            "Экскаватор E31",  # 2: unit_name
            ObjectType.SHOVEL.key(),  # 3: unit_type
            shovel_pos[0],  # 4: latitude
            shovel_pos[1],  # 5: longitude
            0.0,  # 6: speed
            0.0,  # 7: weight
            "working"  # 8: state
        ))

        # Точка разгрузки 1
        telemetry.append((
            frame_id,
            201,
            "Точка разгрузки C1",
            ObjectType.UNLOAD.key(),
            unloading_site1[0],
            unloading_site1[1],
            0.0,
            0.0,
            "waiting"
        ))

        # Точка разгрузки 2
        telemetry.append((
            frame_id,
            202,
            "Точка разгрузки C2",
            ObjectType.UNLOAD.key(),
            unloading_site2[0],
            unloading_site2[1],
            0.0,
            0.0,
            "waiting"
        ))

        # Самосвал C1
        progress = min(1, frame_id / (total_frames * 0.8))
        lat = shovel_pos[0] + (unloading_site1[0] - shovel_pos[0]) * progress
        lng = shovel_pos[1] + (unloading_site1[1] - shovel_pos[1]) * progress

        telemetry.append((
            frame_id,
            101,
            "Самосвал C1",
            ObjectType.TRUCK.key(),
            lat,
            lng,
            40 + (frame_id % 10),
            25 if frame_id < total_frames * 0.8 else 0,
            "moving" if frame_id < total_frames * 0.8 else "unloading"
        ))

        # Самосвал C2
        progress = min(1, frame_id / (total_frames * 0.7))
        lat = shovel_pos[0] + (unloading_site2[0] - shovel_pos[0]) * progress
        lng = shovel_pos[1] + (unloading_site2[1] - shovel_pos[1]) * progress

        telemetry.append((
            frame_id,
            103,
            "Самосвал C2",
            ObjectType.TRUCK.key(),
            lat,
            lng,
            35 + (frame_id % 15),
            25 if frame_id < total_frames * 0.7 else 0,
            "moving" if frame_id < total_frames * 0.7 else "unloading"
        ))

    # Сводные данные (можно оставить в dict)
    by_hours = {str(h): random.randint(100, 500) for h in range(1, 13)}

    summary = {
        "trips": random.randint(5, 20),
        "volume": random.randint(5000, 15000),
        "weight": random.randint(100000, 500000),
        "by_hours": by_hours
    }

    return {
        "status": "ok",
        "telemetry": telemetry,  # Теперь это список tuples
        "summary": summary  # Сводка остается dict
    }