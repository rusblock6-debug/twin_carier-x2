from typing import Any


class ServiceLocator:
    __services: dict[str, Any] = {}

    @classmethod
    def bind(cls, alias: str, instance: Any) -> None:
        if cls.has(alias):
            raise RuntimeError(f"ServiceLocator: service '{alias}' already registered")
        cls.__services[alias] = instance

    @classmethod
    def get_or_fail(cls, alias: str, fail_message: str | None = None) -> Any:
        service = cls.get(alias)

        if service is None:
            fail_message = fail_message or f"ServiceLocator: service '{alias}' not registered"
            raise RuntimeError(fail_message)

        return service

    @classmethod
    def get(cls, alias: str) -> Any:
        if cls.has(alias):
            return cls.__services[alias]
        return None

    @classmethod
    def has(cls, alias: str) -> bool:
        return alias in cls.__services

    @classmethod
    def unbind(cls, alias: str) -> None:
        del cls.__services[alias]

    @classmethod
    def unbind_all(cls) -> None:
        cls.__services = {}
