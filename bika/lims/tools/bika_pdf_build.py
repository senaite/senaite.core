from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from PIL import Image as PIL_Image
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName, expandpath
from Products.PythonScripts.standard import newline_to_br
from bika.lims.tools import ToolFolder
from bika.lims import bikaMessageFactory as _
from cStringIO import StringIO
from reportlab import platypus
from reportlab.lib import styles, colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import haveImages, ImageReader
from reportlab.platypus import FrameBreak
from reportlab.platypus.doctemplate import *
from reportlab.platypus.flowables import ParagraphAndImage, Image
from reportlab.platypus.paragraph import Paragraph
import cStringIO
import csv
import string
import tempfile
from bika.lims.interfaces.tools import Ibika_pdf_build
from zope.interface import implements

class bika_pdf_build(UniqueObject, SimpleItem):
    """ PDFBuildTool """

    implements(Ibika_pdf_build)

    security = ClassSecurityInfo()
    id = 'bika_pdf_build'
    title = 'PDF Build Tool'
    description = 'Build PDF'
    meta_type = 'PDF Build Tool'

    class MyPDFDoc :
        # with thanks to Jerome Alet's demo


        def __init__(self, context, filename, headings, all_first_heads, all_other_heads, all_ars, all_results, all_cats, all_oor, all_dries, all_attachments, all_remarks, all_managers, all_disclaimers, lab_title) :
            def myFirstPage(canvas, doc):
                canvas.saveState()
                drawLogos(canvas, doc)
                canvas.restoreState()


            def myLaterPages(canvas, doc):
                canvas.saveState()
                drawLogos(canvas, doc)
                canvas.restoreState()

            def drawLogos(canvas, doc):
                if self.logos[self.logo_imgs[0]] is not None :
                    # draws the logo if it exists
                    (image, width, height) = self.logos[self.logo_imgs[0]]
                    canvas.drawImage(image, 0.75 * inch, doc.pagesize[1] - inch * 1.2, width / 1.5, height / 1.5)
                if self.logos[self.logo_imgs[1]] is not None :
                    # draws the accreditation logo if it exists
                    (image, width, height) = self.logos[self.logo_imgs[1]]
                    canvas.drawImage(image, 5.5 * inch, doc.pagesize[1] - inch * 1.2, width / 1.5, height / 1.5)
                canvas.setFont('Helvetica', 10)
                canvas.drawString(4 * inch, 0.75 * inch, "Page %d" % doc.page)

            # save some datas
            self.context = context
            self.built = 0
            self.objects = []

            # get all the images we need now, in case we've got
            # several pages this will save some CPU

            self.logos = {}
            self.logo_imgs = ['logo_print.jpg', 'accreditation_print.jpg']
            for pic in self.logo_imgs:
                image = self.getImageFP(pic)
                self.logos[pic] = image

            images = {}
            icons = ['no_invoice.png', 'dry.png', 'accredited.jpg', 'exclamation.jpg', 'telephone.jpg', 'email.jpg', ]
            for pic in icons:
                image = self.getImageFromFS(pic, width = 12)
                images[pic] = image
            for manager in all_managers:
                owner = manager
                pic = 'Signature'
                image = self.getImageFromZODB(pic, owner)
                images[manager.getId()] = image


            #   save some colors
            bordercolor = colors.HexColor(0x999933)
            #backgroundcolor = colors.HexColor(0xD3D3AD)
            backgroundcolor = colors.HexColor(0xFFFFFF)
            dryheadcolor = colors.HexColor(0xA6B5DB)
            #drybodycolor = colors.HexColor(0xDAE0F0)
            drybodycolor = colors.HexColor(0xFFFFFF)
            #catcolor = colors.HexColor(0xB6C0D1)
            catcolor = colors.HexColor(0xFFFFFF)

            # we will build an in-memory document
            # instead of creating an on-disk file.
            self.report = cStringIO.StringIO()

            # initialise a PDF document using ReportLab's platypus
            self.doc = SimpleDocTemplate(self.report)

            # get page size
            page_width = self.doc.pagesize[0] - 1.5 * inch
            h_col_width = page_width / 2
            page_height = self.doc.pagesize[1]

            # get the default style sheets
            self.StyleSheet = styles.getSampleStyleSheet()
            self.StyleSheet['Normal'].fontName = 'Helvetica'
            self.StyleSheet['Heading1'].fontName = 'Helvetica'

            # then build a simple doc with ReportLab's platypus
            self.append(Spacer(0, 20))

            h_table = platypus.Table(headings, colWidths = (h_col_width, h_col_width))

            style = platypus.TableStyle([('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                         ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                                         ('FONT', (0, 0), (-1, -1), 'Helvetica'),

                                       ])
            h_table.setStyle(style)
            self.append(h_table)

            self.append(Spacer(0, 10))

            no_ars = all_ars[0]

            col = page_width / ((no_ars * 2) + 4)

            for i in range(len(all_results)):
                these_ars = all_ars[i]
                these_results = all_results[i]
                these_dries = all_dries[i]
                cols = [col * 4, ]
                """ make as fed column wider than dry column """
                for j in range (these_ars):
                    cols.append(col * 1.4)
                    cols.append(col * 0.6)
                col_widths = tuple(cols)
                first_page = True
                if i > 0:
                    self.append(FrameBreak())
                    self.append(Spacer(0, 10))

                """ attachments """
                attachments = all_attachments[i]
                if len(attachments) == 1:
                    attachments[0][1] == 'None'
                else:
                    a_table = platypus.Table(attachments)
                    table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   ('GRID', (0, 0), (-1, -1), 0.1, bordercolor),
                                   ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                   ('BACKGROUND', (0, 0), (0, -1), backgroundcolor),
                                   ('BACKGROUND', (0, 0), (-1, 0), backgroundcolor),
                                   ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 10),
                                    ]
                    style = platypus.TableStyle(table_style)
                    a_table.setStyle(style)
                    a_table.setStyle(style)
                    self.append(a_table)

                self.append(Spacer(0, 10))

                """ determine no of lines in attachment table """
                attachment_count = 0
                for attachment in attachments:
                    attachment_count += 1
                    attachment_count += attachment.count('\n')

                """ headings and results """


                general_table_style = [('ALIGN', (0, 0), (0, -1), 'LEFT'),
                               ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                               ('BACKGROUND', (0, 0), (0, -1), backgroundcolor),
                               ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                                ]


                page_max = 18 - attachment_count

                these_oor = all_oor[i]
                these_cats = all_cats[i]
                num_lines = len(these_results)

                slice_end = 0

                while slice_end < num_lines:
                    """ headings """
                    table_style = list(general_table_style)
                    if first_page:
                        page_content = list(all_first_heads[i])
                        table_style.append(('GRID', (0, 0), (0, -1), 0.1, bordercolor))
                        table_style.append(('BACKGROUND', (0, 11), (-1, 11), backgroundcolor))
                        table_style.append(('LINEBELOW', (0, 10), (-1, 10,), 1, bordercolor))
                        table_style.append(('LINEBELOW', (0, 11), (-1, 11), 1, bordercolor))

                        """ span and box the header lines """
                        for j in range(11):
                            for k in range(these_ars):
                                table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))

                    else:
                        self.append(FrameBreak())
                        self.append(Spacer(0, 20))
                        page_content = list(all_other_heads[i])
                        table_style.append(('GRID', (0, 0), (0, -1), 0.1, bordercolor))
                        table_style.append(('BACKGROUND', (0, 4), (-1, 4), backgroundcolor))
                        table_style.append(('LINEBELOW', (0, 3), (-1, 3,), 1, bordercolor))
                        table_style.append(('LINEBELOW', (0, 4), (-1, 4), 1, bordercolor))

                        """ span and box the header lines """
                        for j in range(4):
                            for k in range(these_ars):
                                table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))

                    offset = len(page_content)

                    slice_start = slice_end
                    slice_end = slice_start + page_max
                    if slice_end > num_lines:
                        slice_end = num_lines
                    page_max = 30

                    page_results = these_results[slice_start: slice_end]

                    """ results """
                    page_content.extend(page_results)
                    c_table = platypus.Table(page_content, colWidths = col_widths)

                    for orig_highlight in these_oor:
                        if orig_highlight[1] < slice_start:
                            continue
                        if orig_highlight[1] >= slice_end:
                            continue
                        highlight = ((orig_highlight[0] * 2) + 1, orig_highlight[1] + offset - slice_start)
                        table_style.append(('TEXTCOLOR', highlight, highlight, colors.red))

                    table_length = len(page_content)
                    if first_page:
                        first_page = False

                        """ span and box the detail lines """
                        for k in range(these_ars):
                            for j in range(11, table_length):
                                if k in these_dries:
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 1, j), 0.1, bordercolor))
                                    table_style.append(('BOX', ((k * 2) + 2, j), ((k * 2) + 2, j), 0.1, bordercolor))
                                else:
                                    table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))
                        """ colour the dry matter columns """
                        for k in range(these_ars):
                            if k in these_dries:
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 11), ((k * 2) + 2, 11), dryheadcolor))
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 12), ((k * 2) + 2, -1), drybodycolor))
                    else:

                        """ span and box the detail lines """
                        for j in range(4, table_length):
                            for k in range(these_ars):
                                if k in these_dries:
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 1, j), 0.1, bordercolor))
                                    table_style.append(('BOX', ((k * 2) + 2, j), ((k * 2) + 2, j), 0.1, bordercolor))
                                else:
                                    table_style.append(('SPAN', ((k * 2) + 1, j), ((k * 2) + 2, j)))
                                    table_style.append(('BOX', ((k * 2) + 1, j), ((k * 2) + 2, j), 0.1, bordercolor))
                        """ colour the dry matter columns """
                        for k in range(these_ars):
                            if k in these_dries:
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 4), ((k * 2) + 2, 4), dryheadcolor))
                                table_style.append(('BACKGROUND', ((k * 2) + 2, 5), ((k * 2) + 2, -1), drybodycolor))

                    """ colour and span the category lines """
                    for cat in these_cats:
                        if cat < slice_start:
                            continue
                        if cat >= slice_end:
                            continue
                        cat_box_start = (0, cat + offset - slice_start)
                        cat_box_end = (-1, cat + offset - slice_start)
                        table_style.append(('SPAN', cat_box_start, cat_box_end))
                        table_style.append(('BACKGROUND', cat_box_start, cat_box_end, catcolor))
                    style = platypus.TableStyle(table_style)
                    c_table.setStyle(style)
                    self.append(c_table)


                self.append(Spacer(0, 10))

                """ remarks """
                remarks = all_remarks[i]
                if remarks:
                    r_table = platypus.Table(remarks)
                    table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   ('GRID', (0, 0), (-1, -1), 0.1, bordercolor),
                                   ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                   ('BACKGROUND', (0, 0), (0, -1), backgroundcolor),
                                   ('BACKGROUND', (0, 0), (-1, 0), backgroundcolor),
                                   ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 9),
                                    ]
                    style = platypus.TableStyle(table_style)
                    r_table.setStyle(style)
                    self.append(KeepTogether(r_table))


                self.append(Spacer(0, 10))

                """ disclaimers """
                disclaimers = all_disclaimers[i]
                table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkgray),
                               ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                                ]
                style = platypus.TableStyle(table_style)
                h_spacer = 10
                d_stuff = []
                for disclaimer in disclaimers:
                    disclaimer.append(' ')
                d_table = platypus.Table(disclaimers, colWidths = (page_width - 3, 3))
                d_table.setStyle(style)
                self.append(d_table)

                i += 1

            self.append(Spacer(0, 10))
            """ signatures"""

            textStyle = ParagraphStyle('BodyText',
                                  alignment = 0,
                                  fontName = 'Helvetica',
                                  fontSize = 10)
            table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                           ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                           ('FONT', (0, 0), (-1, -1), 'Helvetica'),
                           ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ]
            style = platypus.TableStyle(table_style)
            h_spacer = 6
            for manager in all_managers:
                keepers = []

                signatures = [(images[manager.getId()], ' '), ]

                s_table = platypus.Table(signatures, colWidths = (h_col_width, h_col_width))

                s_table.setStyle(style)
                keepers.append(s_table)

                m_stuff = []
                name = manager.Title()
                phone = manager.getBusinessPhone()
                email = manager.getEmailAddress()

                m_stuff.append([name, images['telephone.jpg'], phone, images['email.jpg'], email])
                x = page_width - (len(name) * h_spacer) - (len(phone) * h_spacer) - len(email) - 36
                m_table = platypus.Table(m_stuff, colWidths = (len(name) * h_spacer, 18, len(phone) * h_spacer, 18, len(email) + x))
                m_table.setStyle(style)
                keepers.append(m_table)
                para = Paragraph(lab_title, textStyle)
                keepers.append(para)
                keepers.append(Spacer(0, 10))
                self.append(KeepTogether(keepers))


            # generation du document PDF
            self.doc.build(self.objects, onFirstPage = myFirstPage, onLaterPages = myLaterPages)

            self.built = 1

        def getImageFP(self, name) :
            """Retrieves an image filepath from the ZODB file system
            """
            location = self.context.aq_parent
            try :
                # try to get it from ZODB
                img_pointer = getattr(location, name)
                fp = expandpath(img_pointer._filepath)
            except AttributeError :
                # not found !
                return None

            return (fp, img_pointer.width, img_pointer.height)

        def getImageFromFS(self, name, width = None, height = None) :
            """Retrieves an Image from the ZODB file system
            """
            location = self.context.aq_parent
            try :
                # try to get it from ZODB
                img_pointer = getattr(location, name)
                fp = expandpath(img_pointer._filepath)
                if not width:
                    width = img_pointer.width
                if not height:
                    height = img_pointer.height
                p_img = platypus.Image(fp, width = width / 2, height = height / 2)

                return (p_img)

            except AttributeError :
                # not found !
                return None

        def getImageFromZODB(self, name, owner) :
            """Retrieves an Image from a ZODB object
            """
            # AVS
            try :
                # try to get it from ZODB
                img_pointer = getattr(owner, name)
                image = PIL_Image.open(cStringIO.StringIO(str(img_pointer.data)))
                width = img_pointer.width
                height = img_pointer.height
                filename = img_pointer.filename
                suffix = filename.split('.')[-1]


                try:
                    tmp_img = file(tempfile.mktemp(suffix = suffix), 'w+b')
                    tmp_img.write(img_pointer.data)
                    tmp_img.close()
                except IOError:
                    return []
                p_img = platypus.Image(tmp_img.name, width = width / 2, height = height / 2)

                return (p_img)
                #return ((p_img, width, height))

            except AttributeError :
                # not found !
                return None
        def append(self, object) :
            """Appends an object to our platypus "story" (using ReportLab's terminology)."""
            self.objects.append(object)

    security.declarePublic('ar_results_pdf')
    def ar_results_pdf(self, info):

        settings = self.aq_parent.bika_setup
        max_batch = settings.getBatchEmail()


        laboratory = info['laboratory']
        lab_address = laboratory.getPostalAddress()
        if not lab_address:
            lab_address = laboratory.getBillingAddress()
        if not lab_address:
            lab_address = laboratory.getPhysicalAddress()

        contact = info['contact']
        client = contact.aq_parent
        contact_address = contact.getPostalAddress()
        if not contact_address:
            contact_address = client.getPostalAddress()
        if not contact_address:
            contact_address = client.getBillingAddress()
        if not contact_address:
            contact_address = contact.getPhysicalAddress()
        if not contact_address:
            contact_address = client.getPhysicalAddress()

        lab_accredited = laboratory.getLaboratoryAccredited()
        batch = info['analysis_requests']

        invoice_exclude = False
        out_of_range = []

        contact_stuff = contact.getFullname() + '\n' + client.Title()
        address = newline_to_br(contact_address.get('address', ''))
        contact_stuff = contact_stuff + '\n' + address
        location = contact_address.get('city', '')
        location = location + ', ' + contact_address.get('state', '')
        location = location + ', ' + contact_address.get('zip', '')
        location = location + ' ' + contact_address.get('country', '')
        contact_stuff = contact_stuff + '\n' + location

        lab_stuff = laboratory.Title()
        lab_title = laboratory.Title()
        address = newline_to_br(lab_address.get('address', ''))
        lab_stuff = lab_stuff + '\n' + address
        location = lab_address.get('city', '')
        location = location + ', ' + lab_address.get('state', '')
        location = location + ', ' + lab_address.get('zip', '')
        location = location + ' ' + lab_address.get('country', '')

        lab_stuff = lab_stuff + '\n' + location

        headings = []
        headings.append((contact_stuff, lab_stuff))

        all_first_heads = []
        all_other_heads = []
        all_results = []
        all_cats = []
        all_oor = []
        all_attachments = []
        all_remarks = []
        all_disclaimers = []
        all_ars = []
        all_dries = []
        ars = []
        managers = {}
        batch_cnt = 0
        for ar in info['analysis_requests']:
            responsible = ar.getManagers()
            for manager in responsible:
                if not managers.has_key(manager.getId()):
                    managers[manager.getId()] = manager
            if batch_cnt == max_batch:
                (first_heads, other_heads, results, cats, out_of_range, dries, attachments, remarks, disclaimers) = self.process_batch(ars, lab_accredited, lab_title)
                all_first_heads.append(first_heads)
                all_other_heads.append(other_heads)
                all_results.append(results)
                all_cats.append(cats)
                all_oor.append(out_of_range)
                all_ars.append(batch_cnt)
                all_dries.append(dries)
                all_attachments.append(attachments)
                all_remarks.append(remarks)
                all_disclaimers.append(disclaimers)
                ars = []
                batch_cnt = 0
            ars.append(ar)
            batch_cnt += 1

        if batch_cnt > 0:
            (first_heads, other_heads, results, cats, out_of_range, dries, attachments, remarks, disclaimers) = self.process_batch(ars, lab_accredited, lab_title)
            all_first_heads.append(first_heads)
            all_other_heads.append(other_heads)
            all_results.append(results)
            all_cats.append(cats)
            all_oor.append(out_of_range)
            all_attachments.append(attachments)
            all_remarks.append(remarks)
            all_disclaimers.append(disclaimers)
            all_ars.append(batch_cnt)
            all_dries.append(dries)

        all_managers = []
        m_keys = managers.keys()
        for m_key in m_keys:
            all_managers.append(managers[m_key])



        filename = "results.pdf"

        # tell the browser we send some PDF document
        # with the requested filename

        # get the document's content itself as a string of text
        file = self.MyPDFDoc(self, filename, headings, all_first_heads, all_other_heads, all_ars, all_results, all_cats, all_oor, all_dries, all_attachments, all_remarks, all_managers, all_disclaimers, lab_title)
        filecontent = file.report.getvalue()

        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename=%s' % filename)
        file_data = {}
        file_data['file'] = filecontent
        file_data['file_name'] = filename
        return file_data

    def process_batch(self, ars, lab_accredited, lab_title):
        service_info = self.get_services_from_requests(ars)
        services = service_info['Services']

        any_accredited = service_info['Accredited']
        accredited = lab_accredited and any_accredited

        plone_view = self.restrictedTraverse('@@plone')
        first_heads = []
        other_heads = []
        results = []
        oor = []
        dries = []
        cats = []
        first_heads.append(['Client Order', ])
        other_heads.append(['Client Order', ])
        first_heads.append(['Client Reference', ])
        other_heads.append(['Client Reference', ])
        first_heads.append(['Client SID', ])
        other_heads.append(['Client SID', ])
        first_heads.append(['Request ID', ])
        other_heads.append(['Request ID', ])
        first_heads.append(['Sample ID', ])
        first_heads.append(['Sample type', ])
        first_heads.append(['Sample point', ])
        first_heads.append(['Date Sampled', ])
        first_heads.append(['Date Received', ])
        first_heads.append(['Date Published', ])
        first_heads.append(['Verified by', ])
        first_heads.append(['Analysis results', ])
        other_heads.append(['Analysis results', ])
        categoryStyle = ParagraphStyle('BodyText',
                                  spaceBefore = 0,
                                  spaceAfter = 0,
                                  leading = 8,
                                  alignment = 0,
                                  fontName = 'Helvetica',
                                  fontSize = 10)
        serviceStyle = ParagraphStyle('BodyText',
                                  leftIndent = 6,
                                  spaceBefore = 0,
                                  spaceAfter = 0,
                                  leading = 8,
                                  alignment = 0,
                                  fontName = 'Helvetica',
                                  fontSize = 9)
        category = None
        for service in services:
            if service.getCategoryTitle() != category:
                category = service.getCategoryTitle()
                print_data = category
                print_data = print_data.replace('&', '&amp;')
                print_data = print_data.replace('<', '&lt;')
                print_data = print_data.replace('>', '&gt;')
                para = Paragraph(print_data, categoryStyle)
                cat_line = [para]
                for i in range(len(ars)):
                    cat_line.append('')
                    cat_line.append('')
                results.append(cat_line)
            print_data = service.Title()
            if service.getUnit():
                print_data = '%s %s' % (print_data, service.getUnit())
            if service.getAccredited():
                print_data = '%s *' % (print_data)
            print_data = print_data.replace('&', '&amp;')
            print_data = print_data.replace('<', '&lt;')
            print_data = print_data.replace('>', '&gt;')
            para = Paragraph(print_data, serviceStyle)
            results.append([para])

        ar_analyses = {}
        ar_sampletype = {}
        for ar in ars:
            ar_analyses[ar.getRequestID()] = self.group_analyses_by_service(ar.getPublishedAnalyses())
            ar_sampletype[ar.getRequestID()] = ar.getSample().getSampleType().UID()

        paraStyle = ParagraphStyle('BodyText',
                                  spaceBefore = 0,
                                  spaceAfter = 0,
                                  leading = 8,
                                  alignment = 1,
                                  fontName = 'Helvetica',
                                  fontSize = 9)
        """ attachments """
        attachments = [['Attachments', ''], ]
        for ar in ars:
            if ar.getAttachment():
                attachments.append([ar.getRequestID(), ])
                att = ''
                for attachment in ar.getAttachment():
                    file = attachment.getAttachmentFile()
                    filename = getattr(file, 'filename')
                    filesize = file.getSize()
                    filesize = filesize / 1024
                    att_type = attachment.getAttachmentType().Title()
                    mime_type = self.lookupMime(file.getContentType())
                    print_att = '%s %s %s - %sKb' % (filename, att_type, mime_type, filesize)
                    if att:
                        att = '%s%s' % (att, '\n')
                    att = att + print_att
                    para = Paragraph(att, paraStyle)
                attachments[-1].append(para)

            analyses = ar.getPublishedAnalyses()
            for analysis in analyses:
                if analysis.getAttachment():
                    text = '%s - %s' % (ar.getRequestID(), analysis.Title())
                    text = text.replace('&', '&amp;')
                    text = text.replace('<', '&lt;')
                    text = text.replace('>', '&gt;')
                    para = Paragraph(text, serviceStyle)
                    attachments.append([para, ])
                    att = ''
                    for attachment in analysis.getAttachment():
                        file = attachment.getAttachmentFile()
                        filename = getattr(file, 'filename')
                        filesize = file.getSize()
                        filesize = filesize / 1024
                        att_type = attachment.getAttachmentType().Title()
                        mime_type = self.lookupMime(file.getContentType())
                        print_att = '%s %s %s - %sKb' % (filename, att_type, mime_type, filesize)
                        if att:
                            att = '%s%s' % (att, '\n')
                        att = att + print_att
                        para = Paragraph(att, paraStyle)
                    attachments[-1].append(para)

        """ remarks """

        remarks = [['Remarks', ''], ]
        for ar in ars:
            if ar.getRemarks():
                para = Paragraph(ar.getRemarks(), paraStyle)
                remarks.append([ar.getRequestID(), para])
            else:
                remarks.append([ar.getRequestID(), 'None'])


        """ ars """
        any_oor = False
        ar_cnt = 0
        for ar in ars:
            sample = ar.getSample()
            requestID = ar.getRequestID()

            text = ar.getClientOrderNumber() and ar.getClientOrderNumber() or ''
            para = Paragraph(text, paraStyle)
            first_heads[0].extend([para, ''])
            other_heads[0].extend([para, ''])

            """ temporary fix for long client refs not splitting """
            this_text = sample.getClientReference() and sample.getClientReference() or ''
            max_len = 40
            if len(ars) > 3:
                max_len = 16
            elif len(ars) > 2:
                max_len = 20
            elif len(ars) > 1:
                max_len = 30
            if len(this_text) > max_len:
                new_text = ''
                texts = this_text.split()
                for text in texts:
                    if len(text) > max_len:
                        start = 0
                        end = 0
                        while end < len(text):
                            end = end + max_len
                            new_text = new_text + ' ' + text[start:end]
                            start = end
                    else:
                        new_text = new_text + ' ' + text
                this_text = new_text
            para = Paragraph(this_text, paraStyle)
            first_heads[1].extend([para, ''])
            other_heads[1].extend([para, ''])

            text = sample.getClientSampleID() and sample.getClientSampleID() or ''
            para = Paragraph(text, paraStyle)
            first_heads[2].extend([para, ''])
            other_heads[2].extend([para, ''])

            first_heads[3].extend([requestID, ''])
            other_heads[3].extend([requestID, ''])
            first_heads[4].extend([sample.getSampleID(), ''])

            text = sample.getSampleType() and sample.getSampleType().Title() or ''
            para = Paragraph(text, paraStyle)
            first_heads[5].extend([para, ''])

            text = sample.getSamplePoint() and sample.getSamplePoint().Title() or ''
            para = Paragraph(text, paraStyle)
            first_heads[6].extend([para, ''])

            if sample.getDateSampled():
                datesampled = plone_view.toLocalizedTime(sample.getDateSampled(), long_format = 1)
            else:
                datesampled = ' '
            para = Paragraph(datesampled, paraStyle)
            first_heads[7].extend([para, ''])

            datereceived = plone_view.toLocalizedTime(ar.getDateReceived(), long_format = 1)
            para = Paragraph(datereceived, paraStyle)
            first_heads[8].extend([para, ''])

            datepublished = plone_view.toLocalizedTime(ar.getDatePublished(), long_format = 1)
            para = Paragraph(datepublished, paraStyle)
            first_heads[9].extend([para, ''])

            first_heads[10].extend([self.get_analysisrequest_verifier(ar), ''])
            if ar.getReportDryMatter():
                dries.append(ar_cnt)
                first_heads[11].append('As Fed')
                first_heads[11].append('Dry')
                other_heads[4].append('As Fed')
                other_heads[4].append('Dry')
            else:
                first_heads[11].append('')
                first_heads[11].append('')
                other_heads[4].append('')
                other_heads[4].append('')
            line_cnt = 0

            category = None
            for service in services:
                if service.getCategoryTitle() != category:
                    category = service.getCategoryTitle()
                    cats.append(line_cnt)
                    line_cnt += 1
                service_id = service.getId()
                analysis_found = ar_analyses[requestID].has_key(service_id)
                if analysis_found:
                    analysis = ar_analyses[requestID].get(service_id, None)
                    result = analysis.getResult() or None
                    mou = analysis.getUncertainty() or None
                    result_class = self.XXXresult_in_range(analysis, ar_sampletype[requestID], 'client')
                    print_result = result
                    if result_class == 'out_of_range':
                        oor.append((ar_cnt, line_cnt))
                        any_oor = True
                        print_result = '%s !' % (print_result)
                    if mou:
                        print_result = '%s (+/- %s)' % (print_result, mou)
                    if analysis.getRetested():
                        print_result = '%s  %s' % (print_result, _('Retested'))
                    results[line_cnt].append(print_result)
                    if ar.getReportDryMatter():
                        if analysis.getResultDM():
                            results[line_cnt].append(analysis.getResultDM())
                        else:
                            results[line_cnt].append('')
                    else:
                        results[line_cnt].append('')
                else:
                    results[line_cnt].append('')
                    results[line_cnt].append('')

                line_cnt += 1
            ar_cnt += 1


        """ disclaimers """

        disclaimers = []
        if any_oor:
            disclaimers.append(['!   Result out of client specified range'])
        if accredited:
            disclaimers.append(['*   Methods included in the schedule of Accreditation for this Laboratory. Analysis remarks are not accredited'])
        disclaimers.append(['1.  Analysis results relate only to the samples tested'])
        disclaimers.append(['2.  This document shall not be reproduced except in full, without the written approval of %s' % lab_title])

        return (first_heads, other_heads, results, cats, oor, dries, attachments, remarks, disclaimers)


InitializeClass(bika_pdf_build)
