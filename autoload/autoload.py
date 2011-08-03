#!/usr/bin/env python

import ConfigParser

from grapher import Grapher
from reporter import Reporter
from tester import Tester
    
#import argparse
#parser = argparse.ArgumentParser(description='Run HTTPerf loadtests and output PDF report.')
#parser.add_argument('config', type=str, nargs=1, help='configuration file detailing tests to be executed')

from optparse import OptionParser
import sys
parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help="configuration file detailing tests to be executed", metavar="FILE")

options, args = parser.parse_args()
if not options.config:
    print "Undefined config. You have to specify a test config file, see autoload -h"
    sys.exit(1)

def load_tests():
    #conf_file = vars(parser.parse_args())['config'][0]
    conf_file = options.config
    config = ConfigParser.RawConfigParser()
    config.read(conf_file)

    tests = []
    for test_section in ','.join(config.get('autoload', 'tests').split('\n')).split(','):
        if test_section:
            test = {'title': test_section.capitalize()}
            for option in config.options(test_section):
                value = config.get(test_section, option)
                if value.lower() == 'true':
                    value = ''
                elif value.lower() == 'false':
                    continue
                test[option] = value
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


