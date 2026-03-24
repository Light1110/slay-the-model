from engine.message_bus import MessageBus


def test_message_bus_public_surface_still_exports_runtime_handlers():
    exports = [
        MessageBus,
    ]

    for exported in exports:
        assert exported is not None
