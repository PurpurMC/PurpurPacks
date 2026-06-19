from abc import ABC, abstractmethod


class Publisher(ABC):
    @abstractmethod
    def needs_publish(self, pack_meta: dict) -> bool:
        """Return True if this publisher still needs to publish any artifact for this pack version."""
        ...

    @abstractmethod
    def publish_datapack(self, pack_meta: dict, artifact_path: str, artifact_name: str) -> None: ...

    @abstractmethod
    def publish_mod(self, pack_meta: dict, artifact_path: str, artifact_name: str, loader: str) -> None: ...
