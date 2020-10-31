import csv

from datetime import datetime
from typing import List, Dict

from influxdb import InfluxDBClient
from tqdm import tqdm


def conv_list_value_type(data: list) -> list:
    result = []
    for v in data:
        try:
            value = float(v)
            result.append(value)
        except ValueError:
            value = str(v)
            result.append(value)
    return result


def to_rfc3339(timestamp: str) -> str:
        if '/' in timestamp:
            return datetime.strptime(timestamp.partition('.')[0] + '+0900', '%Y/%m/%d %H:%M:%S%z').isoformat()
        elif '-' in timestamp:
            return datetime.strptime(timestamp.partition('.')[0] + '+0900', '%Y-%m-%d %H:%M:%S%z').isoformat()


def to_lineProtocol(header: list, fieldline: list, measurement: str, tags: Dict[str, str]) -> Dict:
    fields = {}
    field_data = conv_list_value_type(fieldline[1:])
    for k, v in zip(header[1:], field_data):
        try:
            fields[k] = v
        except IndexError:
            pass
    line_protocol = [
        {
            'measurement': measurement,
            'tags': tags,
            'time': to_rfc3339(fieldline[0]),
            'fields': fields
        }
    ]
    return line_protocol


def csv_to_lineProtocol(csvfile, measurement, tags) -> List:
    with open(csvfile, 'r') as f:
        table = [_ for _ in csv.reader(f)]
        header = table.pop(0)
        line_protocols = []
        for data in table:
            line_protocols.append(to_lineProtocol(header, data, measurement, tags))
        return line_protocols


class InfluxHandling(InfluxDBClient):

    def csv_write(self, csvfile: str, measurement: str, tags: dict) -> None:
        with open(csvfile, 'r') as f:
            table =  [_ for _ in csv.reader(f)]
            cnt = 0
            try:
                for row in tqdm(table):
                    if cnt == 0:
                        header = row
                        cnt += 1
                        continue
                    line_protocol = to_lineProtocol(header, row, measurement, tags)
                    self.write_points(line_protocol)
            except:
                pass
        return None
    
    def get_single_column(self, measurement: str, field_key: str) -> List[dict]:
        q = f'SELECT {field_key} FROM {measurement}'
        result = list((self.query(q)))[0]
        return result


