import asyncio

from smart_home.server.connection_handler import handle_client
from smart_home.common.config_loader import (
    AI_ENDPOINT,
    AI_PROVIDER,
    AI_TICK_INTERVAL_SECONDS,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    HOST,
    PORT,
    TICK_INTERVAL_SECONDS,
)
from smart_home.server.ai.transport import (
    AITransport,
    GeminiAITransport,
    HttpAITransport,
)
from smart_home.server.daily_task_reset import DailyTaskReset
from smart_home.server.event_bus import EventBus
from smart_home.server.scheduler import Scheduler
from smart_home.server.tasks import TaskDatabase
from smart_home.server.events import (
    AITickEvent,
    AITickRequestEvent,
    DeviceRegisterEvent,
    DeviceStateChangeRespEvent,
    DeviceStateChangeEvent,
    TaskListRequestEvent,
    TaskDueEvent,
    TickEvent,
    TimeShiftEvent,
)
from smart_home.server.processors import (
    AITickTriggerProcessor,
    AutomationAIProcessor,
    RegisterProcessor,
    ResponseProcessor,
    StateChangeProcessor,
    StateUpdateProcessor,
    TaskListProcessor,
)
from smart_home.server.processors.time_shift import TimeShiftProcessor
from smart_home.server.registry import DeviceRegistry
from smart_home.server.state_history import DeviceStateHistory
from smart_home.server.state_update_sender import StateUpdateSender
from smart_home.server.tick_emitter import TickEmitter
from smart_home.server.time_service import TimeService

async def start_server() -> None:
    registry = DeviceRegistry()
    history = DeviceStateHistory()
    bus = EventBus()
    time_service = TimeService()

    task_database = TaskDatabase()

    scheduler = Scheduler(
        event_bus=bus,
        task_database=task_database,
        max_delay_seconds=300,
    )
    await scheduler.start()

    register_processor = RegisterProcessor(registry, time_service)
    state_change_processor = StateChangeProcessor(registry, history, time_service)
    response_processor = ResponseProcessor()
    time_shift_processor = TimeShiftProcessor(time_service, event_bus=bus)
    task_list_processor = TaskListProcessor(task_database, time_service)
    state_update_sender = StateUpdateSender(registry, time_service)
    state_update_processor = StateUpdateProcessor(
        state_update_sender,
        task_database,
    )
    daily_task_reset = DailyTaskReset(task_database)
    ai_transport = None

    await bus.subscribe(DeviceRegisterEvent, register_processor.handle)
    await bus.subscribe(DeviceStateChangeEvent, state_change_processor.handle)
    await bus.subscribe(DeviceStateChangeRespEvent, response_processor.handle)
    await bus.subscribe(TimeShiftEvent, time_shift_processor.handle)
    await bus.subscribe(TaskListRequestEvent, task_list_processor.handle)
    await bus.subscribe(TaskDueEvent, state_update_processor.handle)
    await bus.subscribe(TickEvent, daily_task_reset.handle)

    ai_transport = _build_ai_transport()
    ai_enabled = ai_transport is not None
    if ai_transport is not None:
        ai_processor = AutomationAIProcessor(
            registry,
            history,
            ai_transport,
            task_database,
        )
        await bus.subscribe(AITickEvent, ai_processor.handle)

    ai_tick_trigger = AITickTriggerProcessor(
        bus,
        task_database,
        time_service,
        ai_enabled=ai_enabled,
    )
    await bus.subscribe(AITickRequestEvent, ai_tick_trigger.handle)

    tick_emitter = TickEmitter(
        bus,
        interval_seconds=TICK_INTERVAL_SECONDS,
        ai_tick_interval_seconds=AI_TICK_INTERVAL_SECONDS,
        time_service=time_service,
    )
    tick_emitter.start()

    server = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, registry, bus),
        HOST,
        PORT,
    )
    print(f"Server started on: {HOST}:{PORT}")

    try:
        async with server:
            await server.serve_forever()
    finally:
        await tick_emitter.stop()
        if ai_transport is not None:
            await ai_transport.aclose()


def _build_ai_transport() -> AITransport | None:
    provider = AI_PROVIDER.lower()

    if provider == "gemini":
        if not GEMINI_API_KEY:
            print("[AI] Gemini provider configured but GEMINI_API_KEY is missing")
            return None
        return GeminiAITransport(
            GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )

    if provider == "http":
        if not AI_ENDPOINT:
            print("[AI] HTTP provider configured but AI_ENDPOINT is missing")
            return None
        return HttpAITransport(AI_ENDPOINT)

    if AI_ENDPOINT:
        return HttpAITransport(AI_ENDPOINT)

    return None
