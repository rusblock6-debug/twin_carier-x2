import inspect
import logging
import multiprocessing
import traceback
from collections import defaultdict
from multiprocessing import Manager
from multiprocessing.managers import DictProxy  # noqa
from typing import Any

from app.sim_engine.config import SIM_CONFIG
from app.sim_engine.core.planner.manage import Planner
from app.sim_engine.core.props import SimData, PlannedTrip
from app.sim_engine.infra.exception_traceback import catch_errors
from app.sim_engine.serializer import SimDataSerializer
from app.sim_engine.simulate import run_reliability, run_simulation, run_simulation_for_planned_trips
from app.sim_engine.writer import IWriter, DictSimpleWriter

logger = logging.getLogger(__name__)


class ManagerValidationError(Exception):
    """Любые ошибки валидации для менеджера"""
    pass


class SimDataValidationError(ManagerValidationError):
    """Ошибка валидации входных данных симуляции"""
    pass


class SimConfigValidationError(ManagerValidationError):
    """Ошибка валидации конфигурации симуляции"""
    pass


class SimWriterValidationError(ManagerValidationError):
    """Ошибка валидации писаря результатов симуляции"""
    pass


class ValidatorValidationError(ManagerValidationError):
    """Ошибка валидации валидатора, используемого в менеджере"""
    pass


class IManagerValidator:
    @staticmethod
    def validate(data: Any) -> Any:
        raise NotImplementedError


class RawSimDataValidator(IManagerValidator):
    @staticmethod
    def validate(data: dict) -> dict:
        if not data:
            if isinstance(data, dict):
                raise SimDataValidationError('Input data is empty!')
            raise SimDataValidationError(f'Input data is invalid! Your data is {data}.')
        return data


class SimConfigOptionsValidator(IManagerValidator):
    @staticmethod
    def validate(data: dict) -> dict:
        if not isinstance(data, dict):
            raise SimConfigValidationError(f'Input config is invalid! Your config is {data}.')
        return data


class SimulationManager:
    """Менеджер для управления запуском симуляции в ручном/автоматическом режиме"""

    def __init__(
            self,
            raw_data: dict,
            options: dict | None = None,
            writer: type[IWriter] = DictSimpleWriter,
            raw_data_validator: type[IManagerValidator] = RawSimDataValidator,
            options_validator: type[IManagerValidator] = SimConfigOptionsValidator,
            use_multiprocessing: bool = False,
    ) -> None:
        """
            Инициализация менеджера.

            Аргументы:
            raw_data - сырые данные, необходимые для проведения симуляции/планирования
            options - опции конфигурации для применения в процессе симуляции/планирования
            writer - писарь результатов симуляции
            raw_data_validator - валидатор сырых данных raw_data
            options_validator - валидатор опций конфигурации
        """
        self.raw_data_validator: IManagerValidator = self.validate_validator(validator=raw_data_validator)
        self.options_validator: IManagerValidator = self.validate_validator(validator=options_validator)

        self.raw_data_validator.validate(raw_data)

        self._writer: IWriter = self.validate_writer(writer)

        self._simdata: SimData = SimDataSerializer.serialize(data=raw_data)
        self.__use_multiprocessing = use_multiprocessing

        # Валидируем опции конфигурации и применяем их
        self.__set_default_config()
        if options:
            self.set_options(options)

        self._result: dict | None = None

    @property
    def simdata(self) -> SimData:
        """Возвращает текущие сериализованные данные, используемые для симуляции"""
        return self._simdata

    @property
    def config(self) -> dict:
        """Возвращает текущую конфигурацию"""
        return self._config

    @property
    def writer(self) -> IWriter:
        """Возвращает текущий класс логгера симуляции"""
        return self._writer

    @property
    def result(self) -> dict:
        """Возвращает результат симуляции при его наличии"""
        if self._result:
            return self._result
        raise RuntimeError('Result is not calculated. Use "run" method for calculation before calling this method.')

    def set_new_simdata(self, raw_data: dict) -> None:
        """
            Проводит валидацию переданных сырых данных для симуляции и
            устанавливает сериализованные данные в качестве текущих
        """
        self.raw_data_validator.validate(raw_data)
        self._simdata = SimDataSerializer.serialize(data=raw_data)

    def set_options(self, options: dict) -> None:
        """Проводит валидацию и устанавливает переданные опции конфигурации"""
        if options:
            self.options_validator.validate(options)
            self._config.update(options)

    def __set_default_config(self):
        """Устанавливает опции конфигурации по умолчанию"""
        self._config = SIM_CONFIG.copy()

    @staticmethod
    def validate_writer(writer: Any) -> IWriter:
        """Производит валидацию переданного писаря результатов симуляции"""
        is_class = inspect.isclass(writer)
        if is_class and not issubclass(writer, IWriter):
            raise SimWriterValidationError(f'Your writer {writer.__name__} is not an subclass of IWriter!')
        if not is_class and not isinstance(writer, IWriter):
            raise SimWriterValidationError(f'Your writer {writer.__name__} is not an instance of IWriter!')
        return writer() if is_class else writer

    @staticmethod
    def validate_validator(validator: Any) -> IManagerValidator:
        """Производит валидацию переданного валидатора"""
        is_class = inspect.isclass(validator)
        if is_class and not issubclass(validator, IManagerValidator):
            raise ValidatorValidationError(
                f'Your validator {validator.__name__} is not an subclass of IManagerValidator!'
            )
        if not is_class and not isinstance(validator, IManagerValidator):
            raise ValidatorValidationError(
                f'Your validator {validator.__name__} is not an instance of IManagerValidator!'
            )
        return validator() if is_class else validator

    def set_raw_data_validator(self, validator: IManagerValidator) -> None:
        """Устанавливает валидатор сырых данных для симуляции"""
        self.raw_data_validator = self.validate_validator(validator=validator)

    def set_options_validator(self, validator: IManagerValidator) -> None:
        """Устанавливает валидатор опций конфигурации"""
        self.options_validator = self.validate_validator(validator=validator)

    def run(self) -> dict:
        """
        Запускает симуляцию в ручном/автоматическом режиме (зависит от текущей конфигурации)
        в отдельном процессе
        """
        if self.__use_multiprocessing:
            return self._run_using_multiprocessing()

        return self._process_simulation()

    def _run_using_multiprocessing(self) -> dict:
        with Manager() as manager:
            manager_dict = manager.dict()

            process = multiprocessing.Process(
                target=self._multiprocessing_simulation_callback,
                args=(
                    manager_dict,
                )
            )

            process.start()
            process.join()

            error_message = 'Не удалось получить результаты выполнения симуляции'

            if 'exception' in manager_dict:
                logger.error(error_message, {
                    'exception': manager_dict['exception']
                })
                raise RuntimeError(error_message)

            if 'result' not in manager_dict:
                raise RuntimeError(error_message)

            return manager_dict['result']

    def _multiprocessing_simulation_callback(self, manager_dict: DictProxy) -> None:
        try:
            result = self._process_simulation()
            manager_dict['result'] = result
        except Exception as e:
            manager_dict['exception'] = {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "traceback": traceback.format_exc(),
                "file": e.__traceback__.tb_frame.f_code.co_filename,
                "line": e.__traceback__.tb_lineno
            }

    @catch_errors
    def _process_simulation(self) -> dict:
        mode = self.config.get('mode')
        if not mode:
            raise RuntimeError('Missing mode parameter in simulation config!')

        reliability_calc_enabled = self.config['reliability_calc_enabled']

        # Запуск симуляции с планировщиком маршрутов
        if mode == 'auto':
            planned_trips = defaultdict(list)

            if self.config["solver"] != "GREEDY":
                # Запускаем планировщик, планируем рейсы на все время симуляции
                planner = Planner(
                    solver=self.config['solver'],
                    msg=self.config['msg'],
                    workers=self.config['workers'],
                    time_limit=self.config['time_limit']
                )
                planned = planner.run(self.simdata)

                planned_trips = defaultdict(list)

                for trip in planned['trips']:
                    planned_trip = PlannedTrip(
                        truck_id=trip['truck_id'],
                        shovel_id=trip['shovel_id'],
                        unload_id=trip['unload_id'],
                        order=trip['order']
                    )
                    planned_trips[planned_trip.truck_id].append(planned_trip)

            if reliability_calc_enabled:
                return run_reliability(
                    run_simulation_for_planned_trips,
                    self.simdata,
                    self.writer,
                    planned_trips,
                    self.config,
                    metric='weight',
                    processes_number=self.config['rel_process_num'],
                    init_runs_number=self.config['rel_init_runs_num'],
                    step_runs_number=self.config['rel_step_runs_num'],
                    max_runs_number=self.config['rel_max_runs_num'],
                    alpha=self.config['rel_alpha'],
                    r_target=self.config['rel_r_target'],
                    delta_target=self.config['rel_delta_target'],
                    consecutive=self.config['rel_consecutive'],
                    boot_b=self.config['rel_boot_b'],
                )

            return run_simulation_for_planned_trips(self.simdata, self.writer, planned_trips, self.config)

        # Запуск симуляции с ручным определением маршрутов
        if mode == 'manual':
            if reliability_calc_enabled:
                return run_reliability(
                    run_simulation,
                    self.simdata,
                    self.writer,
                    self.config,
                    metric='weight',
                    processes_number=self.config['rel_process_num'],
                    init_runs_number=self.config['rel_init_runs_num'],
                    step_runs_number=self.config['rel_step_runs_num'],
                    max_runs_number=self.config['rel_max_runs_num'],
                    alpha=self.config['rel_alpha'],
                    r_target=self.config['rel_r_target'],
                    delta_target=self.config['rel_delta_target'],
                    consecutive=self.config['rel_consecutive'],
                    boot_b=self.config['rel_boot_b'],
                )

            return run_simulation(self.simdata, self.writer, self.config)

        raise RuntimeError(
            f'PlanningAndSimulationManager has no behavior for "{mode}" value in "mode" parameter. '
            f'Set "auto" or "manual" value.'
        )
