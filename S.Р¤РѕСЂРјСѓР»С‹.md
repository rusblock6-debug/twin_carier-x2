# Сводка математических формул проекта

| № | Формула | Пояснение (из чего состоит) | Местоположение | Что делает | Зависимости |
|---|---------|----------------------------|----------------|------------|-------------|

| 1 | `STATIC_DIR = BASE_DIR / "static"` | Операции: деление. Операнды: BASE_DIR. | qsimmine12/app/__init__.py:18 | Присваивает STATIC_DIR результат выражения. | BASE_DIR |
| 2 | `UPLOAD_DIR = BASE_DIR.parent / "upload"` | Операции: деление. Операнды: BASE_DIR. | qsimmine12/app/__init__.py:19 | Присваивает UPLOAD_DIR результат выражения. | BASE_DIR |
| 3 | `return [record.id for record in records]` | Операции: функции и литералы. Операнды: record, records. | qsimmine12/app/abstract/dao.py:26 | Возвращает результат вычисления. | record, records |
| 4 | `opacity = 0 if (hex_color is None) else 1` | Операции: функции и литералы. Операнды: hex_color. | qsimmine12/app/dxf/dxf_converter.py:180 | Присваивает opacity результат выражения. | hex_color |
| 5 | `stroke_width = float(lineweight / 100)` | Операции: деление. Операнды: float, lineweight. | qsimmine12/app/dxf/dxf_converter.py:181 | Присваивает stroke_width результат выражения. | float, lineweight |
| 6 | `layer = doc.layers.get(entity.dxf.layer) if doc else None` | Операции: функции и литералы. Операнды: doc, entity. | qsimmine12/app/dxf/dxf_converter.py:217 | Присваивает layer результат выражения. | doc, entity |
| 7 | `test_files_dir = pathlib.Path(__file__).parent / 'files'` | Операции: деление. Операнды: __file__, pathlib. | qsimmine12/app/dxf/tests/test_dxf_converter.py:10 | Присваивает test_files_dir результат выражения. | __file__, pathlib |
| 8 | `file_path = self.test_files_dir / filename` | Операции: деление. Операнды: filename, self. | qsimmine12/app/dxf/tests/test_dxf_converter.py:26 | Присваивает file_path результат выражения. | filename, self |
| 9 | `coordinates = [
            [coord.lng, coord.lat] for coord in self.coordinates
        ]` | Операции: функции и литералы. Операнды: coord, self. | qsimmine12/app/forms.py:261 | Присваивает coordinates результат выражения. | coord, self |
| 10 | `shift_config = self.shift_config if self.shift_config is not None else getattr(orm_obj, 'shift_config', None)` | Операции: функции и литералы. Операнды: getattr, orm_obj, self. | qsimmine12/app/forms.py:511 | Присваивает shift_config результат выражения. | getattr, orm_obj, self |
| 11 | `lunch_break_offset_end = lunch_break_offset + lunch_break_duration` | Операции: сложение. Операнды: lunch_break_duration, lunch_break_offset. | qsimmine12/app/forms.py:526 | Присваивает lunch_break_offset_end результат выражения. | lunch_break_duration, lunch_break_offset |
| 12 | `shift_change_offset_end = shift_change_offset + shift_change_duration` | Операции: сложение. Операнды: shift_change_duration, shift_change_offset. | qsimmine12/app/forms.py:535 | Присваивает shift_change_offset_end результат выражения. | shift_change_duration, shift_change_offset |
| 13 | `inner_stmt = exists(1).where(
            self.model.vehicle_type == self.vehicle_type,
            self.model.vehicle_id == self.vehicle_id,
            or_(
                and_(
                    self.model.start_time <= self.start_time,
                    self.start_time < self.model.end_time
                ),
                and_(
                    self.start_time <= self.model.start_time,
                    self.model.start_time < self.end_time
                )
            )
        )` | Операции: функции и литералы. Операнды: and_, exists, or_, self. | qsimmine12/app/forms.py:694 | Присваивает inner_stmt результат выражения. | and_, exists, or_, self |
| 14 | `return [k for k in dir(schema_cls) if not k.startswith('_')]` | Операции: логическое не. Операнды: dir, k, schema_cls. | qsimmine12/app/forms.py:79 | Возвращает результат вычисления. | dir, k, schema_cls |
| 15 | `distance = math.hypot(distance, coord1[2] - coord0[2])` | Операции: вычитание. Операнды: coord0, coord1, distance, math. | qsimmine12/app/geo_utils.py:22 | Присваивает distance результат выражения. | coord0, coord1, distance, math |
| 16 | `rad = 0 * math.pi / 180` | Операции: деление, умножение. Операнды: math. | qsimmine12/app/geo_utils.py:34 | Присваивает rad результат выражения. | math |
| 17 | `cos_r = math.cos(rad)` | Операции: функции и литералы. Операнды: math, rad. | qsimmine12/app/geo_utils.py:35 | Присваивает cos_r результат выражения. | math, rad |
| 18 | `sin_r = math.sin(rad)` | Операции: функции и литералы. Операнды: math, rad. | qsimmine12/app/geo_utils.py:36 | Присваивает sin_r результат выражения. | math, rad |
| 19 | `rx = x * cos_r - y * sin_r` | Операции: вычитание, умножение. Операнды: cos_r, sin_r, x, y. | qsimmine12/app/geo_utils.py:37 | Присваивает rx результат выражения. | cos_r, sin_r, x, y |
| 20 | `ry = x * sin_r + y * cos_r` | Операции: сложение, умножение. Операнды: cos_r, sin_r, x, y. | qsimmine12/app/geo_utils.py:38 | Присваивает ry результат выражения. | cos_r, sin_r, x, y |
| 21 | `delta_lat = ry / metersPerDegree` | Операции: деление. Операнды: metersPerDegree, ry. | qsimmine12/app/geo_utils.py:41 | Присваивает delta_lat результат выражения. | metersPerDegree, ry |
| 22 | `delta_lon = rx / (metersPerDegree * math.cos(lat0 * math.pi / 180))` | Операции: деление, умножение. Операнды: lat0, math, metersPerDegree, rx. | qsimmine12/app/geo_utils.py:42 | Присваивает delta_lon результат выражения. | lat0, math, metersPerDegree, rx |
| 23 | `alt = alt0 + z` | Операции: сложение. Операнды: alt0, z. | qsimmine12/app/geo_utils.py:45 | Присваивает alt результат выражения. | alt0, z |
| 24 | `valid_vehicle_types = tuple(m.__tablename__ for m in valid_vehicle_models)` | Операции: функции и литералы. Операнды: m, tuple, valid_vehicle_models. | qsimmine12/app/models.py:725 | Присваивает valid_vehicle_types результат выражения. | m, tuple, valid_vehicle_models |
| 25 | `all_object_types = list(TYPE_SCHEDULE_MAP.keys()) + list(TYPE_MODEL_MAP.keys())` | Операции: сложение. Операнды: TYPE_MODEL_MAP, TYPE_SCHEDULE_MAP, list. | qsimmine12/app/models.py:788 | Присваивает all_object_types результат выражения. | TYPE_MODEL_MAP, TYPE_SCHEDULE_MAP, list |
| 26 | `non_existent_ids = ids - db_ids` | Операции: вычитание. Операнды: db_ids, ids. | qsimmine12/app/road_net.py:79 | Присваивает non_existent_ids результат выражения. | db_ids, ids |
| 27 | `batch_keys = [
        f'{base_sim_key}:batch:{idx}'
        for idx in indices
    ]` | Операции: функции и литералы. Операнды: base_sim_key, idx, indices. | qsimmine12/app/routes.py:324 | Присваивает batch_keys результат выражения. | base_sim_key, idx, indices |
| 28 | `batches.extend([json.loads(val) for val in batch_vals if val])` | Операции: функции и литералы. Операнды: batch_vals, batches, json, val. | qsimmine12/app/routes.py:331 | Вычисляет выражение без сохранения результата. | batch_vals, batches, json, val |
| 29 | `save_path = upload_folder / save_name` | Операции: деление. Операнды: save_name, upload_folder. | qsimmine12/app/routes.py:397 | Присваивает save_path результат выражения. | save_name, upload_folder |
| 30 | `str_i = '0' * (3 - len(str_i)) + str_i` | Операции: вычитание, сложение, умножение. Операнды: len, str_i. | qsimmine12/app/routes.py:403 | Присваивает str_i результат выражения. | len, str_i |
| 31 | `return FileResponse(upload_dir / filename)` | Операции: деление. Операнды: FileResponse, filename, upload_dir. | qsimmine12/app/routes.py:450 | Возвращает результат вычисления. | FileResponse, filename, upload_dir |
| 32 | `schedule_type = "blasting" if isinstance(form, BlastingSchema) else "planned_idle"` | Операции: функции и литералы. Операнды: BlastingSchema, form, isinstance. | qsimmine12/app/services/object_service.py:168 | Присваивает schedule_type результат выражения. | BlastingSchema, form, isinstance |
| 33 | `quarry_cols = [col.name for col in Quarry.__table__.columns]` | Операции: функции и литералы. Операнды: Quarry, col. | qsimmine12/app/services/quarry_data_service.py:123 | Присваивает quarry_cols результат выражения. | Quarry, col |
| 34 | `qdict = {col_name: getattr(quarry, col_name) for col_name in quarry_cols}` | Операции: функции и литералы. Операнды: col_name, getattr, quarry, quarry_cols. | qsimmine12/app/services/quarry_data_service.py:128 | Присваивает qdict результат выражения. | col_name, getattr, quarry, quarry_cols |
| 35 | `model_cols = [col.name for col in model.__table__.columns]` | Операции: функции и литералы. Операнды: col, model. | qsimmine12/app/services/quarry_data_service.py:142 | Присваивает model_cols результат выражения. | col, model |
| 36 | `item = {col: getattr(inst, col) for col in model_cols}` | Операции: функции и литералы. Операнды: col, getattr, inst, model_cols. | qsimmine12/app/services/quarry_data_service.py:148 | Присваивает item результат выражения. | col, getattr, inst, model_cols |
| 37 | `mo_cols = [col.name for col in MapOverlay.__table__.columns]` | Операции: функции и литералы. Операнды: MapOverlay, col. | qsimmine12/app/services/quarry_data_service.py:167 | Присваивает mo_cols результат выражения. | MapOverlay, col |
| 38 | `item = {col: getattr(mo, col) for col in mo_cols if col != 'geojson_data'}` | Операции: функции и литералы. Операнды: col, getattr, mo, mo_cols. | qsimmine12/app/services/quarry_data_service.py:174 | Присваивает item результат выражения. | col, getattr, mo, mo_cols |
| 39 | `trucks = [assoc.truck_id for assoc in getattr(trail, "truck_associations", [])]` | Операции: функции и литералы. Операнды: assoc, getattr, trail. | qsimmine12/app/services/quarry_data_service.py:198 | Присваивает trucks результат выражения. | assoc, getattr, trail |
| 40 | `column_names = [col.name for col in model.__table__.columns]` | Операции: функции и литералы. Операнды: col, model. | qsimmine12/app/services/quarry_data_service.py:90 | Присваивает column_names результат выражения. | col, model |
| 41 | `return {col_name: getattr(instance, col_name) for col_name in column_names}` | Операции: функции и литералы. Операнды: col_name, column_names, getattr, instance. | qsimmine12/app/services/quarry_data_service.py:91 | Возвращает результат вычисления. | col_name, column_names, getattr, instance |
| 42 | `trails_dto = [
            self._trail_to_dto(trail, assoc_by_trail) for trail in trail_objs
        ]` | Операции: функции и литералы. Операнды: List, TrailDTO, assoc_by_trail, self, trail, trail_objs. | qsimmine12/app/services/scenario_service.py:110 | Присваивает trails_dto результат выражения с аннотацией. | List, TrailDTO, assoc_by_trail, self, trail, trail_objs |
| 43 | `return parsed if isinstance(parsed, list) else []` | Операции: функции и литералы. Операнды: isinstance, list, parsed. | qsimmine12/app/services/scenario_service.py:135 | Возвращает результат вычисления. | isinstance, list, parsed |
| 44 | `return [self._scenario_to_dto(scenario) for scenario in scenarios]` | Операции: функции и литералы. Операнды: scenario, scenarios, self. | qsimmine12/app/services/scenario_service.py:73 | Возвращает результат вычисления. | scenario, scenarios, self |
| 45 | `obj_dict = {col: getattr(obj, col) for col in model_cols}` | Операции: функции и литералы. Операнды: col, getattr, model_cols, obj. | qsimmine12/app/services/schedule_data_service.py:81 | Присваивает obj_dict результат выражения. | col, getattr, model_cols, obj |
| 46 | `mode = "auto" if scenario.get("is_auto_truck_distribution") else "manual"` | Операции: функции и литералы. Операнды: scenario. | qsimmine12/app/services/simulation_id_service.py:136 | Присваивает mode результат выражения. | scenario |
| 47 | `stored_meta_keys = [
            (key, self.redis.ttl(key))
            for key in self.redis.scan_iter(f"{sim_key_base}:*:meta", 1000)
        ]` | Операции: функции и литералы. Операнды: key, self, sim_key_base. | qsimmine12/app/services/simulation_id_service.py:177 | Присваивает stored_meta_keys результат выражения. | key, self, sim_key_base |
| 48 | `key_patterns_to_delete = [
            meta_key[0].replace(":meta", ":*")
            for meta_key in stored_meta_keys[STORED_RESULTS_NUMBER:]
        ]` | Операции: функции и литералы. Операнды: STORED_RESULTS_NUMBER, meta_key, stored_meta_keys. | qsimmine12/app/services/simulation_id_service.py:186 | Присваивает key_patterns_to_delete результат выражения. | STORED_RESULTS_NUMBER, meta_key, stored_meta_keys |
| 49 | `stored_keys_to_delete = [
                key for key in self.redis.scan_iter(key_pattern, 1000)
            ]` | Операции: функции и литералы. Операнды: key, key_pattern, self. | qsimmine12/app/services/simulation_id_service.py:191 | Присваивает stored_keys_to_delete результат выражения. | key, key_pattern, self |
| 50 | `obj_dict = {
                col_name: getattr(obj, col_name)
                for col_name in model_cols
            }` | Операции: функции и литералы. Операнды: col_name, getattr, model_cols, obj. | qsimmine12/app/services/simulation_id_service.py:75 | Присваивает obj_dict результат выражения. | col_name, getattr, model_cols, obj |
| 51 | `column_names = [col.name for col in model.__table__.columns]` | Операции: функции и литералы. Операнды: col, model. | qsimmine12/app/services/template_service.py:56 | Присваивает column_names результат выражения. | col, model |
| 52 | `return [
            {col_name: getattr(inst, col_name) for col_name in column_names}
            for inst in instances
        ]` | Операции: функции и литералы. Операнды: col_name, column_names, getattr, inst, instances. | qsimmine12/app/services/template_service.py:57 | Возвращает результат вычисления. | col_name, column_names, getattr, inst, instances |
| 53 | `offsets_tuple = tuple(
            ShiftOffsetsDTO(
                timedelta(minutes=shift_offsets['begin_offset']),
                timedelta(minutes=shift_offsets['end_offset'])
            )
            for shift_offsets in _shift_config
        )` | Операции: функции и литералы. Операнды: ShiftOffsetsDTO, _shift_config, shift_offsets, timedelta, tuple. | qsimmine12/app/shift.py:104 | Присваивает offsets_tuple результат выражения. | ShiftOffsetsDTO, _shift_config, shift_offsets, timedelta, tuple |
| 54 | `begin_time = day_start + offsets.begin_offset` | Операции: сложение. Операнды: day_start, offsets. | qsimmine12/app/shift.py:152 | Присваивает begin_time результат выражения. | day_start, offsets |
| 55 | `end_time = day_start + offsets.end_offset` | Операции: сложение. Операнды: day_start, offsets. | qsimmine12/app/shift.py:153 | Присваивает end_time результат выражения. | day_start, offsets |
| 56 | `prev_day = shift.day - timedelta(days=1)` | Операции: вычитание. Операнды: shift, timedelta. | qsimmine12/app/shift.py:199 | Присваивает prev_day результат выражения. | shift, timedelta |
| 57 | `prev_number = shift.number - 1` | Операции: вычитание. Операнды: shift. | qsimmine12/app/shift.py:201 | Присваивает prev_number результат выражения. | shift |
| 58 | `next_day = shift.day + timedelta(days=1)` | Операции: сложение. Операнды: shift, timedelta. | qsimmine12/app/shift.py:218 | Присваивает next_day результат выражения. | shift, timedelta |
| 59 | `next_number = shift.number + 1` | Операции: сложение. Операнды: shift. | qsimmine12/app/shift.py:220 | Присваивает next_number результат выражения. | shift |
| 60 | `MTBF = T_A / N_F` | Операции: деление. Операнды: N_F, T_A. | qsimmine12/app/sim_engine/core/calculations/base.py:18 | Присваивает MTBF результат выражения. | N_F, T_A |
| 61 | `failure_rate = 1 / MTBF` | Операции: деление. Операнды: MTBF. | qsimmine12/app/sim_engine/core/calculations/base.py:19 | Присваивает failure_rate результат выражения. | MTBF |
| 62 | `repair_rate = 1 / MTTR` | Операции: деление. Операнды: MTTR. | qsimmine12/app/sim_engine/core/calculations/base.py:20 | Присваивает repair_rate результат выражения. | MTTR |
| 63 | `fuel_rate = ((sfc / (1000 * density)) * p_engine) / 3600` | Операции: деление, умножение. Операнды: density, p_engine, sfc. | qsimmine12/app/sim_engine/core/calculations/base.py:46 | Присваивает fuel_rate результат выражения. | density, p_engine, sfc |
| 64 | `fuel_rate = fuel_idle_lph / 3600` | Операции: деление. Операнды: fuel_idle_lph. | qsimmine12/app/sim_engine/core/calculations/base.py:52 | Присваивает fuel_rate результат выражения. | fuel_idle_lph |
| 65 | `t1 = (glubina_vrezki_m * k['K_r'] * k['K_w']) / props.skorost_vrezki_m_s * k['K_T']` | Операции: деление, умножение. Операнды: glubina_vrezki_m, k, props. | qsimmine12/app/sim_engine/core/calculations/shovel.py:26 | Присваивает t1 результат выражения. | glubina_vrezki_m, k, props |
| 66 | `t2 = (dlina_drag_m * k['K_r'] * k['K_w']) / (props.skorost_napolneniya_m_s * k['K_f']) * k['K_T']` | Операции: деление, умножение. Операнды: dlina_drag_m, k, props. | qsimmine12/app/sim_engine/core/calculations/shovel.py:28 | Присваивает t2 результат выражения. | dlina_drag_m, k, props |
| 67 | `t3 = visota_podem_m / props.skorost_podem_m_s * k['K_i'] * k['K_h'] * k['K_T']` | Операции: деление, умножение. Операнды: k, props, visota_podem_m. | qsimmine12/app/sim_engine/core/calculations/shovel.py:30 | Присваивает t3 результат выражения. | k, props, visota_podem_m |
| 68 | `t4 = ugol_swing_rad / props.skorost_povorot_rad_s * k['K_i'] * k['K_h'] * k['K_T']` | Операции: деление, умножение. Операнды: k, props, ugol_swing_rad. | qsimmine12/app/sim_engine/core/calculations/shovel.py:32 | Присваивает t4 результат выражения. | k, props, ugol_swing_rad |
| 69 | `t5 = ugol_dump_rad / props.skorost_povorot_rad_s * k['K_h'] * k['K_T']` | Операции: деление, умножение. Операнды: k, props, ugol_dump_rad. | qsimmine12/app/sim_engine/core/calculations/shovel.py:34 | Присваивает t5 результат выражения. | k, props, ugol_dump_rad |
| 70 | `t6 = ugol_swing_rad / props.skorost_povorot_rad_s * k['K_ret'] * k['K_h'] * k['K_T']` | Операции: деление, умножение. Операнды: k, props, ugol_swing_rad. | qsimmine12/app/sim_engine/core/calculations/shovel.py:36 | Присваивает t6 результат выражения. | k, props, ugol_swing_rad |
| 71 | `idles = [idle(t) for t in [t1, t2, t3, t4, t5, t6]]` | Операции: функции и литералы. Операнды: idle, t, t1, t2, t3, t4, t5, t6. | qsimmine12/app/sim_engine/core/calculations/shovel.py:45 | Присваивает idles результат выражения. | idle, t, t1, t2, t3, t4, t5, t6 |
| 72 | `total_s = sum([t1, t2, t3, t4, t5, t6]) + sum(idles)` | Операции: сложение. Операнды: idles, sum, t1, t2, t3, t4, t5, t6. | qsimmine12/app/sim_engine/core/calculations/shovel.py:46 | Присваивает total_s результат выражения. | idles, sum, t1, t2, t3, t4, t5, t6 |
| 73 | `cycle_volume = shovel_props.obem_kovsha_m3 * shovel_props.koef_zapolneniya` | Операции: умножение. Операнды: shovel_props. | qsimmine12/app/sim_engine/core/calculations/shovel.py:96 | Присваивает cycle_volume результат выражения. | shovel_props |
| 74 | `cycle_weight = cycle_volume * density` | Операции: умножение. Операнды: cycle_volume, density. | qsimmine12/app/sim_engine/core/calculations/shovel.py:97 | Присваивает cycle_weight результат выражения. | cycle_volume, density |
| 75 | `return sum([1 for _ in cls.calculate_motion_by_edges(route, props, forward, is_loaded)])` | Операции: функции и литералы. Операнды: cls, forward, is_loaded, props, route, sum. | qsimmine12/app/sim_engine/core/calculations/truck.py:108 | Возвращает результат вычисления. | cls, forward, is_loaded, props, route, sum |
| 76 | `t = self.distance_km / self.speed_empty_kmh * 3600` | Операции: деление, умножение. Операнды: self. | qsimmine12/app/sim_engine/core/calculations/truck.py:117 | Присваивает t результат выражения. | self |
| 77 | `return int(np.ceil(t / self.driver_skill))` | Операции: деление. Операнды: int, np, self, t. | qsimmine12/app/sim_engine/core/calculations/truck.py:118 | Возвращает результат вычисления. | int, np, self, t |
| 78 | `t = self.distance_km / self.speed_loaded_kmh * 3600` | Операции: деление, умножение. Операнды: self. | qsimmine12/app/sim_engine/core/calculations/truck.py:126 | Присваивает t результат выражения. | self |
| 79 | `return int(np.ceil(t / self.driver_skill))` | Операции: деление. Операнды: int, np, self, t. | qsimmine12/app/sim_engine/core/calculations/truck.py:127 | Возвращает результат вычисления. | int, np, self, t |
| 80 | `speed = min(speed + acceleration, speed_limit)` | Операции: сложение. Операнды: acceleration, min, speed, speed_limit. | qsimmine12/app/sim_engine/core/calculations/truck.py:28 | Присваивает speed результат выражения. | acceleration, min, speed, speed_limit |
| 81 | `delta_km = speed * time_step_sec / 3600.0` | Операции: деление, умножение. Операнды: speed, time_step_sec. | qsimmine12/app/sim_engine/core/calculations/truck.py:29 | Присваивает delta_km результат выражения. | speed, time_step_sec |
| 82 | `travelled_km = min(travelled_km + delta_km, distance_km)` | Операции: сложение. Операнды: delta_km, distance_km, min, travelled_km. | qsimmine12/app/sim_engine/core/calculations/truck.py:30 | Присваивает travelled_km результат выражения. | delta_km, distance_km, min, travelled_km |
| 83 | `ratio = travelled_km / distance_km` | Операции: деление. Операнды: distance_km, travelled_km. | qsimmine12/app/sim_engine/core/calculations/truck.py:31 | Присваивает ratio результат выражения. | distance_km, travelled_km |
| 84 | `points = route.points if forward else list(reversed(route.points))` | Операции: функции и литералы. Операнды: forward, list, reversed, route. | qsimmine12/app/sim_engine/core/calculations/truck.py:41 | Присваивает points результат выражения. | forward, list, reversed, route |
| 85 | `speed_limit = props.speed_empty_kmh if not forward else props.speed_loaded_kmh` | Операции: логическое не. Операнды: forward, props. | qsimmine12/app/sim_engine/core/calculations/truck.py:42 | Присваивает speed_limit результат выражения. | forward, props |
| 86 | `acceleration = props.acceleration_empty if not forward else props.acceleration_loaded` | Операции: логическое не. Операнды: forward, props. | qsimmine12/app/sim_engine/core/calculations/truck.py:43 | Присваивает acceleration результат выражения. | forward, props |
| 87 | `distance_km = edge.length / 1000` | Операции: деление. Операнды: edge. | qsimmine12/app/sim_engine/core/calculations/truck.py:65 | Присваивает distance_km результат выражения. | edge |
| 88 | `speed = min(speed + acceleration, speed_limit)` | Операции: сложение. Операнды: acceleration, min, speed, speed_limit. | qsimmine12/app/sim_engine/core/calculations/truck.py:72 | Присваивает speed результат выражения. | acceleration, min, speed, speed_limit |
| 89 | `delta_km = speed * time_step_sec / 3600.0` | Операции: деление, умножение. Операнды: speed, time_step_sec. | qsimmine12/app/sim_engine/core/calculations/truck.py:73 | Присваивает delta_km результат выражения. | speed, time_step_sec |
| 90 | `travelled_km = min(travelled_km + delta_km, distance_km)` | Операции: сложение. Операнды: delta_km, distance_km, min, travelled_km. | qsimmine12/app/sim_engine/core/calculations/truck.py:74 | Присваивает travelled_km результат выражения. | delta_km, distance_km, min, travelled_km |
| 91 | `ratio = travelled_km / distance_km` | Операции: деление. Операнды: distance_km, travelled_km. | qsimmine12/app/sim_engine/core/calculations/truck.py:75 | Присваивает ratio результат выражения. | distance_km, travelled_km |
| 92 | `speed_limit = props.speed_empty_kmh if not is_loaded else props.speed_loaded_kmh` | Операции: логическое не. Операнды: is_loaded, props. | qsimmine12/app/sim_engine/core/calculations/truck.py:85 | Присваивает speed_limit результат выражения. | is_loaded, props |
| 93 | `acceleration = props.acceleration_empty if not is_loaded else props.acceleration_loaded` | Операции: логическое не. Операнды: is_loaded, props. | qsimmine12/app/sim_engine/core/calculations/truck.py:86 | Присваивает acceleration результат выражения. | is_loaded, props |
| 94 | `cs2_load = variance_load_duration / (mean_load_duration ** 2)` | Операции: деление, степень. Операнды: mean_load_duration, variance_load_duration. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:160 | Присваивает cs2_load результат выражения. | mean_load_duration, variance_load_duration |
| 95 | `cs2_unload = variance_unload_duration / (mean_unload_duration ** 2)` | Операции: деление, степень. Операнды: mean_unload_duration, variance_unload_duration. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:161 | Присваивает cs2_unload результат выражения. | mean_unload_duration, variance_unload_duration |
| 96 | `ca2_load = variance_shovels_waiting_trucks_duration / (mean_shovels_waiting_trucks_duration ** 2)` | Операции: деление, степень. Операнды: mean_shovels_waiting_trucks_duration, variance_shovels_waiting_trucks_duration. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:162 | Присваивает ca2_load результат выражения. | mean_shovels_waiting_trucks_duration, variance_shovels_waiting_trucks_duration |
| 97 | `ca2_unload = variance_unloads_waiting_trucks_duration / (mean_unloads_waiting_trucks_duration ** 2)` | Операции: деление, степень. Операнды: mean_unloads_waiting_trucks_duration, variance_unloads_waiting_trucks_duration. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:163 | Присваивает ca2_unload результат выражения. | mean_unloads_waiting_trucks_duration, variance_unloads_waiting_trucks_duration |
| 98 | `a = lam / mu` | Операции: деление. Операнды: lam, mu. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:19 | Присваивает a результат выражения. | lam, mu |
| 99 | `rho = lam / (c * mu)` | Операции: деление, умножение. Операнды: c, lam, mu. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:20 | Присваивает rho результат выражения. | c, lam, mu |
| 100 | `term *= a / k` | Операции: деление. Операнды: a, k. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:28 | Обновляет term через умножение. | a, k |
| 101 | `termc = (a ** c) / math.factorial(c) * (c / (c - a))` | Операции: вычитание, деление, степень, умножение. Операнды: a, c, math. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:30 | Присваивает termc результат выражения. | a, c, math |
| 102 | `Pw = termc / (sum0 + termc)` | Операции: деление, сложение. Операнды: sum0, termc. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:31 | Присваивает Pw результат выражения. | sum0, termc |
| 103 | `rho = lam / (c * mu)` | Операции: деление, умножение. Операнды: c, lam, mu. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:42 | Присваивает rho результат выражения. | c, lam, mu |
| 104 | `Wq_mm = Pw / (c * mu - lam)` | Операции: вычитание, деление, умножение. Операнды: Pw, c, lam, mu. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:46 | Присваивает Wq_mm результат выражения. | Pw, c, lam, mu |
| 105 | `return 0.5 * (ca2 + cs2) * Wq_mm` | Операции: сложение, умножение. Операнды: Wq_mm, ca2, cs2. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:47 | Возвращает результат вычисления. | Wq_mm, ca2, cs2 |
| 106 | `mu_load = 1.0 / T_load` | Операции: деление. Операнды: T_load. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:82 | Присваивает mu_load результат выражения. | T_load |
| 107 | `mu_unld = 1.0 / T_unload` | Операции: деление. Операнды: T_unload. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:83 | Присваивает mu_unld результат выражения. | T_unload |
| 108 | `u_star2 = 1 - (Dur_rep + Dur_idle + Dur_blast + Dur_lunch) / (Dur_work * M)` | Операции: вычитание, деление, сложение, умножение. Операнды: Dur_blast, Dur_idle, Dur_lunch, Dur_rep, Dur_work, M. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:84 | Присваивает u_star2 результат выражения. | Dur_blast, Dur_idle, Dur_lunch, Dur_rep, Dur_work, M |
| 109 | `lam = u_star * u_star2 * M * mu_load` | Операции: умножение. Операнды: M, mu_load, u_star, u_star2. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:85 | Присваивает lam результат выражения. | M, mu_load, u_star, u_star2 |
| 110 | `T_cycle = T_haul + T_return + T_load + T_unload + Wq_load + Wq_unld + cls.T_rot` | Операции: сложение. Операнды: T_haul, T_load, T_return, T_unload, Wq_load, Wq_unld, cls. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:90 | Присваивает T_cycle результат выражения. | T_haul, T_load, T_return, T_unload, Wq_load, Wq_unld, cls |
| 111 | `N = lam * T_cycle` | Операции: умножение. Операнды: T_cycle, lam. | qsimmine12/app/sim_engine/core/calculations/trucks_needed.py:91 | Присваивает N результат выражения. | T_cycle, lam |
| 112 | `t_drive = 30 / driver_rating` | Операции: деление. Операнды: driver_rating. | qsimmine12/app/sim_engine/core/calculations/unload.py:27 | Присваивает t_drive результат выражения. | driver_rating |
| 113 | `K_ugl = 1 + 0.01 * max(props.angle - 25, 0)` | Операции: вычитание, сложение, умножение. Операнды: max, props. | qsimmine12/app/sim_engine/core/calculations/unload.py:32 | Присваивает K_ugl результат выражения. | max, props |
| 114 | `t_dump = truck_volume / (speed * K_ugl * K_mat * K_temp)` | Операции: деление, умножение. Операнды: K_mat, K_temp, K_ugl, speed, truck_volume. | qsimmine12/app/sim_engine/core/calculations/unload.py:36 | Присваивает t_dump результат выражения. | K_mat, K_temp, K_ugl, speed, truck_volume |
| 115 | `total_time = t_drive + t_stop + t_lift + t_dump + t_down + t_leave` | Операции: сложение. Операнды: t_down, t_drive, t_dump, t_leave, t_lift, t_stop. | qsimmine12/app/sim_engine/core/calculations/unload.py:37 | Присваивает total_time результат выражения. | t_down, t_drive, t_dump, t_leave, t_lift, t_stop |
| 116 | `truck_volume = truck_props.body_capacity / density` | Операции: деление. Операнды: density, truck_props. | qsimmine12/app/sim_engine/core/calculations/unload.py:61 | Присваивает truck_volume результат выражения. | density, truck_props |
| 117 | `t_drive = 30 / driver_rating` | Операции: деление. Операнды: driver_rating. | qsimmine12/app/sim_engine/core/calculations/unload.py:64 | Присваивает t_drive результат выражения. | driver_rating |
| 118 | `t_stop = 15 / driver_rating` | Операции: деление. Операнды: driver_rating. | qsimmine12/app/sim_engine/core/calculations/unload.py:65 | Присваивает t_stop результат выражения. | driver_rating |
| 119 | `K_ugl = 1 + 0.01 * max(unload_props.angle - 25, 0)` | Операции: вычитание, сложение, умножение. Операнды: max, unload_props. | qsimmine12/app/sim_engine/core/calculations/unload.py:69 | Присваивает K_ugl результат выражения. | max, unload_props |
| 120 | `t_dump = truck_volume / (speed * K_ugl * K_mat * K_temp)` | Операции: деление, умножение. Операнды: K_mat, K_temp, K_ugl, speed, truck_volume. | qsimmine12/app/sim_engine/core/calculations/unload.py:73 | Присваивает t_dump результат выражения. | K_mat, K_temp, K_ugl, speed, truck_volume |
| 121 | `total_time = t_drive + t_stop + t_lift + t_dump + t_down + t_leave` | Операции: сложение. Операнды: t_down, t_drive, t_dump, t_leave, t_lift, t_stop. | qsimmine12/app/sim_engine/core/calculations/unload.py:74 | Присваивает total_time результат выражения. | t_down, t_drive, t_dump, t_leave, t_lift, t_stop |
| 122 | `p = (percent - 30) / 20` | Операции: вычитание, деление. Операнды: percent. | qsimmine12/app/sim_engine/core/coefficients.py:15 | Присваивает p результат выражения. | percent |
| 123 | `return 1.5 + 0.5 * min(max(p, 0), 1)` | Операции: сложение, умножение. Операнды: max, min, p. | qsimmine12/app/sim_engine/core/coefficients.py:16 | Возвращает результат вычисления. | max, min, p |
| 124 | `result = [RouteEdge(path.edges) for path in paths]` | Операции: функции и литералы. Операнды: RouteEdge, path, paths. | qsimmine12/app/sim_engine/core/geometry.py:299 | Присваивает result результат выражения. | RouteEdge, path, paths |
| 125 | `result = [RouteEdge(path.edges) for path in paths]` | Операции: функции и литералы. Операнды: RouteEdge, path, paths. | qsimmine12/app/sim_engine/core/geometry.py:329 | Присваивает result результат выражения. | RouteEdge, path, paths |
| 126 | `result = [RouteEdge(path.edges) for path in paths]` | Операции: функции и литералы. Операнды: RouteEdge, path, paths. | qsimmine12/app/sim_engine/core/geometry.py:356 | Присваивает result результат выражения. | RouteEdge, path, paths |
| 127 | `lat = p1.lat + (p2.lat - p1.lat) * ratio` | Операции: вычитание, сложение, умножение. Операнды: p1, p2, ratio. | qsimmine12/app/sim_engine/core/geometry.py:364 | Присваивает lat результат выражения. | p1, p2, ratio |
| 128 | `lon = p1.lon + (p2.lon - p1.lon) * ratio` | Операции: вычитание, сложение, умножение. Операнды: p1, p2, ratio. | qsimmine12/app/sim_engine/core/geometry.py:365 | Присваивает lon результат выражения. | p1, p2, ratio |
| 129 | `a = math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon / 2)**2` | Операции: деление, сложение, степень, умножение. Операнды: dlat, dlon, lat1, lat2, math. | qsimmine12/app/sim_engine/core/geometry.py:374 | Присваивает a результат выражения. | dlat, dlon, lat1, lat2, math |
| 130 | `c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))` | Операции: вычитание, умножение. Операнды: a, math. | qsimmine12/app/sim_engine/core/geometry.py:375 | Присваивает c результат выражения. | a, math |
| 131 | `return R * c` | Операции: умножение. Операнды: R, c. | qsimmine12/app/sim_engine/core/geometry.py:376 | Возвращает результат вычисления. | R, c |
| 132 | `nearest_point = min(point_list, key=lambda p: haversine_km(point, p))` | Операции: функции и литералы. Операнды: haversine_km, min, p, point, point_list. | qsimmine12/app/sim_engine/core/geometry.py:380 | Присваивает nearest_point результат выражения. | haversine_km, min, p, point, point_list |
| 133 | `return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])` | Операции: вычитание, умножение. Операнды: a, b, o. | qsimmine12/app/sim_engine/core/geometry.py:72 | Возвращает результат вычисления. | a, b, o |
| 134 | `return sorted({i for (i, _) in self.T_load.keys()})` | Операции: функции и литералы. Операнды: i, self, sorted. | qsimmine12/app/sim_engine/core/planner/entities.py:29 | Возвращает результат вычисления. | i, self, sorted |
| 135 | `return sorted({j for (_, j) in self.T_load.keys()})` | Операции: функции и литералы. Операнды: j, self, sorted. | qsimmine12/app/sim_engine/core/planner/entities.py:33 | Возвращает результат вычисления. | j, self, sorted |
| 136 | `return sorted({z for (_, z) in self.T_unload.keys()})` | Операции: функции и литералы. Операнды: self, sorted, z. | qsimmine12/app/sim_engine/core/planner/entities.py:37 | Возвращает результат вычисления. | self, sorted, z |
| 137 | `planning_data.T_start[truck.id, shovel.id] = int(TruckCalc.calculate_time_motion_by_edges(
                    start_route,
                    truck.properties,
                    forward=True
                ) / 60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, shovel, start_route, truck. | qsimmine12/app/sim_engine/core/planner/manage.py:112 | Присваивает planning_data.T_start[truck.id, shovel.id] результат выражения. | TruckCalc, int, planning_data, shovel, start_route, truck |
| 138 | `planning_data.T_haul[truck.id, shovel.id, unload.id] = int(TruckCalc.calculate_time_motion_by_edges(
                        route,
                        truck.properties,
                        forward=True
                    ) / 60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, route, shovel, truck, unload. | qsimmine12/app/sim_engine/core/planner/manage.py:135 | Присваивает planning_data.T_haul[truck.id, shovel.id, unload.id] результат выражения. | TruckCalc, int, planning_data, route, shovel, truck, unload |
| 139 | `planning_data.T_return[truck.id, unload.id, shovel.id] = int(TruckCalc.calculate_time_motion_by_edges(
                        route,
                        truck.properties,
                        forward=False
                    ) / 60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, route, shovel, truck, unload. | qsimmine12/app/sim_engine/core/planner/manage.py:145 | Присваивает planning_data.T_return[truck.id, unload.id, shovel.id] результат выражения. | TruckCalc, int, planning_data, route, shovel, truck, unload |
| 140 | `planning_data.T_unload[truck.id, unload.id] = int(UnloadCalc.unload_calculation_by_norm(unload.properties, truck.properties)["t_total"] / 60)` | Операции: деление. Операнды: UnloadCalc, int, planning_data, truck, unload. | qsimmine12/app/sim_engine/core/planner/manage.py:157 | Присваивает planning_data.T_unload[truck.id, unload.id] результат выражения. | UnloadCalc, int, planning_data, truck, unload |
| 141 | `planning_data.T_end[truck.id, unload.id] = int(TruckCalc.calculate_time_motion_by_edges(
                    end_route,
                    truck.properties,
                    forward=True
                ) / 60)` | Операции: деление. Операнды: TruckCalc, end_route, int, planning_data, truck, unload. | qsimmine12/app/sim_engine/core/planner/manage.py:170 | Присваивает planning_data.T_end[truck.id, unload.id] результат выражения. | TruckCalc, end_route, int, planning_data, truck, unload |
| 142 | `planning_data.T_load[truck.id, shovel.id] = int(time_load / 60)` | Операции: деление. Операнды: int, planning_data, shovel, time_load, truck. | qsimmine12/app/sim_engine/core/planner/manage.py:87 | Присваивает planning_data.T_load[truck.id, shovel.id] результат выражения. | int, planning_data, shovel, time_load, truck |
| 143 | `planning_data.T_return[truck.id, unload.id, shovel.id] = int(TruckCalc.calculate_time_motion_by_edges(
                    route,
                    truck.properties,
                    forward=False
                ) / 60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, route, shovel, truck, unload. | qsimmine12/app/sim_engine/core/planner/planning_matrix.py:101 | Присваивает planning_data.T_return[truck.id, unload.id, shovel.id] результат выражения. | TruckCalc, int, planning_data, route, shovel, truck, unload |
| 144 | `planning_data.T_unload[truck.id, unload.id] = int(UnloadCalc.unload_calculation_by_norm(unload.properties, truck.properties)["t_total"] / 60)` | Операции: деление. Операнды: UnloadCalc, int, planning_data, truck, unload. | qsimmine12/app/sim_engine/core/planner/planning_matrix.py:113 | Присваивает planning_data.T_unload[truck.id, unload.id] результат выражения. | UnloadCalc, int, planning_data, truck, unload |
| 145 | `planning_data.T_end[truck.id, unload.id] = int(TruckCalc.calculate_time_motion_by_edges(
                end_route,
                truck.properties,
                forward=True
            ) / 60)` | Операции: деление. Операнды: TruckCalc, end_route, int, planning_data, truck, unload. | qsimmine12/app/sim_engine/core/planner/planning_matrix.py:126 | Присваивает planning_data.T_end[truck.id, unload.id] результат выражения. | TruckCalc, end_route, int, planning_data, truck, unload |
| 146 | `planning_data.T_load[truck.id, shovel.id] = int(time_load / 60)` | Операции: деление. Операнды: int, planning_data, shovel, time_load, truck. | qsimmine12/app/sim_engine/core/planner/planning_matrix.py:43 | Присваивает planning_data.T_load[truck.id, shovel.id] результат выражения. | int, planning_data, shovel, time_load, truck |
| 147 | `planning_data.T_start[truck.id, shovel.id] = int(TruckCalc.calculate_time_motion_by_edges(
                start_route,
                truck.properties,
                forward=True
            ) / 60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, shovel, start_route, truck. | qsimmine12/app/sim_engine/core/planner/planning_matrix.py:68 | Присваивает planning_data.T_start[truck.id, shovel.id] результат выражения. | TruckCalc, int, planning_data, shovel, start_route, truck |
| 148 | `planning_data.T_haul[truck.id, shovel.id, unload.id] = int(TruckCalc.calculate_time_motion_by_edges(
                    route,
                    truck.properties,
                    forward=True
                ) / 60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, route, shovel, truck, unload. | qsimmine12/app/sim_engine/core/planner/planning_matrix.py:91 | Присваивает planning_data.T_haul[truck.id, shovel.id, unload.id] результат выражения. | TruckCalc, int, planning_data, route, shovel, truck, unload |
| 149 | `model.Add(sum(choose_shovel[i, k, j] for j in J) <= sum(choose_shovel[i, k - 1, j] for j in J))` | Операции: вычитание. Операнды: J, choose_shovel, i, j, k, model, sum. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:105 | Вычисляет выражение без сохранения результата. | J, choose_shovel, i, j, k, model, sum |
| 150 | `terms.append(ton * choose_shovel[i, k, j])` | Операции: умножение. Операнды: choose_shovel, i, j, k, terms, ton. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:151 | Вычисляет выражение без сохранения результата. | choose_shovel, i, j, k, terms, ton |
| 151 | `model.Maximize(sum(terms))` | Операции: функции и литералы. Операнды: model, sum, terms. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:152 | Вычисляет выражение без сохранения результата. | model, sum, terms |
| 152 | `js = {j for (ti, j) in inst.T_start.keys() if ti == i}` | Операции: функции и литералы. Операнды: i, inst, j, ti. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:19 | Присваивает js результат выражения. | i, inst, j, ti |
| 153 | `zs = {z for (ti, z) in inst.T_end.keys() if ti == i}` | Операции: функции и литералы. Операнды: i, inst, ti, z. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:20 | Присваивает zs результат выражения. | i, inst, ti, z |
| 154 | `min_start = min(inst.T_start[i, j] for j in js)` | Операции: функции и литералы. Операнды: i, inst, j, js, min. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:21 | Присваивает min_start результат выражения. | i, inst, j, js, min |
| 155 | `min_end = min(inst.T_end[i, z] for z in zs)` | Операции: функции и литералы. Операнды: i, inst, min, z, zs. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:22 | Присваивает min_end результат выражения. | i, inst, min, z, zs |
| 156 | `min_d = min(
            inst.T_haul[i, j, z] + inst.T_return[i, z, j] + inst.T_load[i, j] + inst.T_unload[i, z]
            for j in js for z in zs
        )` | Операции: сложение. Операнды: i, inst, j, js, min, z, zs. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:23 | Присваивает min_d результат выражения. | i, inst, j, js, min, z, zs |
| 157 | `available = inst.D_work - min_start - min_end` | Операции: вычитание. Операнды: inst, min_end, min_start. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:27 | Присваивает available результат выражения. | inst, min_end, min_start |
| 158 | `return max(0, floor(available / max(1, min_d)))` | Операции: деление. Операнды: available, floor, max, min_d. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:28 | Возвращает результат вычисления. | available, floor, max, min_d |
| 159 | `H = 2 * inst.D_work` | Операции: умножение. Операнды: inst. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:39 | Присваивает H результат выражения. | inst |
| 160 | `Kmax_i = {i: cls.compute_Kmax_i(inst, i) for i in I}` | Операции: функции и литералы. Операнды: I, cls, i, inst. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:45 | Присваивает Kmax_i результат выражения. | I, cls, i, inst |
| 161 | `K = max(Kmax_i.values() or [0])` | Операции: функции и литералы. Операнды: Kmax_i, max. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:47 | Присваивает K результат выражения. | Kmax_i, max |
| 162 | `Kmax_i = {i: K for i in I}` | Операции: функции и литералы. Операнды: I, K, i. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:48 | Присваивает Kmax_i результат выражения. | I, K, i |
| 163 | `shovel_to_intervals = {j: [] for j in J}` | Операции: функции и литералы. Операнды: J, j. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:60 | Присваивает shovel_to_intervals результат выражения. | J, j |
| 164 | `dump_to_intervals = {z: [] for z in Zs}` | Операции: функции и литералы. Операнды: Zs, z. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:61 | Присваивает dump_to_intervals результат выражения. | Zs, z |
| 165 | `model.Add(sum(choose_shovel[i, k, j] for j in J) <= 1)` | Операции: функции и литералы. Операнды: J, choose_shovel, i, j, k, model, sum. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:98 | Вычисляет выражение без сохранения результата. | J, choose_shovel, i, j, k, model, sum |
| 166 | `model.Add(sum(choose_dump[i, k, z] for z in Zs) <= 1)` | Операции: функции и литералы. Операнды: Zs, choose_dump, i, k, model, sum, z. | qsimmine12/app/sim_engine/core/planner/solvers/cp.py:99 | Вычисляет выражение без сохранения результата. | Zs, choose_dump, i, k, model, sum, z |
| 167 | `trucks_count = len(shovel.trucks_queue) + len(moving_trucks)` | Операции: сложение. Операнды: len, moving_trucks, shovel. | qsimmine12/app/sim_engine/core/planner/solvers/greedy.py:158 | Присваивает trucks_count результат выражения. | len, moving_trucks, shovel |
| 168 | `wait_shovel = trucks_count * self.planning_data.T_load[(truck.id, shovel.id)]` | Операции: умножение. Операнды: self, shovel, truck, trucks_count. | qsimmine12/app/sim_engine/core/planner/solvers/greedy.py:159 | Присваивает wait_shovel результат выражения. | self, shovel, truck, trucks_count |
| 169 | `wait_unl = len(unld.trucks_queue) * self.planning_data.T_unload[(truck.id, unld.id)]` | Операции: умножение. Операнды: len, self, truck, unld. | qsimmine12/app/sim_engine/core/planner/solvers/greedy.py:164 | Присваивает wait_unl результат выражения. | len, self, truck, unld |
| 170 | `cycle_time = self.planning_data.T_start[(truck.id, shovel.id)] +
                        wait_shovel +
                        self.planning_data.T_load[(truck.id, shovel.id)] +
                        self.planning_data.T_haul[(truck.id, shovel.id, unld.id)] +
                        wait_unl +
                        self.planning_data.T_unload[(truck.id, unld.id)] +
                        self.planning_data.T_return[(truck.id, unld.id, shovel.id)]` | Операции: сложение. Операнды: self, shovel, truck, unld, wait_shovel, wait_unl. | qsimmine12/app/sim_engine/core/planner/solvers/greedy.py:166 | Присваивает cycle_time результат выражения. | self, shovel, truck, unld, wait_shovel, wait_unl |
| 171 | `score = tons / cycle_time` | Операции: деление. Операнды: cycle_time, tons. | qsimmine12/app/sim_engine/core/planner/solvers/greedy.py:176 | Присваивает score результат выражения. | cycle_time, tons |
| 172 | `truck.initial_edge_id = sim_truck.edge.index if sim_truck.edge else None` | Операции: функции и литералы. Операнды: sim_truck, truck. | qsimmine12/app/sim_engine/core/planner/solvers/greedy.py:65 | Присваивает truck.initial_edge_id результат выражения. | sim_truck, truck |
| 173 | `model += y[i, k + 1] <= y[i, k]` | Операции: сложение. Операнды: i, k, y. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:106 | Обновляет model через сложение. | i, k, y |
| 174 | `model += s_load[i, k] >= a_arr[i, k]` | Операции: функции и литералы. Операнды: a_arr, i, k, s_load. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:114 | Обновляет model через сложение. | a_arr, i, k, s_load |
| 175 | `model += s_unload[i, k] >= s_load[i, k] + lpSum(
                x[i, k, j, z] * (inst.T_load[i, j] + inst.T_haul[i, j, z])
                for j in J for z in Z
            )` | Операции: сложение, умножение. Операнды: J, Z, i, inst, j, k, lpSum, s_load, s_unload, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:120 | Обновляет model через сложение. | J, Z, i, inst, j, k, lpSum, s_load, s_unload, x, z |
| 176 | `model += a_arr[i, k + 1] >= s_unload[i, k] + \
                         lpSum(b_use(i, k, z) * inst.T_unload[i, z] for z in Z) + \
                         lpSum(q[i, k, j, z] * inst.T_return[i, z, j] for j in J for z in Z)` | Операции: сложение, умножение. Операнды: J, Z, a_arr, b_use, i, inst, j, k, lpSum, q, s_unload, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:128 | Обновляет model через сложение. | J, Z, a_arr, b_use, i, inst, j, k, lpSum, q, s_unload, z |
| 177 | `model += lpSum(q[i, k, j, z] for j in J) <= b_use(i, k, z)` | Операции: функции и литералы. Операнды: J, b_use, i, j, k, lpSum, q, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:134 | Обновляет model через сложение. | J, b_use, i, j, k, lpSum, q, z |
| 178 | `model += lpSum(q[i, k, j, z] for z in Z) <= a_use(i, k + 1, j)` | Операции: сложение. Операнды: Z, a_use, i, j, k, lpSum, q, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:136 | Обновляет model через сложение. | Z, a_use, i, j, k, lpSum, q, z |
| 179 | `model += s_load[i, k] >= a_arr[i, k]` | Операции: функции и литералы. Операнды: a_arr, i, k, s_load. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:140 | Обновляет model через сложение. | a_arr, i, k, s_load |
| 180 | `model += ell[i, k] <= y[i, k]` | Операции: функции и литералы. Операнды: ell, i, k, y. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:146 | Обновляет model через сложение. | ell, i, k, y |
| 181 | `model += ell[i, k] <= 1 - y[i, k + 1]` | Операции: вычитание, сложение. Операнды: ell, i, k, y. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:148 | Обновляет model через сложение. | ell, i, k, y |
| 182 | `model += ell[i, k] >= y[i, k] - y[i, k + 1]` | Операции: вычитание, сложение. Операнды: ell, i, k, y. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:149 | Обновляет model через сложение. | ell, i, k, y |
| 183 | `model += s_unload[i, k] + \
                         lpSum(b_use(i, k, z) * (inst.T_unload[i, z] + inst.T_end[i, z]) for z in Z) \
                         <= inst.D_work + Mbig * (1 - ell[i, k])` | Операции: вычитание, сложение, умножение. Операнды: Mbig, Z, b_use, ell, i, inst, k, lpSum, s_unload, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:153 | Обновляет model через сложение. | Mbig, Z, b_use, ell, i, inst, k, lpSum, s_unload, z |
| 184 | `model += a_arr[p] - a_arr[q_] <= Mbig * (1 - wvar)` | Операции: вычитание, умножение. Операнды: Mbig, a_arr, p, q_, wvar. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:176 | Обновляет model через сложение. | Mbig, a_arr, p, q_, wvar |
| 185 | `model += a_arr[q_] - a_arr[p] <= Mbig * wvar - eps` | Операции: вычитание, умножение. Операнды: Mbig, a_arr, eps, p, q_, wvar. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:177 | Обновляет model через сложение. | Mbig, a_arr, eps, p, q_, wvar |
| 186 | `load_p = lpSum(x[p[0], p[1], j, z] * inst.T_load[p[0], j] for z in Z)` | Операции: умножение. Операнды: Z, inst, j, lpSum, p, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:183 | Присваивает load_p результат выражения. | Z, inst, j, lpSum, p, x, z |
| 187 | `load_q = lpSum(x[q_[0], q_[1], j, z] * inst.T_load[q_[0], j] for z in Z)` | Операции: умножение. Операнды: Z, inst, j, lpSum, q_, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:184 | Присваивает load_q результат выражения. | Z, inst, j, lpSum, q_, x, z |
| 188 | `model += s_load[q_] >= s_load[p] + load_p - Mbig * (1 - wvar) - Mbig * (2 - xpj - xqj)` | Операции: вычитание, сложение, умножение. Операнды: Mbig, load_p, p, q_, s_load, wvar, xpj, xqj. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:189 | Обновляет model через сложение. | Mbig, load_p, p, q_, s_load, wvar, xpj, xqj |
| 189 | `model += s_load[p] >= s_load[q_] + load_q - Mbig * wvar - Mbig * (2 - xpj - xqj)` | Операции: вычитание, сложение, умножение. Операнды: Mbig, load_q, p, q_, s_load, wvar, xpj, xqj. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:190 | Обновляет model через сложение. | Mbig, load_q, p, q_, s_load, wvar, xpj, xqj |
| 190 | `obj_tons = lpSum(inst.m_tons[i, j] * x[i, k, j, z] for (i, k) in P for j in J for z in Z)` | Операции: умножение. Операнды: J, P, Z, i, inst, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:194 | Присваивает obj_tons результат выражения. | J, P, Z, i, inst, j, k, lpSum, x, z |
| 191 | `obj_trips = lpSum(x[i, k, j, z] for (i, k) in P for j in J for z in Z)` | Операции: функции и литералы. Операнды: J, P, Z, i, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:195 | Присваивает obj_trips результат выражения. | J, P, Z, i, j, k, lpSum, x, z |
| 192 | `js = {j for (ti, j) in inst.T_start.keys() if ti == i}` | Операции: функции и литералы. Операнды: i, inst, j, ti. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:24 | Присваивает js результат выражения. | i, inst, j, ti |
| 193 | `zs = {z for (ti, z) in inst.T_end.keys() if ti == i}` | Операции: функции и литералы. Операнды: i, inst, ti, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:25 | Присваивает zs результат выражения. | i, inst, ti, z |
| 194 | `min_start = min(inst.T_start[i, j] for j in js)` | Операции: функции и литералы. Операнды: i, inst, j, js, min. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:26 | Присваивает min_start результат выражения. | i, inst, j, js, min |
| 195 | `chosen = [(j, z) for j in J for z in Z if x[i, k, j, z].value() and x[i, k, j, z].value() > 0.5]` | Операции: функции и литералы. Операнды: J, Z, i, j, k, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:267 | Присваивает chosen результат выражения. | J, Z, i, j, k, x, z |
| 196 | `min_end = min(inst.T_end[i, z] for z in zs)` | Операции: функции и литералы. Операнды: i, inst, min, z, zs. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:27 | Присваивает min_end результат выражения. | i, inst, min, z, zs |
| 197 | `min_d = min(
            inst.T_haul[i, j, z] + inst.T_return[i, z, j] + inst.T_load[i, j] + inst.T_unload[i, z]
            for j in js for z in zs
        )` | Операции: сложение. Операнды: i, inst, j, js, min, z, zs. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:28 | Присваивает min_d результат выражения. | i, inst, j, js, min, z, zs |
| 198 | `available = inst.D_work - min_start - min_end` | Операции: вычитание. Операнды: inst, min_end, min_start. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:32 | Присваивает available результат выражения. | inst, min_end, min_start |
| 199 | `return max(0, floor(available / max(1, min_d)))` | Операции: деление. Операнды: available, floor, max, min_d. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:33 | Возвращает результат вычисления. | available, floor, max, min_d |
| 200 | `return {i: cls.compute_Kmax_i(inst, i) for i in inst.truck_ids}` | Операции: функции и литералы. Операнды: cls, i, inst. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:38 | Возвращает результат вычисления. | cls, i, inst |
| 201 | `P = [(i, k) for i in I for k in range(1, Kmax[i] + 1)]` | Операции: сложение. Операнды: I, Kmax, List, Tuple, i, int, k, range. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:51 | Присваивает P результат выражения с аннотацией. | I, Kmax, List, Tuple, i, int, k, range |
| 202 | `x = {(i, k, j, z): LpVariable(f"x_{i}_{k}_{j}_{z}", 0, 1, LpBinary)
             for (i, k) in P for j in J for z in Z}` | Операции: функции и литералы. Операнды: J, LpBinary, LpVariable, P, Z, i, j, k, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:63 | Присваивает x результат выражения. | J, LpBinary, LpVariable, P, Z, i, j, k, z |
| 203 | `y = {(i, k): LpVariable(f"y_{i}_{k}", 0, 1, LpBinary) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpBinary, LpVariable, P, i, k. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:67 | Присваивает y результат выражения. | LpBinary, LpVariable, P, i, k |
| 204 | `s_load = {(i, k): LpVariable(f"sLoad_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpInteger, LpVariable, P, i, k. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:73 | Присваивает s_load результат выражения. | LpInteger, LpVariable, P, i, k |
| 205 | `s_unload = {(i, k): LpVariable(f"sUnload_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpInteger, LpVariable, P, i, k. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:74 | Присваивает s_unload результат выражения. | LpInteger, LpVariable, P, i, k |
| 206 | `a_arr = {(i, k): LpVariable(f"aArr_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpInteger, LpVariable, P, i, k. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:75 | Присваивает a_arr результат выражения. | LpInteger, LpVariable, P, i, k |
| 207 | `q = {(i, k, j, z): LpVariable(f"q_{i}_{k}_{j}_{z}", 0, 1, LpBinary)
             for i in I for k in range(1, Kmax[i]) for j in J for z in Z}` | Операции: функции и литералы. Операнды: I, J, Kmax, LpBinary, LpVariable, Z, i, j, k, range, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:76 | Присваивает q результат выражения. | I, J, Kmax, LpBinary, LpVariable, Z, i, j, k, range, z |
| 208 | `ell = {(i, k): LpVariable(f"ell_{i}_{k}", 0, 1, LpBinary) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpBinary, LpVariable, P, i, k. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:78 | Присваивает ell результат выражения. | LpBinary, LpVariable, P, i, k |
| 209 | `return lpSum(x[i, k, j, z] for z in Z)` | Операции: функции и литералы. Операнды: Z, i, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:94 | Возвращает результат вычисления. | Z, i, j, k, lpSum, x, z |
| 210 | `return lpSum(x[i, k, j, z] for j in J)` | Операции: функции и литералы. Операнды: J, i, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/core/planner/solvers/milp.py:97 | Возвращает результат вычисления. | J, i, j, k, lpSum, x, z |
| 211 | `return [area for area in self.areas if area.is_lunch_area]` | Операции: функции и литералы. Операнды: area, self. | qsimmine12/app/sim_engine/core/props.py:120 | Возвращает результат вычисления. | area, self |
| 212 | `return [area for area in self.areas if area.is_shift_change_area]` | Операции: функции и литералы. Операнды: area, self. | qsimmine12/app/sim_engine/core/props.py:124 | Возвращает результат вычисления. | area, self |
| 213 | `return [area for area in self.areas if area.is_planned_idle_area]` | Операции: функции и литералы. Операнды: area, self. | qsimmine12/app/sim_engine/core/props.py:128 | Возвращает результат вычисления. | area, self |
| 214 | `return [area for area in self.areas if area.is_blast_waiting_area]` | Операции: функции и литералы. Операнды: area, self. | qsimmine12/app/sim_engine/core/props.py:132 | Возвращает результат вычисления. | area, self |
| 215 | `time_to_lunch = nearest_lunch_start - self.env.now` | Операции: вычитание. Операнды: int, nearest_lunch_start, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/base.py:138 | Присваивает time_to_lunch результат выражения с аннотацией. | int, nearest_lunch_start, self |
| 216 | `lunch_time_remaining = nearest_lunch_end - self.env.now` | Операции: вычитание. Операнды: int, nearest_lunch_end, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/base.py:147 | Присваивает lunch_time_remaining результат выражения с аннотацией. | int, nearest_lunch_end, self |
| 217 | `wait_time = nearest_idle_start - self.env.now` | Операции: вычитание. Операнды: nearest_idle_start, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/base.py:198 | Присваивает wait_time результат выражения. | nearest_idle_start, self |
| 218 | `idle_time_remaining = nearest_idle_end - self.env.now` | Операции: вычитание. Операнды: int, nearest_idle_end, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/base.py:207 | Присваивает idle_time_remaining результат выражения с аннотацией. | int, nearest_idle_end, self |
| 219 | `remember_zones = {blasting.id for blasting in self.target.quarry.active_blasting}` | Операции: функции и литералы. Операнды: blasting, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/blasting.py:134 | Присваивает remember_zones результат выражения. | blasting, self |
| 220 | `remember_zones = {blasting.id for blasting in self.target.quarry.active_blasting}` | Операции: функции и литералы. Операнды: blasting, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/blasting.py:191 | Присваивает remember_zones результат выражения. | blasting, self |
| 221 | `blasting_list = [b for b in blasting_list if self.env.now < b.end_time]` | Операции: функции и литералы. Операнды: b, blasting_list, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/blasting.py:57 | Присваивает blasting_list результат выражения. | b, blasting_list, self |
| 222 | `active_blasting = [b for b in blasting_list if b.start_time <= self.env.now < b.end_time]` | Операции: функции и литералы. Операнды: b, blasting_list, self. | qsimmine12/app/sim_engine/core/simulations/behaviors/blasting.py:58 | Присваивает active_blasting результат выражения. | b, blasting_list, self |
| 223 | `self.target.active_blasting_polygons = [zone for blasting in active_blasting for zone in blasting.zones]` | Операции: функции и литералы. Операнды: active_blasting, blasting, self, zone. | qsimmine12/app/sim_engine/core/simulations/behaviors/blasting.py:61 | Присваивает self.target.active_blasting_polygons результат выражения. | active_blasting, blasting, self, zone |
| 224 | `active_ids = {b.id for b in active_blasting}` | Операции: функции и литералы. Операнды: active_blasting, b. | qsimmine12/app/sim_engine/core/simulations/behaviors/blasting.py:67 | Присваивает active_ids результат выражения. | active_blasting, b |
| 225 | `completed_ids = set(self.active_blasting_dict.keys()) - active_ids` | Операции: вычитание. Операнды: active_ids, self, set. | qsimmine12/app/sim_engine/core/simulations/behaviors/blasting.py:69 | Присваивает completed_ids результат выражения. | active_ids, self, set |
| 226 | `current_time = self.start_time + timedelta(seconds=self.env.now)` | Операции: сложение. Операнды: self, timedelta. | qsimmine12/app/sim_engine/core/simulations/fuel_station.py:35 | Присваивает current_time результат выражения. | self, timedelta |
| 227 | `fuel_needed = truck.properties.fuel_capacity - truck.fuel` | Операции: вычитание. Операнды: truck. | qsimmine12/app/sim_engine/core/simulations/fuel_station.py:44 | Присваивает fuel_needed результат выражения. | truck |
| 228 | `refuel_time = fuel_needed / self.properties.flow_rate` | Операции: деление. Операнды: fuel_needed, self. | qsimmine12/app/sim_engine/core/simulations/fuel_station.py:45 | Присваивает refuel_time результат выражения. | fuel_needed, self |
| 229 | `truck.initial_edge_id = sim_truck.edge.index if sim_truck.edge else None` | Операции: функции и литералы. Операнды: sim_truck, truck. | qsimmine12/app/sim_engine/core/simulations/quarry.py:100 | Присваивает truck.initial_edge_id результат выражения. | sim_truck, truck |
| 230 | `self.blasting_proc = QuarryBlastingWatcher(
            target=self,
        ) if self.sim_conf["blasting"] else None` | Операции: функции и литералы. Операнды: QuarryBlastingWatcher, self. | qsimmine12/app/sim_engine/core/simulations/quarry.py:60 | Присваивает self.blasting_proc результат выражения. | QuarryBlastingWatcher, self |
| 231 | `return self.start_time + timedelta(seconds=self.env.now)` | Операции: сложение. Операнды: self, timedelta. | qsimmine12/app/sim_engine/core/simulations/quarry.py:66 | Возвращает результат вычисления. | self, timedelta |
| 232 | `self.breakdown = BreakdownBehavior(self, properties) if self.sim_conf["breakdown"] else None` | Операции: функции и литералы. Операнды: BreakdownBehavior, properties, self. | qsimmine12/app/sim_engine/core/simulations/shovel.py:49 | Присваивает self.breakdown результат выражения. | BreakdownBehavior, properties, self |
| 233 | `self.planned_idle_proc = PlannedIdleBehavior(
            target=self,
            object_type=ObjectType.SHOVEL,
        ) if self.sim_conf["planned_idle"] and self.quarry.sim_data.planned_idles.get((ObjectType.SHOVEL.key(), self.id)) else None` | Операции: функции и литералы. Операнды: ObjectType, PlannedIdleBehavior, self. | qsimmine12/app/sim_engine/core/simulations/shovel.py:53 | Присваивает self.planned_idle_proc результат выражения. | ObjectType, PlannedIdleBehavior, self |
| 234 | `self.blasting_proc = ShovelBlastingWatcher(
            target=self,
        ) if self.sim_conf["blasting"] else None` | Операции: функции и литералы. Операнды: ShovelBlastingWatcher, self. | qsimmine12/app/sim_engine/core/simulations/shovel.py:60 | Присваивает self.blasting_proc результат выражения. | ShovelBlastingWatcher, self |
| 235 | `return self.start_time + timedelta(seconds=self.env.now)` | Операции: сложение. Операнды: self, timedelta. | qsimmine12/app/sim_engine/core/simulations/shovel.py:69 | Возвращает результат вычисления. | self, timedelta |
| 236 | `return self.trucks_queue[0] if self.trucks_queue else None` | Операции: функции и литералы. Операнды: self. | qsimmine12/app/sim_engine/core/simulations/shovel.py:78 | Возвращает результат вычисления. | self |
| 237 | `return self.trucks_queue[1:] if len(self.trucks_queue) > 1 else None` | Операции: функции и литералы. Операнды: len, self. | qsimmine12/app/sim_engine/core/simulations/shovel.py:83 | Возвращает результат вычисления. | len, self |
| 238 | `truck.state = TruckState.REPAIR if truck.broken else TruckState.IDLE` | Операции: функции и литералы. Операнды: TruckState, truck. | qsimmine12/app/sim_engine/core/simulations/shovel.py:95 | Присваивает truck.state результат выражения. | TruckState, truck |
| 239 | `self.fuel_proc = FuelBehavior(self, properties) if self.sim_conf["refuel"] and self.fuel_stations else None` | Операции: функции и литералы. Операнды: FuelBehavior, properties, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:101 | Присваивает self.fuel_proc результат выражения. | FuelBehavior, properties, self |
| 240 | `self.lunch_proc = LunchBehavior(
            target=self
        ) if self.sim_conf["lunch"] and self.quarry.sim_data.lunch_times else None` | Операции: функции и литералы. Операнды: LunchBehavior, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:105 | Присваивает self.lunch_proc результат выражения. | LunchBehavior, self |
| 241 | `self.planned_idle_proc = PlannedIdleBehavior(
            target=self,
            object_type=ObjectType.TRUCK,
        ) if self.sim_conf["planned_idle"] and self.quarry.sim_data.planned_idles.get(
            (ObjectType.TRUCK.key(), self.id)
        ) else None` | Операции: функции и литералы. Операнды: ObjectType, PlannedIdleBehavior, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:111 | Присваивает self.planned_idle_proc результат выражения. | ObjectType, PlannedIdleBehavior, self |
| 242 | `self.blasting_proc = TruckBlastingWatcher(
            target=self
        ) if self.sim_conf["blasting"] else None` | Операции: функции и литералы. Операнды: TruckBlastingWatcher, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:119 | Присваивает self.blasting_proc результат выражения. | TruckBlastingWatcher, self |
| 243 | `nearest_fs = min(self.fuel_stations, key=lambda fs: haversine_km(self.position, fs.position))` | Операции: функции и литералы. Операнды: fs, haversine_km, min, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:129 | Присваивает nearest_fs результат выражения. | fs, haversine_km, min, self |
| 244 | `return self.start_time + timedelta(seconds=self.env.now)` | Операции: сложение. Операнды: self, timedelta. | qsimmine12/app/sim_engine/core/simulations/truck.py:136 | Возвращает результат вычисления. | self, timedelta |
| 245 | `restricted_zones = self.quarry.restricted_zones if self.state != TruckState.MOVING_LOADED else []` | Операции: функции и литералы. Операнды: TruckState, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:156 | Присваивает restricted_zones результат выражения. | TruckState, self |
| 246 | `remember_zones = {blasting.id for blasting in self.quarry.active_blasting}` | Операции: функции и литералы. Операнды: blasting, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:287 | Присваивает remember_zones результат выражения. | blasting, self |
| 247 | `restricted_zones = self.quarry.restricted_zones if attention_to_restricted_zones else []` | Операции: функции и литералы. Операнды: attention_to_restricted_zones, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:328 | Присваивает restricted_zones результат выражения. | attention_to_restricted_zones, self |
| 248 | `remember_blasting_zones = {blasting.id for blasting in self.quarry.active_blasting}` | Операции: функции и литералы. Операнды: blasting, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:361 | Присваивает remember_blasting_zones результат выражения. | blasting, self |
| 249 | `restricted_zones = self.quarry.active_blasting_polygons if attention_to_restricted_zones else []` | Операции: функции и литералы. Операнды: attention_to_restricted_zones, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:368 | Присваивает restricted_zones результат выражения. | attention_to_restricted_zones, self |
| 250 | `destination_point = route.end_point if forward else route.start_point` | Операции: функции и литералы. Операнды: forward, route. | qsimmine12/app/sim_engine/core/simulations/truck.py:406 | Присваивает destination_point результат выражения. | forward, route |
| 251 | `shovel_id = self.shovel.id if self.shovel else None` | Операции: функции и литералы. Операнды: self. | qsimmine12/app/sim_engine/core/simulations/truck.py:630 | Присваивает shovel_id результат выражения. | self |
| 252 | `unload_id = self.unload.id if self.unload else None` | Операции: функции и литералы. Операнды: self. | qsimmine12/app/sim_engine/core/simulations/truck.py:631 | Присваивает unload_id результат выражения. | self |
| 253 | `self.breakdown_proc = BreakdownBehavior(self, properties) if self.sim_conf["breakdown"] else None` | Операции: функции и литералы. Операнды: BreakdownBehavior, properties, self. | qsimmine12/app/sim_engine/core/simulations/truck.py:97 | Присваивает self.breakdown_proc результат выражения. | BreakdownBehavior, properties, self |
| 254 | `self.breakdown_proc = BreakdownBehavior(self, properties) if self.sim_conf["breakdown"] else None` | Операции: функции и литералы. Операнды: BreakdownBehavior, properties, self. | qsimmine12/app/sim_engine/core/simulations/unload.py:43 | Присваивает self.breakdown_proc результат выражения. | BreakdownBehavior, properties, self |
| 255 | `self.blasting_proc = UnloadBlastingWatcher(
            self,
        ) if self.sim_conf["blasting"] else None` | Операции: функции и литералы. Операнды: UnloadBlastingWatcher, self. | qsimmine12/app/sim_engine/core/simulations/unload.py:47 | Присваивает self.blasting_proc результат выражения. | UnloadBlastingWatcher, self |
| 256 | `return self.start_time + timedelta(seconds=self.env.now)` | Операции: сложение. Операнды: self, timedelta. | qsimmine12/app/sim_engine/core/simulations/unload.py:56 | Возвращает результат вычисления. | self, timedelta |
| 257 | `return self.trucks_queue[0] if self.trucks_queue else None` | Операции: функции и литералы. Операнды: self. | qsimmine12/app/sim_engine/core/simulations/unload.py:65 | Возвращает результат вычисления. | self |
| 258 | `return self.trucks_queue[self.properties.trucks_at_once:] if len(self.trucks_queue) > self.properties.trucks_at_once else None` | Операции: функции и литералы. Операнды: len, self. | qsimmine12/app/sim_engine/core/simulations/unload.py:70 | Возвращает результат вычисления. | len, self |
| 259 | `weight_in_second = truck.weight / time_unload` | Операции: деление. Операнды: time_unload, truck. | qsimmine12/app/sim_engine/core/simulations/unload.py:78 | Присваивает weight_in_second результат выражения. | time_unload, truck |
| 260 | `volume_in_second = truck.volume / time_unload` | Операции: деление. Операнды: time_unload, truck. | qsimmine12/app/sim_engine/core/simulations/unload.py:79 | Присваивает volume_in_second результат выражения. | time_unload, truck |
| 261 | `truck.state = TruckState.REPAIR if truck.broken else TruckState.IDLE` | Операции: функции и литералы. Операнды: TruckState, truck. | qsimmine12/app/sim_engine/core/simulations/unload.py:83 | Присваивает truck.state результат выражения. | TruckState, truck |
| 262 | `truck.weight = max(0, truck.weight - weight_in_second)` | Операции: вычитание. Операнды: max, truck, weight_in_second. | qsimmine12/app/sim_engine/core/simulations/unload.py:87 | Присваивает truck.weight результат выражения. | max, truck, weight_in_second |
| 263 | `truck.volume = max(0, truck.volume - volume_in_second)` | Операции: вычитание. Операнды: max, truck, volume_in_second. | qsimmine12/app/sim_engine/core/simulations/unload.py:88 | Присваивает truck.volume результат выражения. | max, truck, volume_in_second |
| 264 | `return env.sim_data.start_time + timedelta(seconds=env.now)` | Операции: сложение. Операнды: env, timedelta. | qsimmine12/app/sim_engine/core/simulations/utils/helpers.py:12 | Возвращает результат вычисления. | env, timedelta |
| 265 | `length = sum([edge.length for edge in route.edges])` | Операции: функции и литералы. Операнды: edge, route, sum. | qsimmine12/app/sim_engine/core/simulations/utils/idle_area_service.py:70 | Присваивает length результат выражения. | edge, route, sum |
| 266 | `return sum(data_list) / len(data_list)` | Операции: деление. Операнды: data_list, len, sum. | qsimmine12/app/sim_engine/core/simulations/utils/statistic_service.py:854 | Возвращает результат вычисления. | data_list, len, sum |
| 267 | `mean = self._calculate_mean(data_list)` | Операции: функции и литералы. Операнды: data_list, self. | qsimmine12/app/sim_engine/core/simulations/utils/statistic_service.py:872 | Присваивает mean результат выражения. | data_list, self |
| 268 | `squared_deviations = [(x - mean) ** 2 for x in data_list]` | Операции: вычитание, степень. Операнды: data_list, mean, x. | qsimmine12/app/sim_engine/core/simulations/utils/statistic_service.py:876 | Присваивает squared_deviations результат выражения. | data_list, mean, x |
| 269 | `return sum(squared_deviations) / (len(data_list) - 1)` | Операции: вычитание, деление. Операнды: data_list, len, squared_deviations, sum. | qsimmine12/app/sim_engine/core/simulations/utils/statistic_service.py:877 | Возвращает результат вычисления. | data_list, len, squared_deviations, sum |
| 270 | `lunches_duration_total = sum([(lunch[1] - lunch[0]).total_seconds() for lunch in sim_data.lunch_times])` | Операции: вычитание. Операнды: lunch, sim_data, sum. | qsimmine12/app/sim_engine/core/simulations/utils/statistic_service.py:889 | Присваивает lunches_duration_total результат выражения. | lunch, sim_data, sum |
| 271 | `self.shovel_stats.totals.lunches_duration = lunches_duration_total * shovels_quantity` | Операции: умножение. Операнды: lunches_duration_total, self, shovels_quantity. | qsimmine12/app/sim_engine/core/simulations/utils/statistic_service.py:890 | Присваивает self.shovel_stats.totals.lunches_duration результат выражения. | lunches_duration_total, self, shovels_quantity |
| 272 | `self.hourly_volume[hour] = int(self.hourly_volume[hour] + round_volume)` | Операции: сложение. Операнды: hour, int, round_volume, self. | qsimmine12/app/sim_engine/core/simulations/utils/trip_service.py:166 | Присваивает self.hourly_volume[hour] результат выражения. | hour, int, round_volume, self |
| 273 | `self.hourly_weight[hour] = int(self.hourly_weight[hour] + round_weight)` | Операции: сложение. Операнды: hour, int, round_weight, self. | qsimmine12/app/sim_engine/core/simulations/utils/trip_service.py:167 | Присваивает self.hourly_weight[hour] результат выражения. | hour, int, round_weight, self |
| 274 | `hours = list(range(start_hour, end_hour + 1))` | Операции: сложение. Операнды: end_hour, list, range, start_hour. | qsimmine12/app/sim_engine/core/simulations/utils/trip_service.py:77 | Присваивает hours результат выражения. | end_hour, list, range, start_hour |
| 275 | `hours = list(range(start_hour, 24)) + list(range(0, end_hour + 1))` | Операции: сложение. Операнды: end_hour, list, range, start_hour. | qsimmine12/app/sim_engine/core/simulations/utils/trip_service.py:79 | Присваивает hours результат выражения. | end_hour, list, range, start_hour |
| 276 | `x = {(i, k, j, z): LpVariable(f"x_{i}_{k}_{j}_{z}", 0, 1, LpBinary)
         for (i, k) in P for j in J for z in Z}` | Операции: функции и литералы. Операнды: J, LpBinary, LpVariable, P, Z, i, j, k, z. | qsimmine12/app/sim_engine/planner.py:106 | Присваивает x результат выражения. | J, LpBinary, LpVariable, P, Z, i, j, k, z |
| 277 | `y = {(i, k): LpVariable(f"y_{i}_{k}", 0, 1, LpBinary) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpBinary, LpVariable, P, i, k. | qsimmine12/app/sim_engine/planner.py:110 | Присваивает y результат выражения. | LpBinary, LpVariable, P, i, k |
| 278 | `s_load = {(i, k): LpVariable(f"sLoad_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpInteger, LpVariable, P, i, k. | qsimmine12/app/sim_engine/planner.py:116 | Присваивает s_load результат выражения. | LpInteger, LpVariable, P, i, k |
| 279 | `s_unload = {(i, k): LpVariable(f"sUnload_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpInteger, LpVariable, P, i, k. | qsimmine12/app/sim_engine/planner.py:117 | Присваивает s_unload результат выражения. | LpInteger, LpVariable, P, i, k |
| 280 | `a_arr = {(i, k): LpVariable(f"aArr_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpInteger, LpVariable, P, i, k. | qsimmine12/app/sim_engine/planner.py:118 | Присваивает a_arr результат выражения. | LpInteger, LpVariable, P, i, k |
| 281 | `q = {(i, k, j, z): LpVariable(f"q_{i}_{k}_{j}_{z}", 0, 1, LpBinary)
         for i in I for k in range(1, Kmax[i]) for j in J for z in Z}` | Операции: функции и литералы. Операнды: I, J, Kmax, LpBinary, LpVariable, Z, i, j, k, range, z. | qsimmine12/app/sim_engine/planner.py:119 | Присваивает q результат выражения. | I, J, Kmax, LpBinary, LpVariable, Z, i, j, k, range, z |
| 282 | `ell = {(i, k): LpVariable(f"ell_{i}_{k}", 0, 1, LpBinary) for (i, k) in P}` | Операции: функции и литералы. Операнды: LpBinary, LpVariable, P, i, k. | qsimmine12/app/sim_engine/planner.py:121 | Присваивает ell результат выражения. | LpBinary, LpVariable, P, i, k |
| 283 | `return lpSum(x[i, k, j, z] for z in Z)` | Операции: функции и литералы. Операнды: Z, i, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/planner.py:137 | Возвращает результат вычисления. | Z, i, j, k, lpSum, x, z |
| 284 | `return lpSum(x[i, k, j, z] for j in J)` | Операции: функции и литералы. Операнды: J, i, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/planner.py:140 | Возвращает результат вычисления. | J, i, j, k, lpSum, x, z |
| 285 | `model += y[i, k + 1] <= y[i, k]` | Операции: сложение. Операнды: i, k, y. | qsimmine12/app/sim_engine/planner.py:149 | Обновляет model через сложение. | i, k, y |
| 286 | `model += s_load[i, k] >= a_arr[i, k]` | Операции: функции и литералы. Операнды: a_arr, i, k, s_load. | qsimmine12/app/sim_engine/planner.py:157 | Обновляет model через сложение. | a_arr, i, k, s_load |
| 287 | `model += s_unload[i, k] >= s_load[i, k] + lpSum(
            x[i, k, j, z] * (inst.T_load[i, j] + inst.T_haul[i, j, z])
            for j in J for z in Z
        )` | Операции: сложение, умножение. Операнды: J, Z, i, inst, j, k, lpSum, s_load, s_unload, x, z. | qsimmine12/app/sim_engine/planner.py:163 | Обновляет model через сложение. | J, Z, i, inst, j, k, lpSum, s_load, s_unload, x, z |
| 288 | `model += a_arr[i, k + 1] >= s_unload[i, k] + \
                     lpSum(b_use(i, k, z) * inst.T_unload[i, z] for z in Z) + \
                     lpSum(q[i, k, j, z] * inst.T_return[i, z, j] for j in J for z in Z)` | Операции: сложение, умножение. Операнды: J, Z, a_arr, b_use, i, inst, j, k, lpSum, q, s_unload, z. | qsimmine12/app/sim_engine/planner.py:171 | Обновляет model через сложение. | J, Z, a_arr, b_use, i, inst, j, k, lpSum, q, s_unload, z |
| 289 | `model += lpSum(q[i, k, j, z] for j in J) <= b_use(i, k, z)` | Операции: функции и литералы. Операнды: J, b_use, i, j, k, lpSum, q, z. | qsimmine12/app/sim_engine/planner.py:177 | Обновляет model через сложение. | J, b_use, i, j, k, lpSum, q, z |
| 290 | `model += lpSum(q[i, k, j, z] for z in Z) <= a_use(i, k + 1, j)` | Операции: сложение. Операнды: Z, a_use, i, j, k, lpSum, q, z. | qsimmine12/app/sim_engine/planner.py:179 | Обновляет model через сложение. | Z, a_use, i, j, k, lpSum, q, z |
| 291 | `model += s_load[i, k] >= a_arr[i, k]` | Операции: функции и литералы. Операнды: a_arr, i, k, s_load. | qsimmine12/app/sim_engine/planner.py:183 | Обновляет model через сложение. | a_arr, i, k, s_load |
| 292 | `model += ell[i, k] <= y[i, k]` | Операции: функции и литералы. Операнды: ell, i, k, y. | qsimmine12/app/sim_engine/planner.py:189 | Обновляет model через сложение. | ell, i, k, y |
| 293 | `model += ell[i, k] <= 1 - y[i, k + 1]` | Операции: вычитание, сложение. Операнды: ell, i, k, y. | qsimmine12/app/sim_engine/planner.py:191 | Обновляет model через сложение. | ell, i, k, y |
| 294 | `model += ell[i, k] >= y[i, k] - y[i, k + 1]` | Операции: вычитание, сложение. Операнды: ell, i, k, y. | qsimmine12/app/sim_engine/planner.py:192 | Обновляет model через сложение. | ell, i, k, y |
| 295 | `model += s_unload[i, k] + \
                     lpSum(b_use(i, k, z) * (inst.T_unload[i, z] + inst.T_end[i, z]) for z in Z) \
                     <= inst.D_work + Mbig * (1 - ell[i, k])` | Операции: вычитание, сложение, умножение. Операнды: Mbig, Z, b_use, ell, i, inst, k, lpSum, s_unload, z. | qsimmine12/app/sim_engine/planner.py:196 | Обновляет model через сложение. | Mbig, Z, b_use, ell, i, inst, k, lpSum, s_unload, z |
| 296 | `model += a_arr[p] - a_arr[q_] <= Mbig * (1 - wvar)` | Операции: вычитание, умножение. Операнды: Mbig, a_arr, p, q_, wvar. | qsimmine12/app/sim_engine/planner.py:219 | Обновляет model через сложение. | Mbig, a_arr, p, q_, wvar |
| 297 | `model += a_arr[q_] - a_arr[p] <= Mbig * wvar - eps` | Операции: вычитание, умножение. Операнды: Mbig, a_arr, eps, p, q_, wvar. | qsimmine12/app/sim_engine/planner.py:220 | Обновляет model через сложение. | Mbig, a_arr, eps, p, q_, wvar |
| 298 | `load_p = lpSum(x[p[0], p[1], j, z] * inst.T_load[p[0], j] for z in Z)` | Операции: умножение. Операнды: Z, inst, j, lpSum, p, x, z. | qsimmine12/app/sim_engine/planner.py:226 | Присваивает load_p результат выражения. | Z, inst, j, lpSum, p, x, z |
| 299 | `load_q = lpSum(x[q_[0], q_[1], j, z] * inst.T_load[q_[0], j] for z in Z)` | Операции: умножение. Операнды: Z, inst, j, lpSum, q_, x, z. | qsimmine12/app/sim_engine/planner.py:227 | Присваивает load_q результат выражения. | Z, inst, j, lpSum, q_, x, z |
| 300 | `model += s_load[q_] >= s_load[p] + load_p - Mbig * (1 - wvar) - Mbig * (2 - xpj - xqj)` | Операции: вычитание, сложение, умножение. Операнды: Mbig, load_p, p, q_, s_load, wvar, xpj, xqj. | qsimmine12/app/sim_engine/planner.py:232 | Обновляет model через сложение. | Mbig, load_p, p, q_, s_load, wvar, xpj, xqj |
| 301 | `model += s_load[p] >= s_load[q_] + load_q - Mbig * wvar - Mbig * (2 - xpj - xqj)` | Операции: вычитание, сложение, умножение. Операнды: Mbig, load_q, p, q_, s_load, wvar, xpj, xqj. | qsimmine12/app/sim_engine/planner.py:233 | Обновляет model через сложение. | Mbig, load_q, p, q_, s_load, wvar, xpj, xqj |
| 302 | `obj_tons = lpSum(inst.m_tons[i, j] * x[i, k, j, z] for (i, k) in P for j in J for z in Z)` | Операции: умножение. Операнды: J, P, Z, i, inst, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/planner.py:237 | Присваивает obj_tons результат выражения. | J, P, Z, i, inst, j, k, lpSum, x, z |
| 303 | `obj_trips = lpSum(x[i, k, j, z] for (i, k) in P for j in J for z in Z)` | Операции: функции и литералы. Операнды: J, P, Z, i, j, k, lpSum, x, z. | qsimmine12/app/sim_engine/planner.py:238 | Присваивает obj_trips результат выражения. | J, P, Z, i, j, k, lpSum, x, z |
| 304 | `chosen = [(j, z) for j in J for z in Z if x[i, k, j, z].value() and x[i, k, j, z].value() > 0.5]` | Операции: функции и литералы. Операнды: J, Z, i, j, k, x, z. | qsimmine12/app/sim_engine/planner.py:303 | Присваивает chosen результат выражения. | J, Z, i, j, k, x, z |
| 305 | `H = 2 * inst.D_work` | Операции: умножение. Операнды: inst. | qsimmine12/app/sim_engine/planner.py:331 | Присваивает H результат выражения. | inst |
| 306 | `Kmax_i = {i: compute_Kmax_i(inst, i) for i in I}` | Операции: функции и литералы. Операнды: I, compute_Kmax_i, i, inst. | qsimmine12/app/sim_engine/planner.py:337 | Присваивает Kmax_i результат выражения. | I, compute_Kmax_i, i, inst |
| 307 | `K = max(Kmax_i.values() or [0])` | Операции: функции и литералы. Операнды: Kmax_i, max. | qsimmine12/app/sim_engine/planner.py:339 | Присваивает K результат выражения. | Kmax_i, max |
| 308 | `Kmax_i = {i: K for i in I}` | Операции: функции и литералы. Операнды: I, K, i. | qsimmine12/app/sim_engine/planner.py:340 | Присваивает Kmax_i результат выражения. | I, K, i |
| 309 | `shovel_to_intervals = {j: [] for j in J}` | Операции: функции и литералы. Операнды: J, j. | qsimmine12/app/sim_engine/planner.py:352 | Присваивает shovel_to_intervals результат выражения. | J, j |
| 310 | `dump_to_intervals = {z: [] for z in Zs}` | Операции: функции и литералы. Операнды: Zs, z. | qsimmine12/app/sim_engine/planner.py:353 | Присваивает dump_to_intervals результат выражения. | Zs, z |
| 311 | `model.Add(sum(choose_shovel[i, k, j] for j in J) <= 1)` | Операции: функции и литералы. Операнды: J, choose_shovel, i, j, k, model, sum. | qsimmine12/app/sim_engine/planner.py:390 | Вычисляет выражение без сохранения результата. | J, choose_shovel, i, j, k, model, sum |
| 312 | `model.Add(sum(choose_dump[i, k, z] for z in Zs) <= 1)` | Операции: функции и литералы. Операнды: Zs, choose_dump, i, k, model, sum, z. | qsimmine12/app/sim_engine/planner.py:391 | Вычисляет выражение без сохранения результата. | Zs, choose_dump, i, k, model, sum, z |
| 313 | `model.Add(sum(choose_shovel[i, k, j] for j in J) <= sum(choose_shovel[i, k-1, j] for j in J))` | Операции: вычитание. Операнды: J, choose_shovel, i, j, k, model, sum. | qsimmine12/app/sim_engine/planner.py:397 | Вычисляет выражение без сохранения результата. | J, choose_shovel, i, j, k, model, sum |
| 314 | `terms.append(ton * choose_shovel[i, k, j])` | Операции: умножение. Операнды: choose_shovel, i, j, k, terms, ton. | qsimmine12/app/sim_engine/planner.py:443 | Вычисляет выражение без сохранения результата. | choose_shovel, i, j, k, terms, ton |
| 315 | `model.Maximize(sum(terms))` | Операции: функции и литералы. Операнды: model, sum, terms. | qsimmine12/app/sim_engine/planner.py:444 | Вычисляет выражение без сохранения результата. | model, sum, terms |
| 316 | `return sorted({i for (i, _) in self.T_load.keys()})` | Операции: функции и литералы. Операнды: i, self, sorted. | qsimmine12/app/sim_engine/planner.py:54 | Возвращает результат вычисления. | i, self, sorted |
| 317 | `D_work = 12 * 60` | Операции: умножение. Операнды: —. | qsimmine12/app/sim_engine/planner.py:555 | Присваивает D_work результат выражения. | — |
| 318 | `T_load[i, j] = 10 + 2 * (j - 1)` | Операции: вычитание, сложение, умножение. Операнды: T_load, i, j. | qsimmine12/app/sim_engine/planner.py:579 | Присваивает T_load[i, j] результат выражения. | T_load, i, j |
| 319 | `return sorted({j for (_, j) in self.T_load.keys()})` | Операции: функции и литералы. Операнды: j, self, sorted. | qsimmine12/app/sim_engine/planner.py:58 | Возвращает результат вычисления. | j, self, sorted |
| 320 | `T_start[i, j] = 15 + 3 * (i - 1)` | Операции: вычитание, сложение, умножение. Операнды: T_start, i, j. | qsimmine12/app/sim_engine/planner.py:580 | Присваивает T_start[i, j] результат выражения. | T_start, i, j |
| 321 | `T_unload[i, z] = 8 + (z - 1)` | Операции: вычитание, сложение. Операнды: T_unload, i, z. | qsimmine12/app/sim_engine/planner.py:583 | Присваивает T_unload[i, z] результат выражения. | T_unload, i, z |
| 322 | `T_end[i, z] = 20 + 5 * (z - 1)` | Операции: вычитание, сложение, умножение. Операнды: T_end, i, z. | qsimmine12/app/sim_engine/planner.py:584 | Присваивает T_end[i, z] результат выражения. | T_end, i, z |
| 323 | `T_haul[i, j, z] = 25 + 5 * (z - 1) + 3 * (i - 1)` | Операции: вычитание, сложение, умножение. Операнды: T_haul, i, j, z. | qsimmine12/app/sim_engine/planner.py:587 | Присваивает T_haul[i, j, z] результат выражения. | T_haul, i, j, z |
| 324 | `T_return[i, z, j] = 22 + 4 * (j - 1) + 2 * (i - 1)` | Операции: вычитание, сложение, умножение. Операнды: T_return, i, j, z. | qsimmine12/app/sim_engine/planner.py:588 | Присваивает T_return[i, z, j] результат выражения. | T_return, i, j, z |
| 325 | `return sorted({z for (_, z) in self.T_unload.keys()})` | Операции: функции и литералы. Операнды: self, sorted, z. | qsimmine12/app/sim_engine/planner.py:62 | Возвращает результат вычисления. | self, sorted, z |
| 326 | `planning_data.T_load[truck.id, shovel.id] = int(time_load/60)` | Операции: деление. Операнды: int, planning_data, shovel, time_load, truck. | qsimmine12/app/sim_engine/planner.py:635 | Присваивает planning_data.T_load[truck.id, shovel.id] результат выражения. | int, planning_data, shovel, time_load, truck |
| 327 | `planning_data.T_start[truck.id, shovel.id] = int(TruckCalc.calculate_time_motion_by_edges(
                start_route,
                truck.properties,
                forward=True
            )/60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, shovel, start_route, truck. | qsimmine12/app/sim_engine/planner.py:660 | Присваивает planning_data.T_start[truck.id, shovel.id] результат выражения. | TruckCalc, int, planning_data, shovel, start_route, truck |
| 328 | `js = {j for (ti, j) in inst.T_start.keys() if ti == i}` | Операции: функции и литералы. Операнды: i, inst, j, ti. | qsimmine12/app/sim_engine/planner.py:67 | Присваивает js результат выражения. | i, inst, j, ti |
| 329 | `zs = {z for (ti, z) in inst.T_end.keys() if ti == i}` | Операции: функции и литералы. Операнды: i, inst, ti, z. | qsimmine12/app/sim_engine/planner.py:68 | Присваивает zs результат выражения. | i, inst, ti, z |
| 330 | `planning_data.T_haul[truck.id, shovel.id, unload.id] = int(TruckCalc.calculate_time_motion_by_edges(
                    route,
                    truck.properties,
                    forward=True
                )/60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, route, shovel, truck, unload. | qsimmine12/app/sim_engine/planner.py:684 | Присваивает planning_data.T_haul[truck.id, shovel.id, unload.id] результат выражения. | TruckCalc, int, planning_data, route, shovel, truck, unload |
| 331 | `min_start = min(inst.T_start[i, j] for j in js)` | Операции: функции и литералы. Операнды: i, inst, j, js, min. | qsimmine12/app/sim_engine/planner.py:69 | Присваивает min_start результат выражения. | i, inst, j, js, min |
| 332 | `planning_data.T_return[truck.id, unload.id, shovel.id] = int(TruckCalc.calculate_time_motion_by_edges(
                    route,
                    truck.properties,
                    forward=False
                )/60)` | Операции: деление. Операнды: TruckCalc, int, planning_data, route, shovel, truck, unload. | qsimmine12/app/sim_engine/planner.py:694 | Присваивает planning_data.T_return[truck.id, unload.id, shovel.id] результат выражения. | TruckCalc, int, planning_data, route, shovel, truck, unload |
| 333 | `min_end = min(inst.T_end[i, z] for z in zs)` | Операции: функции и литералы. Операнды: i, inst, min, z, zs. | qsimmine12/app/sim_engine/planner.py:70 | Присваивает min_end результат выражения. | i, inst, min, z, zs |
| 334 | `planning_data.T_unload[truck.id, unload.id] = int(UnloadCalc.unload_calculation_by_norm(unload.properties, truck.properties)["t_total"]/60)` | Операции: деление. Операнды: UnloadCalc, int, planning_data, truck, unload. | qsimmine12/app/sim_engine/planner.py:707 | Присваивает planning_data.T_unload[truck.id, unload.id] результат выражения. | UnloadCalc, int, planning_data, truck, unload |
| 335 | `min_d = min(
        inst.T_haul[i, j, z] + inst.T_return[i, z, j] + inst.T_load[i, j] + inst.T_unload[i, z]
        for j in js for z in zs
    )` | Операции: сложение. Операнды: i, inst, j, js, min, z, zs. | qsimmine12/app/sim_engine/planner.py:71 | Присваивает min_d результат выражения. | i, inst, j, js, min, z, zs |
| 336 | `planning_data.T_end[truck.id, unload.id] = int(TruckCalc.calculate_time_motion_by_edges(
                end_route,
                truck.properties,
                forward=True
            )/60)` | Операции: деление. Операнды: TruckCalc, end_route, int, planning_data, truck, unload. | qsimmine12/app/sim_engine/planner.py:720 | Присваивает planning_data.T_end[truck.id, unload.id] результат выражения. | TruckCalc, end_route, int, planning_data, truck, unload |
| 337 | `available = inst.D_work - min_start - min_end` | Операции: вычитание. Операнды: inst, min_end, min_start. | qsimmine12/app/sim_engine/planner.py:75 | Присваивает available результат выражения. | inst, min_end, min_start |
| 338 | `return max(0, floor(available / max(1, min_d)))` | Операции: деление. Операнды: available, floor, max, min_d. | qsimmine12/app/sim_engine/planner.py:76 | Возвращает результат вычисления. | available, floor, max, min_d |
| 339 | `return {i: compute_Kmax_i(inst, i) for i in inst.truck_ids}` | Операции: функции и литералы. Операнды: compute_Kmax_i, i, inst. | qsimmine12/app/sim_engine/planner.py:81 | Возвращает результат вычисления. | compute_Kmax_i, i, inst |
| 340 | `P = [(i, k) for i in I for k in range(1, Kmax[i] + 1)]` | Операции: сложение. Операнды: I, Kmax, List, Tuple, i, int, k, range. | qsimmine12/app/sim_engine/planner.py:94 | Присваивает P результат выражения с аннотацией. | I, Kmax, List, Tuple, i, int, k, range |
| 341 | `tval = float(stats.t.ppf(1 - alpha / 2, df=n - 1))` | Операции: вычитание, деление. Операнды: alpha, float, n, stats. | qsimmine12/app/sim_engine/reliability.py:103 | Присваивает tval результат выражения. | alpha, float, n, stats |
| 342 | `half = tval * s * np.sqrt(1 + 1 / n)` | Операции: деление, сложение, умножение. Операнды: n, np, s, tval. | qsimmine12/app/sim_engine/reliability.py:104 | Присваивает half результат выражения. | n, np, s, tval |
| 343 | `n_cal = n // 2` | Операции: целочисленное деление. Операнды: n. | qsimmine12/app/sim_engine/reliability.py:140 | Присваивает n_cal результат выражения. | n |
| 344 | `mu = float(np.mean(train))` | Операции: функции и литералы. Операнды: float, np, train. | qsimmine12/app/sim_engine/reliability.py:142 | Присваивает mu результат выражения. | float, np, train |
| 345 | `scores = np.abs(cal - mu)` | Операции: вычитание. Операнды: cal, mu, np. | qsimmine12/app/sim_engine/reliability.py:143 | Присваивает scores результат выражения. | cal, mu, np |
| 346 | `k = int(np.ceil((1 - alpha) * (n_cal + 1)))` | Операции: вычитание, сложение, умножение. Операнды: alpha, int, n_cal, np. | qsimmine12/app/sim_engine/reliability.py:145 | Присваивает k результат выражения. | alpha, int, n_cal, np |
| 347 | `lx = np.log(x)` | Операции: функции и литералы. Операнды: np, x. | qsimmine12/app/sim_engine/reliability.py:157 | Присваивает lx результат выражения. | np, x |
| 348 | `m = float(np.mean(lx))` | Операции: функции и литералы. Операнды: float, lx, np. | qsimmine12/app/sim_engine/reliability.py:158 | Присваивает m результат выражения. | float, lx, np |
| 349 | `tval = float(stats.t.ppf(1 - alpha / 2, df=len(x) - 1))` | Операции: вычитание, деление. Операнды: alpha, float, len, stats, x. | qsimmine12/app/sim_engine/reliability.py:160 | Присваивает tval результат выражения. | alpha, float, len, stats, x |
| 350 | `half = tval * s * np.sqrt(1 + 1 / len(x))` | Операции: деление, сложение, умножение. Операнды: len, np, s, tval, x. | qsimmine12/app/sim_engine/reliability.py:161 | Присваивает half результат выражения. | len, np, s, tval, x |
| 351 | `g = np.linspace(np.min(x), np.max(x), grids)` | Операции: функции и литералы. Операнды: grids, np, x. | qsimmine12/app/sim_engine/reliability.py:176 | Присваивает g результат выражения. | grids, np, x |
| 352 | `cs = np.cumsum(f[idx])` | Операции: функции и литералы. Операнды: f, idx, np. | qsimmine12/app/sim_engine/reliability.py:179 | Присваивает cs результат выражения. | f, idx, np |
| 353 | `mask = cs <= (1 - alpha)` | Операции: вычитание. Операнды: alpha, cs. | qsimmine12/app/sim_engine/reliability.py:181 | Присваивает mask результат выражения. | alpha, cs |
| 354 | `mu_full = float(np.mean(x))` | Операции: функции и литералы. Операнды: float, np, x. | qsimmine12/app/sim_engine/reliability.py:205 | Присваивает mu_full результат выражения. | float, np, x |
| 355 | `mu_loo = np.array([(np.sum(x) - xi) / (n - 1) for xi in x])` | Операции: вычитание, деление. Операнды: n, np, x, xi. | qsimmine12/app/sim_engine/reliability.py:206 | Присваивает mu_loo результат выражения. | n, np, x, xi |
| 356 | `resid = np.abs(x - mu_loo)` | Операции: вычитание. Операнды: mu_loo, np, x. | qsimmine12/app/sim_engine/reliability.py:207 | Присваивает resid результат выражения. | mu_loo, np, x |
| 357 | `q = np.quantile(resid, 1 - alpha, method="higher")` | Операции: вычитание. Операнды: alpha, np, resid. | qsimmine12/app/sim_engine/reliability.py:208 | Присваивает q результат выражения. | alpha, np, resid |
| 358 | `n_cal = n // 2` | Операции: целочисленное деление. Операнды: n. | qsimmine12/app/sim_engine/reliability.py:223 | Присваивает n_cal результат выражения. | n |
| 359 | `mu = float(np.mean(tr))` | Операции: функции и литералы. Операнды: float, np, tr. | qsimmine12/app/sim_engine/reliability.py:225 | Присваивает mu результат выражения. | float, np, tr |
| 360 | `e = cal - mu` | Операции: вычитание. Операнды: cal, mu. | qsimmine12/app/sim_engine/reliability.py:226 | Присваивает e результат выражения. | cal, mu |
| 361 | `q_lo = np.quantile(e, alpha / 2, method="lower")` | Операции: деление. Операнды: alpha, e, np. | qsimmine12/app/sim_engine/reliability.py:227 | Присваивает q_lo результат выражения. | alpha, e, np |
| 362 | `q_hi = np.quantile(e, 1 - alpha / 2, method="higher")` | Операции: вычитание, деление. Операнды: alpha, e, np. | qsimmine12/app/sim_engine/reliability.py:228 | Присваивает q_hi результат выражения. | alpha, e, np |
| 363 | `lam = stats.yeojohnson_normmax(x)` | Операции: функции и литералы. Операнды: stats, x. | qsimmine12/app/sim_engine/reliability.py:239 | Присваивает lam результат выражения. | stats, x |
| 364 | `tval = float(stats.t.ppf(1 - alpha / 2, df=n - 1))` | Операции: вычитание, деление. Операнды: alpha, float, n, stats. | qsimmine12/app/sim_engine/reliability.py:243 | Присваивает tval результат выражения. | alpha, float, n, stats |
| 365 | `half = tval * s * np.sqrt(1 + 1 / n)` | Операции: деление, сложение, умножение. Операнды: n, np, s, tval. | qsimmine12/app/sim_engine/reliability.py:244 | Присваивает half результат выражения. | n, np, s, tval |
| 366 | `pos = yv >= 0` | Операции: функции и литералы. Операнды: yv. | qsimmine12/app/sim_engine/reliability.py:254 | Присваивает pos результат выражения. | yv |
| 367 | `l2 = 2.0 - lmbda` | Операции: вычитание. Операнды: lmbda. | qsimmine12/app/sim_engine/reliability.py:255 | Присваивает l2 результат выражения. | lmbda |
| 368 | `base_pos = yv[pos] * lmbda + 1.0` | Операции: сложение, умножение. Операнды: lmbda, pos, yv. | qsimmine12/app/sim_engine/reliability.py:262 | Присваивает base_pos результат выражения. | lmbda, pos, yv |
| 369 | `out[pos] = np.power(base_pos, 1.0 / lmbda) - 1.0` | Операции: вычитание, деление. Операнды: base_pos, lmbda, np, out, pos. | qsimmine12/app/sim_engine/reliability.py:264 | Присваивает out[pos] результат выражения. | base_pos, lmbda, np, out, pos |
| 370 | `neg = ~pos` | Операции: битовое НЕ. Операнды: pos. | qsimmine12/app/sim_engine/reliability.py:269 | Присваивает neg результат выражения. | pos |
| 371 | `base_neg = 1.0 - yv[neg] * l2` | Операции: вычитание, умножение. Операнды: l2, neg, yv. | qsimmine12/app/sim_engine/reliability.py:272 | Присваивает base_neg результат выражения. | l2, neg, yv |
| 372 | `out[neg] = 1.0 - np.power(base_neg, 1.0 / l2)` | Операции: вычитание, деление. Операнды: base_neg, l2, neg, np, out. | qsimmine12/app/sim_engine/reliability.py:274 | Присваивает out[neg] результат выражения. | base_neg, l2, neg, np, out |
| 373 | `out[neg] = 1.0 - np.exp(-yv[neg])` | Операции: вычитание, унарное -. Операнды: neg, np, out, yv. | qsimmine12/app/sim_engine/reliability.py:276 | Присваивает out[neg] результат выражения. | neg, np, out, yv |
| 374 | `lo = float(np.min(inv_yj(np.array([lo_y, hi_y]), lam)))` | Операции: функции и литералы. Операнды: float, hi_y, inv_yj, lam, lo_y, np. | qsimmine12/app/sim_engine/reliability.py:281 | Присваивает lo результат выражения. | float, hi_y, inv_yj, lam, lo_y, np |
| 375 | `hi = float(np.max(inv_yj(np.array([lo_y, hi_y]), lam)))` | Операции: функции и литералы. Операнды: float, hi_y, inv_yj, lam, lo_y, np. | qsimmine12/app/sim_engine/reliability.py:282 | Присваивает hi результат выражения. | float, hi_y, inv_yj, lam, lo_y, np |
| 376 | `return float(np.mean(y))` | Операции: функции и литералы. Операнды: float, np, y. | qsimmine12/app/sim_engine/reliability.py:292 | Возвращает результат вычисления. | float, np, y |
| 377 | `k = n // 2` | Операции: целочисленное деление. Операнды: n. | qsimmine12/app/sim_engine/reliability.py:293 | Присваивает k результат выражения. | n |
| 378 | `widths = y[k:] - y[:n - k]` | Операции: вычитание. Операнды: k, n, y. | qsimmine12/app/sim_engine/reliability.py:294 | Присваивает widths результат выражения. | k, n, y |
| 379 | `j = int(np.argmin(widths))` | Операции: функции и литералы. Операнды: int, np, widths. | qsimmine12/app/sim_engine/reliability.py:295 | Присваивает j результат выражения. | int, np, widths |
| 380 | `grid = np.linspace(np.min(x), np.max(x), grids)` | Операции: функции и литералы. Операнды: grids, np, x. | qsimmine12/app/sim_engine/reliability.py:303 | Присваивает grid результат выражения. | grids, np, x |
| 381 | `inside += int(lo <= x[i] <= hi)` | Операции: функции и литералы. Операнды: hi, i, int, lo, x. | qsimmine12/app/sim_engine/reliability.py:325 | Обновляет inside через сложение. | hi, i, int, lo, x |
| 382 | `return inside / n` | Операции: деление. Операнды: inside, n. | qsimmine12/app/sim_engine/reliability.py:326 | Возвращает результат вычисления. | inside, n |
| 383 | `m = float(np.mean(x))` | Операции: функции и литералы. Операнды: float, np, x. | qsimmine12/app/sim_engine/reliability.py:334 | Присваивает m результат выражения. | float, np, x |
| 384 | `s = float(np.std(x, ddof=1)) if n > 1 else 1.0` | Операции: функции и литералы. Операнды: float, n, np, x. | qsimmine12/app/sim_engine/reliability.py:335 | Присваивает s результат выражения. | float, n, np, x |
| 385 | `scale = s * np.sqrt(1 + 1 / n) if n > 0 else 1.0` | Операции: деление, сложение, умножение. Операнды: n, np, s. | qsimmine12/app/sim_engine/reliability.py:336 | Присваивает scale результат выражения. | n, np, s |
| 386 | `z = (x - m) / (scale if scale > 0 else 1.0)` | Операции: вычитание, деление. Операнды: m, scale, x. | qsimmine12/app/sim_engine/reliability.py:337 | Присваивает z результат выражения. | m, scale, x |
| 387 | `return float(hi - lo) if (np.isfinite(hi) and np.isfinite(lo)) else np.inf` | Операции: вычитание. Операнды: float, hi, lo, np. | qsimmine12/app/sim_engine/reliability.py:351 | Возвращает результат вычисления. | float, hi, lo, np |
| 388 | `target = 1 - alpha` | Операции: вычитание. Операнды: alpha. | qsimmine12/app/sim_engine/reliability.py:371 | Присваивает target результат выражения. | alpha |
| 389 | `ok = 1 if cov >= target - tol else 0` | Операции: вычитание. Операнды: cov, target, tol. | qsimmine12/app/sim_engine/reliability.py:386 | Присваивает ok результат выражения. | cov, target, tol |
| 390 | `shortfall = max(0.0, target - cov)` | Операции: вычитание. Операнды: cov, max, target. | qsimmine12/app/sim_engine/reliability.py:387 | Присваивает shortfall результат выражения. | cov, max, target |
| 391 | `robust_bonus = 1 if (abs(skew) > 1.0 and name in robust_names) else 0` | Операции: функции и литералы. Операнды: abs, name, robust_names, skew. | qsimmine12/app/sim_engine/reliability.py:388 | Присваивает robust_bonus результат выражения. | abs, name, robust_names, skew |
| 392 | `half = 0.5 * (hi - lo)` | Операции: вычитание, умножение. Операнды: hi, lo. | qsimmine12/app/sim_engine/reliability.py:449 | Присваивает half результат выражения. | hi, lo |
| 393 | `metric_median = float(np.median(sub))` | Операции: функции и литералы. Операнды: float, np, sub. | qsimmine12/app/sim_engine/reliability.py:450 | Присваивает metric_median результат выражения. | float, np, sub |
| 394 | `rel_half = half / max(abs(metric_median), eps)` | Операции: деление. Операнды: abs, eps, half, max, metric_median. | qsimmine12/app/sim_engine/reliability.py:451 | Присваивает rel_half результат выражения. | abs, eps, half, max, metric_median |
| 395 | `rel_delta = np.inf
        if prev_metric_median is None
        else abs(metric_median - prev_metric_median) / max(abs(metric_median), eps)` | Операции: вычитание, деление. Операнды: abs, eps, max, metric_median, np, prev_metric_median. | qsimmine12/app/sim_engine/reliability.py:452 | Присваивает rel_delta результат выражения. | abs, eps, max, metric_median, np, prev_metric_median |
| 396 | `stable_streak = (cur_stable_streak + 1) if ok else 0` | Операции: сложение. Операнды: cur_stable_streak, ok. | qsimmine12/app/sim_engine/reliability.py:459 | Присваивает stable_streak результат выражения. | cur_stable_streak, ok |
| 397 | `stability_achieved = stable_streak >= consecutive` | Операции: функции и литералы. Операнды: consecutive, stable_streak. | qsimmine12/app/sim_engine/reliability.py:460 | Присваивает stability_achieved результат выражения. | consecutive, stable_streak |
| 398 | `rd_txt = "-" if prev_metric_median is None else f"{rel_delta:.4f}"` | Операции: функции и литералы. Операнды: prev_metric_median, rel_delta. | qsimmine12/app/sim_engine/reliability.py:463 | Присваивает rd_txt результат выражения. | prev_metric_median, rel_delta |
| 399 | `(sh_stat, sh_p) = stats.shapiro(metric_array) if len(metric_array) <= 5000 else (np.nan, np.nan)` | Операции: функции и литералы. Операнды: len, metric_array, np, stats. | qsimmine12/app/sim_engine/reliability.py:489 | Присваивает (sh_stat, sh_p) результат выражения. | len, metric_array, np, stats |
| 400 | `cov_txt = f"  LOO cover={cov:.3f}" if not np.isnan(cov) else ""` | Операции: логическое не. Операнды: cov, np. | qsimmine12/app/sim_engine/reliability.py:534 | Присваивает cov_txt результат выражения. | cov, np |
| 401 | `pit_cov = float(np.mean((u >= alpha/2) & (u <= 1 - alpha/2)))` | Операции: вычитание, деление, побитовое И. Операнды: alpha, float, np, u. | qsimmine12/app/sim_engine/reliability.py:540 | Присваивает pit_cov результат выражения. | alpha, float, np, u |
| 402 | `median = float(np.median(metric_array))` | Операции: функции и литералы. Операнды: float, metric_array, np. | qsimmine12/app/sim_engine/reliability.py:554 | Присваивает median результат выражения. | float, metric_array, np |
| 403 | `weight_diff = abs(metric_value - metric_reliable)` | Операции: вычитание. Операнды: abs, metric_reliable, metric_value. | qsimmine12/app/sim_engine/reliability.py:576 | Присваивает weight_diff результат выражения. | abs, metric_reliable, metric_value |
| 404 | `m = float(np.mean(x)) if n else np.nan` | Операции: функции и литералы. Операнды: float, n, np, x. | qsimmine12/app/sim_engine/reliability.py:67 | Присваивает m результат выражения. | float, n, np, x |
| 405 | `s = float(np.std(x, ddof=1)) if n > 1 else np.nan` | Операции: функции и литералы. Операнды: float, n, np, x. | qsimmine12/app/sim_engine/reliability.py:68 | Присваивает s результат выражения. | float, n, np, x |
| 406 | `med = float(np.median(x)) if n else np.nan` | Операции: функции и литералы. Операнды: float, n, np, x. | qsimmine12/app/sim_engine/reliability.py:69 | Присваивает med результат выражения. | float, n, np, x |
| 407 | `(q1, q3) = (np.quantile(x, 0.25), np.quantile(x, 0.75)) if n > 0 else (np.nan, np.nan)` | Операции: функции и литералы. Операнды: n, np, x. | qsimmine12/app/sim_engine/reliability.py:70 | Присваивает (q1, q3) результат выражения. | n, np, x |
| 408 | `iqr = float(q3 - q1) if n > 0 else np.nan` | Операции: вычитание. Операнды: float, n, np, q1, q3. | qsimmine12/app/sim_engine/reliability.py:71 | Присваивает iqr результат выражения. | float, n, np, q1, q3 |
| 409 | `sk = stats.skew(x, bias=False) if n > 2 else np.nan` | Операции: функции и литералы. Операнды: n, np, stats, x. | qsimmine12/app/sim_engine/reliability.py:72 | Присваивает sk результат выражения. | n, np, stats, x |
| 410 | `kurt = stats.kurtosis(x, fisher=True, bias=False) if n > 3 else np.nan` | Операции: функции и литералы. Операнды: n, np, stats, x. | qsimmine12/app/sim_engine/reliability.py:73 | Присваивает kurt результат выражения. | n, np, stats, x |
| 411 | `m = float(np.mean(x))` | Операции: функции и литералы. Операнды: float, np, x. | qsimmine12/app/sim_engine/reliability.py:98 | Присваивает m результат выражения. | float, np, x |
| 412 | `start_time = item["start_time"].isoformat() if isinstance(item["start_time"], datetime) else item["start_time"]` | Операции: функции и литералы. Операнды: datetime, isinstance, item. | qsimmine12/app/sim_engine/serializer.py:128 | Присваивает start_time результат выражения. | datetime, isinstance, item |
| 413 | `end_time = item["end_time"].isoformat() if isinstance(item["end_time"], datetime) else item["end_time"]` | Операции: функции и литералы. Операнды: datetime, isinstance, item. | qsimmine12/app/sim_engine/serializer.py:129 | Присваивает end_time результат выражения. | datetime, isinstance, item |
| 414 | `segments = [
                Segment(
                    start=Point(lat=s["start"][0], lon=s["start"][1]),
                    end=Point(lat=s["end"][0], lon=s["end"][1]),
                )
                for s in raw["segments"]
            ]` | Операции: функции и литералы. Операнды: Point, Segment, raw, s. | qsimmine12/app/sim_engine/serializer.py:286 | Присваивает segments результат выражения. | Point, Segment, raw, s |
| 415 | `shift_start = current_day + timedelta(minutes=shift["begin_offset"])` | Операции: сложение. Операнды: current_day, shift, timedelta. | qsimmine12/app/sim_engine/serializer.py:38 | Присваивает shift_start результат выражения. | current_day, shift, timedelta |
| 416 | `lunch_start = shift_start + timedelta(minutes=lunch_break_offset)` | Операции: сложение. Операнды: lunch_break_offset, shift_start, timedelta. | qsimmine12/app/sim_engine/serializer.py:41 | Присваивает lunch_start результат выражения. | lunch_break_offset, shift_start, timedelta |
| 417 | `lunch_end = lunch_start + timedelta(minutes=lunch_break_duration)` | Операции: сложение. Операнды: lunch_break_duration, lunch_start, timedelta. | qsimmine12/app/sim_engine/serializer.py:42 | Присваивает lunch_end результат выражения. | lunch_break_duration, lunch_start, timedelta |
| 418 | `actual_lunch_start = max(lunch_start, start_time)` | Операции: функции и литералы. Операнды: lunch_start, max, start_time. | qsimmine12/app/sim_engine/serializer.py:47 | Присваивает actual_lunch_start результат выражения. | lunch_start, max, start_time |
| 419 | `actual_lunch_end = min(lunch_end, end_time)` | Операции: функции и литералы. Операнды: end_time, lunch_end, min. | qsimmine12/app/sim_engine/serializer.py:48 | Присваивает actual_lunch_end результат выражения. | end_time, lunch_end, min |
| 420 | `start_time = idle["start_time"].isoformat() if isinstance(idle["start_time"], datetime) else idle["start_time"]` | Операции: функции и литералы. Операнды: datetime, idle, isinstance. | qsimmine12/app/sim_engine/serializer.py:86 | Присваивает start_time результат выражения. | datetime, idle, isinstance |
| 421 | `end_time = idle["end_time"].isoformat() if isinstance(idle["end_time"], datetime) else idle["end_time"]` | Операции: функции и литералы. Операнды: datetime, idle, isinstance. | qsimmine12/app/sim_engine/serializer.py:87 | Присваивает end_time результат выражения. | datetime, idle, isinstance |
| 422 | `self.processes = int(multiprocessing.cpu_count() / 2)` | Операции: деление. Операнды: int, multiprocessing, self. | qsimmine12/app/sim_engine/simulate.py:295 | Присваивает self.processes результат выражения. | int, multiprocessing, self |
| 423 | `starmap_args_list = [self._make_closure_args() for _ in range(next_runs_number)]` | Операции: функции и литералы. Операнды: next_runs_number, range, self. | qsimmine12/app/sim_engine/simulate.py:329 | Присваивает starmap_args_list результат выражения. | next_runs_number, range, self |
| 424 | `final_result['summary']['confidence_interval'] = (1 - self.alpha) * 100` | Операции: вычитание, умножение. Операнды: final_result, self. | qsimmine12/app/sim_engine/simulate.py:374 | Присваивает final_result['summary']['confidence_interval'] результат выражения. | final_result, self |
| 425 | `return writer() if is_class else writer` | Операции: функции и литералы. Операнды: is_class, writer. | qsimmine12/app/sim_engine/simulation_manager.py:162 | Возвращает результат вычисления. | is_class, writer |
| 426 | `return validator() if is_class else validator` | Операции: функции и литералы. Операнды: is_class, validator. | qsimmine12/app/sim_engine/simulation_manager.py:176 | Возвращает результат вычисления. | is_class, validator |
| 427 | `mode = "auto" if scenario and scenario["is_auto_truck_distribution"] else "manual"` | Операции: функции и литералы. Операнды: scenario. | qsimmine12/app/sim_engine/tests/run_simulate.py:23 | Присваивает mode результат выражения. | scenario |
| 428 | `hourly_volume = " \| ".join([f"{i["time"]}: {i["value"]}" for i in summary["chart_volume_data"]])` | Операции: функции и литералы. Операнды: i, summary. | qsimmine12/app/sim_engine/tests/run_simulate.py:38 | Присваивает hourly_volume результат выражения. | i, summary |
| 429 | `hourly_trip = " \| ".join([f"{i["time"]}: {i["value"]}" for i in summary["chart_trip_data"]])` | Операции: функции и литералы. Операнды: i, summary. | qsimmine12/app/sim_engine/tests/run_simulate.py:39 | Присваивает hourly_trip результат выражения. | i, summary |
| 430 | `truck_telemetry = [
        i for i in result["telemetry"] if i["object_type"] == ObjectType.TRUCK.key() and i["object_id"] == "1_truck"
    ]` | Операции: функции и литералы. Операнды: ObjectType, i, result. | qsimmine12/app/sim_engine/tests/run_simulate.py:47 | Присваивает truck_telemetry результат выражения. | ObjectType, i, result |
| 431 | `shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.SHOVEL.key()]` | Операции: функции и литералы. Операнды: ObjectType, i, result. | qsimmine12/app/sim_engine/tests/test_simulate.py:109 | Присваивает shovel_telemetry результат выражения. | ObjectType, i, result |
| 432 | `shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.TRUCK.key()]` | Операции: функции и литералы. Операнды: ObjectType, i, result. | qsimmine12/app/sim_engine/tests/test_simulate.py:134 | Присваивает shovel_telemetry результат выражения. | ObjectType, i, result |
| 433 | `shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.UNLOAD.key()]` | Операции: функции и литералы. Операнды: ObjectType, i, result. | qsimmine12/app/sim_engine/tests/test_simulate.py:155 | Присваивает shovel_telemetry результат выражения. | ObjectType, i, result |
| 434 | `shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.FUEL_STATION.key()]` | Операции: функции и литералы. Операнды: ObjectType, i, result. | qsimmine12/app/sim_engine/tests/test_simulate.py:177 | Присваивает shovel_telemetry результат выражения. | ObjectType, i, result |
| 435 | `shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.SHOVEL.key()]` | Операции: функции и литералы. Операнды: ObjectType, i, result. | qsimmine12/app/sim_engine/tests/test_simulate.py:84 | Присваивает shovel_telemetry результат выражения. | ObjectType, i, result |
| 436 | `time_slot = int(timestamp // self.batch_size_seconds)` | Операции: целочисленное деление. Операнды: int, self, timestamp. | qsimmine12/app/sim_engine/writer.py:85 | Присваивает time_slot результат выражения. | int, self, timestamp |
| 437 | `start_time = datetime.now() - timedelta(hours=1)` | Операции: вычитание. Операнды: datetime, timedelta. | qsimmine12/app/simulate_test.py:10 | Присваивает start_time результат выражения. | datetime, timedelta |
| 438 | `frame_time = start_time + timedelta(minutes=frame_id)` | Операции: сложение. Операнды: frame_id, start_time, timedelta. | qsimmine12/app/simulate_test.py:18 | Присваивает frame_time результат выражения. | frame_id, start_time, timedelta |
| 439 | `progress = min(1, frame_id / (total_frames * 0.8))` | Операции: деление, умножение. Операнды: frame_id, min, total_frames. | qsimmine12/app/simulate_test.py:60 | Присваивает progress результат выражения. | frame_id, min, total_frames |
| 440 | `lat = shovel_pos[0] + (unloading_site1[0] - shovel_pos[0]) * progress` | Операции: вычитание, сложение, умножение. Операнды: progress, shovel_pos, unloading_site1. | qsimmine12/app/simulate_test.py:61 | Присваивает lat результат выражения. | progress, shovel_pos, unloading_site1 |
| 441 | `lng = shovel_pos[1] + (unloading_site1[1] - shovel_pos[1]) * progress` | Операции: вычитание, сложение, умножение. Операнды: progress, shovel_pos, unloading_site1. | qsimmine12/app/simulate_test.py:62 | Присваивает lng результат выражения. | progress, shovel_pos, unloading_site1 |
| 442 | `progress = min(1, frame_id / (total_frames * 0.7))` | Операции: деление, умножение. Операнды: frame_id, min, total_frames. | qsimmine12/app/simulate_test.py:77 | Присваивает progress результат выражения. | frame_id, min, total_frames |
| 443 | `lat = shovel_pos[0] + (unloading_site2[0] - shovel_pos[0]) * progress` | Операции: вычитание, сложение, умножение. Операнды: progress, shovel_pos, unloading_site2. | qsimmine12/app/simulate_test.py:78 | Присваивает lat результат выражения. | progress, shovel_pos, unloading_site2 |
| 444 | `lng = shovel_pos[1] + (unloading_site2[1] - shovel_pos[1]) * progress` | Операции: вычитание, сложение, умножение. Операнды: progress, shovel_pos, unloading_site2. | qsimmine12/app/simulate_test.py:79 | Присваивает lng результат выражения. | progress, shovel_pos, unloading_site2 |
| 445 | `by_hours = {str(h): random.randint(100, 500) for h in range(1, 13)}` | Операции: функции и литералы. Операнды: h, random, range, str. | qsimmine12/app/simulate_test.py:94 | Присваивает by_hours результат выражения. | h, random, range, str |
| 446 | `index_file = static_dir / "index.html"` | Операции: деление. Операнды: static_dir. | qsimmine12/app/tests/conftest.py:32 | Присваивает index_file результат выражения. | static_dir |

---

**Всего формул:** 446
*Отчёт сформирован автоматически скриптом `S.math_finding.py`.*
