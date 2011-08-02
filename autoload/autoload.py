#!/usr/bin/env python

import argparse
import ConfigParser

from grapher import Grapher
from reporter import Reporter
from tester import Tester
    
parser = argparse.ArgumentParser(description='Run HTTPerf loadtests and output PDF report.')
parser.add_argument('config', type=str, nargs=1, help='configuration file detailing tests to be executed')

def load_tests():
    conf_file = vars(parser.parse_args())['config'][0]
    config = ConfigParser.RawConfigParser()
    config.read(conf_file)

    tests = []
    for test_section in ','.join(config.get('autoload', 'tests').split('\n')).split(','):
        if test_section:
            test = {'title': test_section.capitalize()}
            for option in config.options(test_section):
                test[option] = config.get(test_section, option)
            tests.append(test)

    return tests

if __name__ == '__main__':
    #import signal
    #from tester import alarm_handler
    #signal.signal(signal.SIGALRM, alarm_handler)
    reporter = Reporter()
    tester = Tester()

    tests = load_tests()
    all_graphs = []
    for test in tests:
        results = tester.run(test)
        if results:
            graphs = Grapher(results, test)
            all_graphs.append(graphs)
            reporter.build_page(test, graphs, results)

    reporter.generate()
    for graphs in all_graphs:
        graphs.cleanup()


