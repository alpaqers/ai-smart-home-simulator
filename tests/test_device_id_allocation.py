from smart_home.client.controllers.device_id_allocator import next_device_id, seed_device_id_allocator


def test_seed_device_id_allocator():
    seed_device_id_allocator(5)
    assert next_device_id() == 5
    assert next_device_id() == 6