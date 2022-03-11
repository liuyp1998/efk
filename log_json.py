# import json
import re
import time
# from datetime import datetime
from elasticsearch import Elasticsearch
import calendar


class ES():
    es_host = "" esip地址
    port = 9200
    timeout = 15000
    index = "secure"

    def conn(self):
        es = Elasticsearch(hosts=self.es_host, port=self.port, timeout=self.timeout)
        return es

    def count(self, index=index):
        es = self.conn()
        count = es.count(index=index)['count']
        return count

    def add_date(self, row_obj):
        """
        :param row_obj    The document  类型：dict
        """
        index = "linux"
        es = self.conn()
        es.index(index=index, body=row_obj)
        print("添加成功")

    def get_page(self, page, size):
        try:
            rs = self.conn().search(index=self.index, body={
                "query": {
                    "match_all": {}
                },
                "from": page,
                "size": size
            })
            data = []
            for entry in rs['hits']['hits']:
                result = entry['_source']['message']
                data.append(result)
            return data
        except:
            return "error"

    def delete(self):
        es = self.conn()
        index = "linux"
        es.delete_by_query(index=index, body={
                "query": {
                    "match_all": {}
                }
            })
        print("delete" + index + "ok")

    def data_json(self, data):
        # json_dd = []
        for times in data:
            ss = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", times)
            ip = ' '.join(ss)
            if ip != '':
                string = times.split()
                date_time = time.strftime("%Y-") + str(format_time(string[0])) + "-" + string[1] + " " + string[2]
                ts = time.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                timestamp = time.mktime(ts)
                secure = {
                    "@timestamp": timestamp,
                    "date_time": date_time,
                    "local_time": string[0] + " " + string[1] + " " + string[2],
                    "node_name": string[3],
                    "status": string[5],
                    "password": string[6],
                    "user": string[8] if string[8] != "invalid" else string[10],
                    "ip": ip
                }
                try:
                    self.add_date(row_obj=secure)
                except:
                    print("添加失败")
        #     relust = json.dumps(secure)
        #     json_dd.append(relust)
        # return json_dd


def format_time(dd):
    date = list(calendar.month_abbr).index(dd)
    return date


def pages(count):
    es = ES()
    size = 200
    page = int(count / size + 1)
    max_sum = page - 1
    for i in range(page):
        if i != max_sum:
            es.data_json(es.get_page(page=i, size=size))
        else:
            size = int(count - (size * i))
            if size != 0:
                es.data_json(es.get_page(page=i, size=size))


if __name__ == '__main__':
    es = ES()
    es.delete()
    count = es.count()
    pages(count)


