"""Research-system semantics hosted by Generic Documentation Engine."""


def register_builders(registry):
    from .builders import register
    register(registry)
