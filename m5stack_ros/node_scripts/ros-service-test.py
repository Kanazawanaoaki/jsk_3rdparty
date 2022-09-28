import roslibpy

client = roslibpy.Ros(host='localhost', port=9090)
client.run()

service = roslibpy.Service(client, '/firdge_pi_task', 'jsk_2022_09_fridge_pi/FridgePiOrder')
request = roslibpy.ServiceRequest({'task': 'test'})

print('Calling service...')
result = service.call(request)
print('Service response: {}'.format(result))

client.terminate()
