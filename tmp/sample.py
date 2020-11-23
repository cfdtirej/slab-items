from influxdb import InfluxDBClient

line_protocol = [{
    'time': '2020-10-10T12:01:30',
    'measurement': 'sample',
    'tags': {'tag': 10},
    'fields': {
        'data': 10,
    }
}]

client = InfluxDBClient(
    host='localhost',
    port=8086,
    username='root',
    password='root',
    database='sample'
)

client.write_points(line_protocol)
