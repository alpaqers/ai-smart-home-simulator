import message_pb2

msg = message_pb2.DeviceStateChange() #nowa pusta wiadomosc

msg.device_id = 1
msg.device_type = 2
msg.parameters["temperature"] = "24.6"

data = msg.SerializeToString() #serializacja

print(data)

received = message_pb2.DeviceStateChange() #druga pusta wiadomosc
received.ParseFromString(data) #deserializacja

print(received.device_id) 
print(received.device_type)
print(received.parameters["temperature"])