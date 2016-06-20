from subprocess import check_call, check_output

import re

import os
import dropme.models


class DocInfo:
    def __init__(self, doc: "dropme.models.Document"):
        self.doc = doc

    def prepare_preview(self):
        self.doc.page_count = self.get_page_count()
        self.doc.filesize = os.path.getsize(self.doc.get_main_filespec())
        self.doc.save()

    def get_page_count(self):
        return 1


class PdfDocInfo(DocInfo):
    def prepare_preview(self):
        super().prepare_preview()
        src = self.doc.get_main_filespec()
        tmp = self.doc.get_path() + 'tmp%d.jpg'

        # generate jpg file named _tmpX.jpg for each page of the PDF
        check_call(['gs', '-dBATCH', '-dNOPAUSE', '-dQUIET', '-sDEVICE=jpeg', '-sOutputFile='+tmp, '-r144', src])

        # iterate over pages ...
        for pag in range(1, self.doc.page_count):
            # generate page preview (max. 800x800 pixel)
            check_call(['convert', tmp % (pag,), "-quality", "70", "-resize", "800x800^",
                        "-trim", "-fuzz", "70%", "+repage",
                        self.doc.get_page_preview_filespec(pag)])

            # generate page thumbnail (cropped to 150x150 pixel)
            check_call(['convert', tmp % (pag,), "-resize", "150x150^", "-crop", "150x150+0+0", "-trim", "-fuzz", "70%",
                        self.doc.get_thumb_filespec(pag)])

            # remove temp jpg file
            os.remove(tmp % (pag,))


    def get_page_count(self):
        output = check_output(['pdfinfo', self.doc.get_main_filespec()])
        match = re.search(r'Pages:\s*(\d+)', output)
        return int(match.group(1))


class ImageDocInfo(DocInfo):
    def prepare_preview(self):
        super().prepare_preview()
        pass

    def get_page_count(self):
        if self.doc.subtype == "tiff":
            return 42
        else:
            return 1


