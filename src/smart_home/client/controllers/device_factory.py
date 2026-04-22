from ..models.device import Device


def create_lamp(device_id: int, device_type: str, capabilities: dict, device_state: dict) -> Device:
    brightness = input("Podaj jasność lampy (0-100): ")
    return Device(
        device_id=device_id,
        device_type=device_type,
        capabilities=capabilities,
        device_state=device_state,
        parameters={"brightness": brightness}
    )


def create_thermometer(device_id: int, device_type: str, capabilities: dict, device_state: dict) -> Device:
    unit = input("Podaj jednostkę temperatury (C/F): ")
    return Device(
        device_id=device_id,
        device_type=device_type,
        capabilities=capabilities,
        device_state=device_state,
        parameters={"unit": unit}
    )


def create_sensor(device_id: int, device_type: str, capabilities: dict, device_state: dict) -> Device:
    sensitivity = input("Podaj czułość czujnika (low/medium/high): ")
    return Device(
        device_id=device_id,
        device_type=device_type,
        capabilities=capabilities,
        device_state=device_state,
        parameters={"sensitivity": sensitivity}
    )


def create_ac(device_id: int, device_type: str, capabilities: dict, device_state: dict) -> Device:
    target_temp = input("Podaj docelową temperaturę klimatyzacji: ")
    return Device(
        device_id=device_id,
        device_type=device_type,
        capabilities=capabilities,
        device_state=device_state,
        parameters={"target_temp": target_temp}
    )