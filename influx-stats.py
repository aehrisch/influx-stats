import requests
import itertools
import logging
import os
import sys

LOG = logging.getLogger('influx-stats')

LOG.setLevel(os.getenv('LOG_LEVEL', logging.INFO))
consoleHandler = logging.StreamHandler(sys.stdout)
LOG.addHandler(consoleHandler)

class InfluxWriter:

    def __init__(self, baseUrl, user, password, db):
        self.baseUrl = baseUrl
        self.user = user
        self.password = password
        self.db = db

    def write_result(self, lines):
        u = self.baseUrl + "/write"
        headers = {
            'Authorization': "Token " + self.user + ":" + self.password,
            'precision': 's'
        }
        params = {'db': self.db}
        r = requests.post(u, headers = headers, params = params, data = '\n'.join(lines))
        LOG.info("result of writing counts to db %s: %s", self.db, r.status_code)


class InfluxStats:

    def __init__(self, baseUrl, user, password, db, writer):
        self.baseUrl = baseUrl
        self.user = user
        self.password = password
        self.db = db
        self.writer = writer

    def run_query(self, q):
        u = self.baseUrl + "/query"
        headers = {
            'Authorization': "Token " + self.user + ":" + self.password
        }
        params = {'db': self.db, 'q': q}
        r = requests.get(u, headers = headers, params = params)
        LOG.debug("running query q=%s returned %s", q, r.status_code)
        return r.json()

    def get_measurements(self):
        json = self.run_query('show measurements')
        return list(itertools.chain(*json['results'][0]['series'][0]['values']))

    def count_points(self, series, time_limit = None):
        if time_limit:
            where_clause = ' where time >= now() - {0}d'.format(time_limit)
        else:
            where_clause = ''
        query = 'select count(*) from {0}{1}'.format(series, where_clause)
        json = self.run_query(query)
        values = json['results'][0]
        if 'series' in values:
            values = values['series'][0]
            values = values['values'][0]
            return sum(filter(lambda x: type(x) is int, values), 0)
        else:
            return 0

    def compute_sums(self):

        measurements = self.get_measurements()

        template = 'influx_points,period=total,db={0},measurement={1} value={2}'
        totals = 0
        lines = []
        for m in measurements:
            c = self.count_points(m)
            LOG.debug("count for %s is %s", m, c)
            totals = totals + c
            line = template.format(self.db, m, c)
            lines.append(line)

        line = template.format(self.db, 'total', totals)
        lines.append(line)

        LOG.debug("line: %s", lines)
        self.writer.write_result(lines)

def main():

    baseUrl = os.getenv('BASE_URL')

    result_db = os.getenv('RESULT_DB')
    result_user = os.getenv('RESULT_USER')
    result_pass = os.getenv('RESULT_PASS')

    check_db = os.getenv('CHECK_DB')
    check_user = os.getenv('CHECK_USER')
    check_pass = os.getenv('CHECK_PASS')

    writer = InfluxWriter(baseUrl, result_user, result_pass, result_db)

    LOG.info("counting points in DB %s", check_db)
    stats = InfluxStats(baseUrl, check_user, check_pass, check_db, writer)
    stats.compute_sums()

main()