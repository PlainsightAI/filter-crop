import logging

from filter_runtime.filter import FilterConfig, Filter, Frame

__all__ = ['FilterCropConfig', 'FilterCrop']

logger = logging.getLogger(__name__)


class FilterCropConfig(FilterConfig):
    pass


class FilterCrop(Filter):
    """Put help documentation here."""

    @classmethod
    def normalize_config(cls, config: FilterCropConfig):
        config = FilterCropConfig(super().normalize_config(config))

        # TODO: normalize and validate parameters, don't touch touch stateful resources here

        return config

    def setup(self, config: FilterCropConfig):
        pass  # TODO: setup and connect to resources (files, databases, doomsday machines, etc...)

    def shutdown(self):
        pass  # TODO: shutdown

    def process(self, frames: dict[str, Frame]):

        # TODO: process

        return frames


if __name__ == '__main__':
    FilterCrop.run()
