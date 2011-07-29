from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table

class Reporter(object):
    fonts = {
        'Cicle': 'fonts/cicle.ttf',
        'Cicle-Strong': 'fonts/cicle_strong.ttf',

    }
    style_additions =[
        ParagraphStyle(name='PageTitle', fontName='Cicle-Strong', fontSize=25, alignment=TA_JUSTIFY),
        ParagraphStyle(name='PageByline', fontName='Cicle', fontSize=20, alignment=TA_JUSTIFY),
        ParagraphStyle(name='Heading', fontName='Cicle-Strong', fontSize=15, alignment=TA_JUSTIFY),
        ParagraphStyle(name='Text', fontName='Cicle', fontSize=12, alignment=TA_JUSTIFY),
        ParagraphStyle(name='Small', fontName='Cicle', fontSize=6, alignment=TA_JUSTIFY),
    ]
    elements = []

    def __init__(self):
        for name, path in self.fonts.iteritems():
            pdfmetrics.registerFont(TTFont(name, path))
        
        self.styles=getSampleStyleSheet()
        for style in self.style_additions:
            self.styles.add(style)
        
        self.doc = SimpleDocTemplate(
            "report.pdf",
            pagesize=landscape(letter),
            rightMargin=52,
            leftMargin=52,
            topMargin=25,
            bottomMargin=25
        )

    def draw_footer(self, canvas, doc):
        canvas.drawImage(ImageReader('media/logo.png'), 675, 15, 100, 13)

    def gen_heading(self):
        elements = []
        elements.append(Paragraph('Results - %s' % self.test['title'], self.styles["PageTitle"]))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph('http://localhost/foo/bar?fubar=1', self.styles["PageByline"]))
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
    
        cleaned = self.results.split('\n')[1:]
        while '' in cleaned:
            cleaned.remove('')
        cleaned = '<br />'.join(cleaned)
        elements.append(Paragraph(cleaned, self.styles["Small"]))
        elements.append(Spacer(1, 20))
        return elements
   
    def gen_conclusion(self):
        elements = []
        elements.append(Paragraph('Conclusion', self.styles["Heading"]))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph('Recommendation on performance results.', self.styles["Text"]))
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

