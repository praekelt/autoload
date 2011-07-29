#!/usr/bin/env python

import os
import re

#result = os.popen('httperf --server localhost --uri "/" --num-conn 50 --num-call 10 --timeout 5 --rate 5 --port 80').read()
#import pdb; pdb.set_trace()
raw_result = 'httperf --timeout=5 --client=0/1 --server=localhost --port=80 --uri=/ --rate=5 --send-buffer=4096 --recv-buffer=16384 --num-conns=50 --num-calls=10\nMaximum connect burst length: 1\n\nTotal: connections 50 requests 500 replies 500 test-duration 9.800 s\n\nConnection rate: 5.1 conn/s (196.0 ms/conn, <=1 concurrent connections)\nConnection time [ms]: min 0.3 avg 0.4 max 1.0 median 0.5 stddev 0.1\nConnection time [ms]: connect 0.0\nConnection length [replies/conn]: 10.000\n\nRequest rate: 51.0 req/s (19.6 ms/req)\nRequest size [B]: 62.0\n\nReply rate [replies/s]: min 50.0 avg 50.0 max 50.0 stddev 0.0 (1 samples)\nReply time [ms]: response 0.0 transfer 0.0\nReply size [B]: header 216.0 content 151.0 footer 0.0 (total 367.0)\nReply status: 1xx=0 2xx=500 3xx=0 4xx=0 5xx=0\n\nCPU time [s]: user 2.58 system 7.20 (user 26.3% system 73.5% total 99.8%)\nNet I/O: 21.4 KB/s (0.2*10^6 bps)\n\nErrors: total 0 client-timo 0 socket-timo 0 connrefused 0 connreset 0\nErrors: fd-unavail 0 addrunavail 0 ftab-full 0 other 0\n'

print raw_result

results = {}
results['replies'] = re.search('Total: .*replies (\d+)', raw_result).groups()[0]
results['conn_rate'] = re.search('Connection rate: (\d+\.\d)', raw_result).groups()[0]
results['req_rate'] = re.search('Request rate: (\d+\.\d)', raw_result).groups()[0]
results['rep_rate_min'], results['rep_rate_avg'], results['rep_rate_max'], results['rep_rate_stdv'] = re.search('Reply rate .*min (\d+\.\d) avg (\d+\.\d) max (\d+\.\d) stddev (\d+\.\d)', raw_result).groups()
results['rep_time'] = re.search('Reply time .* response (\d+\.\d)', raw_result).groups()[0]
results['net_io'] = re.search('Net I\/O: (\d+\.\d)', raw_result).groups()[0]
results['errors'] = re.search('Errors: total (\d+)', raw_result).groups()[0]

print results

def print_header():
    print "\t".join(["dem_req_rate", "req_rate", "con_rate", "min_rep_rate", "avg_rep_rate", "max_rep_rate", "stddev_rep_rate", "resp_time", "net_io", "errors"])

def print_result(results):
    num_call = 1
    curr_rate = 1

    dem_req = num_call * curr_rate

    print "\t".join([str(dem_req), results['req_rate'], results['conn_rate'], results['rep_rate_min'], results['rep_rate_avg'], results['rep_rate_max'], results['rep_rate_stdv'], results['rep_time'], results['net_io'], results['errors']])

print_header()
print_result(results)

tests = [{
        'title': 'Home',
        'path': '/',
    },
    {
        'title': 'Signup',
        'path': '/register',
    },
    {
        'title': 'Login',
        'path': '/login',
    },
    {
        'title': 'News',
        'path': '/news',
    },
]

result = 'httperf --timeout=5 --client=0/1 --server=localhost --port=80 --uri=/ --rate=5 --send-buffer=4096 --recv-buffer=16384 --num-conns=50 --num-calls=10\nMaximum connect burst length: 1\n\nTotal: connections 50 requests 500 replies 500 test-duration 9.800 s\n\nConnection rate: 5.1 conn/s (196.0 ms/conn, <=1 concurrent connections)\nConnection time [ms]: min 0.3 avg 0.4 max 1.0 median 0.5 stddev 0.1\nConnection time [ms]: connect 0.0\nConnection length [replies/conn]: 10.000\n\nRequest rate: 51.0 req/s (19.6 ms/req)\nRequest size [B]: 62.0\n\nReply rate [replies/s]: min 50.0 avg 50.0 max 50.0 stddev 0.0 (1 samples)\nReply time [ms]: response 0.0 transfer 0.0\nReply size [B]: header 216.0 content 151.0 footer 0.0 (total 367.0)\nReply status: 1xx=0 2xx=500 3xx=0 4xx=0 5xx=0\n\nCPU time [s]: user 2.58 system 7.20 (user 26.3% system 73.5% total 99.8%)\nNet I/O: 21.4 KB/s (0.2*10^6 bps)\n\nErrors: total 0 client-timo 0 socket-timo 0 connrefused 0 connreset 0\nErrors: fd-unavail 0 addrunavail 0 ftab-full 0 other 0\n'

if __name__ == '__main__':
    from grapher import Grapher
    from reporter import Reporter
    
    reporter = Reporter()
    for test in tests:
        graphs = Grapher([])
        reporter.build_page(test, graphs, result)

    reporter.generate()
    graphs.cleanup()
