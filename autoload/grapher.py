import os

from gruffy import Line
from reportlab.platypus import Image

class Grapher(object):
    def draw_reply_graph(self):
        g = Line()
        g.title = "Average Reply Rate (Responses per Second)"
        g.theme_greyscale()

        g.data("Attempted Request Rate", [2, 4, 8, 16, 32, 64], color='#6886b4')
        g.data("Average Reply Rate", [2, 4, 8, 15, 15, 15], color='#fdd84e')
        g.labels = {0: '2', 1: '4', 2: '8', 3: '16', 4: '32', 5: '64'}

        g.write('reply.png')
        return Image('reply.png', 540/2.65, 400/2.65)

    def draw_time_graph(self):
        g = Line()
        g.title = "Average Response Time (in ms)"
        g.theme_greyscale()

        g.data("Average Response Time", [1, 2, 3, 36, 42, 54], color='#fdd84e')
        g.labels = {0: '2', 1: '4', 2: '8', 3: '16', 4: '32', 5: '64'}

        g.write('time.png')
        return Image('time.png', 540/2.65, 400/2.65)

    def draw_error_graph(self):
        g = Line()
        g.title = "Errors"
        g.theme_greyscale()

        g.data("Errors", [2, 2, 2, 2, 5, 15], color='#fdd84e')
        g.labels = {0: '2', 1: '4', 2: '8', 3: '16', 4: '32', 5: '64'}

        g.write('errors.png')
        return Image('errors.png', 540/2.65, 400/2.65)

    def __init__(self, results):
        self.reply_graph = self.draw_reply_graph()
        self.time_graph = self.draw_time_graph()
        self.error_graph = self.draw_error_graph()

    def cleanup(self):
        os.remove('errors.png')
        os.remove('reply.png')
        os.remove('time.png')
