import os

from gruffy import Line
from reportlab.platypus import Image

class Grapher(object):
    def resolve_filename(self, prefix):
        return '%s_%s.png' % (prefix, self.test['title'])

    def draw_reply_graph(self):
        g = Line()
        g.title = "Average Reply Rate (Responses per Second)"
        g.theme_greyscale()

        req_rates = sorted(self.results.iterkeys())
        reply_rates = []
        g.labels = {}
        i = 0
        for rate in req_rates:
            reply_rates.append(float(self.results[rate]['rep_rate_avg']))
            g.labels[i] = str(rate)
            i += 1

        g.data("Attempted Request Rate", req_rates, color='#6886b4')
        g.data("Average Reply Rate", reply_rates, color='#fdd84e')

        g.write(self.resolve_filename('reply'))
        return Image(self.resolve_filename('reply'), 540/2.65, 400/2.65)

    def draw_time_graph(self):
        g = Line()
        g.title = "Average Response Time (in ms)"
        g.theme_greyscale()
        
        req_rates = sorted(self.results.iterkeys())
        rep_times = []
        g.labels = {}
        i = 0
        for rate in req_rates:
            rep_times.append(float(self.results[rate]['rep_time']))
            g.labels[i] = str(rate)
            i += 1

        g.data("Average Response Time", rep_times, color='#fdd84e')

        g.write(self.resolve_filename('time'))
        return Image(self.resolve_filename('time'), 540/2.65, 400/2.65)

    def draw_error_graph(self):
        g = Line()
        g.title = "Errors"
        g.theme_greyscale()
        
        req_rates = sorted(self.results.iterkeys())
        errors = []
        g.labels = {}
        i = 0
        for rate in req_rates:
            errors.append(float(self.results[rate]['errors']))
            g.labels[i] = str(rate)
            i += 1

        g.data("Errors", errors, color='#fdd84e')

        g.write(self.resolve_filename('errors'))
        return Image(self.resolve_filename('errors'), 540/2.65, 400/2.65)

    def __init__(self, results, test):
        self.results = results
        self.test = test

        self.reply_graph = self.draw_reply_graph()
        self.time_graph = self.draw_time_graph()
        self.error_graph = self.draw_error_graph()

    def cleanup(self):
        os.remove(self.resolve_filename('errors'))
        os.remove(self.resolve_filename('reply'))
        os.remove(self.resolve_filename('time'))
