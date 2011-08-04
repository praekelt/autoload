import os

import autoload
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table

class Reporter(object):
    fonts = {
        'Cicle': os.path.join(os.path.dirname(autoload.__file__), 'fonts', 'cicle.ttf'),
        'Cicle-Strong': os.path.join(os.path.dirname(autoload.__file__), 'fonts', 'cicle_strong.ttf'),

    }
    style_additions =[
        ParagraphStyle(name='PageTitle', fontName='Cicle-Strong', fontSize=25, alignment=TA_JUSTIFY),
        ParagraphStyle(name='PageByline', fontName='Cicle', fontSize=20, alignment=TA_JUSTIFY),
        ParagraphStyle(name='Heading', fontName='Cicle-Strong', fontSize=15, alignment=TA_JUSTIFY),
        ParagraphStyle(name='TableHeading', fontName='Cicle-Strong', fontSize=6, alignment=TA_JUSTIFY),
        ParagraphStyle(name='Text', fontName='Cicle', fontSize=12, alignment=TA_JUSTIFY),
        ParagraphStyle(name='Small', fontName='Cicle', fontSize=6, alignment=TA_JUSTIFY),
    ]
    elements = []

    def __init__(self, output):
        for name, path in self.fonts.iteritems():
            pdfmetrics.registerFont(TTFont(name, path))
        
        self.styles=getSampleStyleSheet()
        for style in self.style_additions:
            self.styles.add(style)
        
        self.doc = SimpleDocTemplate(
            output,
            pagesize=landscape(letter),
            rightMargin=52,
            leftMargin=52,
            topMargin=25,
            bottomMargin=25
        )

    def draw_footer(self, canvas, doc):
        canvas.setTitle('Autoload Report')
        canvas.drawImage(ImageReader(os.path.join(os.path.dirname(autoload.__file__), 'media', 'logo.png')), 690, 15, 85, 13)

    def gen_heading(self):
        elements = []
        elements.append(Paragraph('Results - %s' % self.test['title'], self.styles["PageTitle"]))
        elements.append(Spacer(1, 10))
        url = self.test['server']
        if self.test.has_key('port'):
            url += ':%s' % self.test['port']
        url += self.test['uri']
        url = url.replace("'", '').replace('"', '')
        elements.append(Paragraph(url, self.styles["PageByline"]))
        elements.append(Spacer(1, 30))
        return elements
    
    def gen_params(self):
        elements = []
        elements.append(Paragraph('Test Parameters', self.styles["Heading"]))
        elements.append(Spacer(1, 10))
   
        params = '<br />'.join(["%s: %s" % (key, value) for key, value in self.test.iteritems()])
        elements.append(Paragraph(params, self.styles["Small"]))
        elements.append(Spacer(1, 20))
        return elements

    def gen_graphs(self):
        elements = []
        elements.append(self.graphs.reply_graph)
        elements.append(self.graphs.time_graph)
        elements.append(self.graphs.error_graph)
        return elements
        
    def gen_results_table(self):
        elements = []
        elements.append(Paragraph('Raw HTTPerf Results', self.styles["Heading"]))
        elements.append(Spacer(1, 10))


        data = [[
            Paragraph('Request Rate (req/s)', self.styles["TableHeading"]), 
            Paragraph('Reply Time (ms)', self.styles["TableHeading"]), 
            Paragraph('Errors', self.styles["TableHeading"]),
            Paragraph('Net IO (KB/s)', self.styles["TableHeading"]),
            Paragraph('Reply Rate Avg (req/s)', self.styles["TableHeading"]),
        ]]

        rates = self.results.keys()
        rates.sort()
        for rate in rates:
            data.append([
                Paragraph(str(rate), self.styles["TableHeading"]), 
                Paragraph(str(self.results[rate]['rep_time']), self.styles["Small"]), 
                Paragraph(str(self.results[rate]['errors']), self.styles["Small"]), 
                Paragraph(str(self.results[rate]['net_io']), self.styles["Small"]), 
                Paragraph(str(self.results[rate]['rep_rate_avg']), self.styles["Small"]), 
            ])

        elements.append(Table(data))
        elements.append(Spacer(1, 20))
        return elements
   
    def gen_conclusion(self):
        elements = []
        elements.append(Paragraph('Conclusion', self.styles["Heading"]))
        elements.append(Spacer(1, 10))

        rates = self.results.keys()
        rates.sort()

        breaking_point_rate = rates[-2]
        for rate in rates[1:]:
            if self.results[rate]['rep_time'] > self.results[rates[0]]['rep_time'] * 10:
                breaking_point_rate = rate
                break

        elements.append(Paragraph('Performance starts to degrade at roughly %s requests per second. At %s requests per second the service managed to reply at %s requests per second, reply time is %s percent longer and error rate is %s time(s) more than at idle.' % (breaking_point_rate, breaking_point_rate, int(self.results[breaking_point_rate]['rep_rate_avg']), int(self.results[breaking_point_rate]['rep_time']/self.results[rates[0]]['rep_time'] * 100), int(self.results[breaking_point_rate]['errors'])), self.styles["Text"]))
        elements.append(Spacer(1, 30))
        return elements

    def build_page(self, test, graphs, results):
        self.test = test
        self.graphs = graphs
        self.results = results

        self.layout = [
            ['', ''],
            ['', ''],
            ['', ''],
        ]

        self.elements += self.gen_heading()
        self.layout[0][1] = self.gen_params()
        self.layout[0][0] = self.gen_graphs()
        self.layout[1][1] = self.gen_results_table()
        self.layout[2][1] = self.gen_conclusion()

        self.elements.append(Table(self.layout, style=[('SPAN',(-2,-3),(-2,-1)),]))
        self.elements.append(Spacer(1, 20))

    def generate(self):
        self.doc.build(self.elements, onFirstPage=self.draw_footer, onLaterPages=self.draw_footer)

