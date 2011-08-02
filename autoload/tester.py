import math
import re
import signal
import subprocess
import time

COOLDOWN_TIME = 20
ERROR_FACTOR = 20

def alarm_handler(signum, frame):
    raise Alarm


class Alarm(Exception):
    pass


class HTTPerfError(Exception):
    pass


class Tester(object):
    def parse_result(self, raw_result):
        results = {}
        
        results['replies'] = int(re.search('Total: .*replies (\d+)', raw_result).groups()[0])
        results['conn_rate'] = float(re.search('Connection rate: (\d+\.\d)', raw_result).groups()[0])
        results['req_rate'] = float(re.search('Request rate: (\d+\.\d)', raw_result).groups()[0])
        rep_groups = re.search('Reply rate .*min (\d+\.\d) avg (\d+\.\d) max (\d+\.\d) stddev (\d+\.\d)', raw_result).groups()
        results['rep_rate_min'] = float(rep_groups[0])
        results['rep_rate_avg'] = float(rep_groups[1])
        results['rep_rate_max'] = float(rep_groups[2])
        results['rep_rate_stdv'] = float(rep_groups[3])
        results['rep_time'] = float(re.search('Reply time .* response (\d+\.\d)', raw_result).groups()[0])
        results['net_io'] = float(re.search('Net I\/O: (\d+\.\d)', raw_result).groups()[0])
        results['errors'] = int(re.search('Errors: total (\d+)', raw_result).groups()[0])

        return results

    def execute_test(self, rate, test):
        # HTTPerf collects samples every 5 seconds, so have to run at least 5 times more connections than rate.
        # Implies minimum test duration to be 5s.
        conns = int(rate * 5 + math.ceil((rate * 5) / 10.0))

        cleaned_args = {}
        for key, value in test.iteritems():
            if key not in ['title']:
                cleaned_args[key] = value

        test_args = ' '.join(['--%s %s' % (key, value) for key, value in cleaned_args.iteritems()])
        cmd = 'httperf --hog --timeout 5 --num-calls 1 --num-conns %s --rate %s %s' % (conns, rate, test_args)
        print 'Executing: \n%s\n' % cmd
        signal.alarm(20)
        try:
            proc = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=True)

            stdout_data, stderr_data = proc.communicate()
            if stdout_data and stderr_data:
                print 'Warning:\n%s' % stderr_data
            elif stderr_data:
                raise HTTPerfError(stderr_data)
            signal.alarm(0)  # reset the alarm
        except Alarm:
            print "Oops, taking too long!"
       
        return self.parse_result(stdout_data)

    def find_breaking_point(self, test):
        start_msg = 'Finding breaking point for test %s:' % test['title']
        print start_msg
        print '-' * len(start_msg)
        rate = 0

        previous_result = self.execute_test(1, test)
        result = previous_result

        while result and ((result['rep_rate_avg'] <= previous_result['rep_rate_avg'] * ERROR_FACTOR) and (result['errors'] <= previous_result['errors'] * ERROR_FACTOR) and (result['rep_time'] <= previous_result['rep_time'] * ERROR_FACTOR)):
            rate = rate + ((rate/100) + 1) * 10
            previous_result = result

            result = self.execute_test(rate, test)

        print 'Breaking point seems to be around %sreq/s.' % rate
        
        # Cooldown so breaking point tests don't affect range test.
        print 'Cooling down for %s seconds.\n' % COOLDOWN_TIME
        time.sleep(20)
        return rate

    def run(self, test):
        try:
            breaking_point = self.find_breaking_point(test)
        except HTTPerfError, e:
            print 'Error: \nUnable to find breaking point, aborting test %s - %s' % (test['title'], e) 
            return None
        
        start_msg = 'Running loadtest for test %s:' % test['title']
        print start_msg
        print '-' * len(start_msg)
        
        TEST_COUNT = 8
        rate_step = breaking_point / TEST_COUNT
        results = {}
        rate = 0
        for i in range(0, TEST_COUNT + 1):
            results[rate if rate else 1] = self.execute_test(rate if rate else 1, test)
            rate = rate + rate_step
        
        # Cooldown so tests don't affect each other.
        print 'Cooling down for %s seconds.\n' % COOLDOWN_TIME
        time.sleep(20)
        
        return results
