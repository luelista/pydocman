from django.core.management.base import BaseCommand, CommandError
from dropme.models import Clipboard, Document, DocumentTag, Tag
import MySQLdb

class Command(BaseCommand):
    help = 'Import data from mysql database'

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, dest='sql_host')
        parser.add_argument('--user', type=str, dest='user')
        parser.add_argument('--password', type=str, dest='passwd')
        parser.add_argument('--db', type=str, dest='sql_db')
        parser.add_argument('--user-id=ID', type=int, dest='user_id')
        parser.add_argument('--from-docman', action='store_true', dest='from_docman')
        parser.add_argument('--from-dropme', action='store_true', dest='from_dropme')

    def handle(self, *args, **options):
        self.acting_user_id = options['user_id']

        dbconn = MySQLdb.connect(host=options['sql_host'], user=options['user'], passwd=options['passwd'])
        dbconn.cursor().execute('USE `'+options['sql_db']+'`;')
        print('Connected to db ',dbconn)
        if options['from_docman']:
            self.import_from_docman(dbconn)
        elif options['from_dropme']:
            self.import_from_dropme(dbconn)
        else:
            print('Please specify --from-docman or --from-dropme parameter. ')
            print('Nothing to do, exiting.')

    def import_from_docman(self, dbconn):
        c = dbconn.cursor()
        c.execute("SELECT doc_name,doc_date,doc_mandant,title,import_filename,import_source,"
                  "description,tags,page_count,file_size,created_at,updated_at,deleted_at,id "
                  "FROM documents ORDER BY id")

        cb_gewerbe = Clipboard.objects.get(title='GEWERBE')
        cb_privat = Clipboard.objects.get(title='PRIVAT')

        for row in c:
            doc = Document()

            mandant = row[2]  # doc_mandant
            if mandant == 'GEWERBE':
                doc.clipboard = cb_gewerbe
            else:
                doc.clipboard = cb_privat

            doc.storage_path = row[0]  # doc_name
            doc.doc_date = row[1]  # doc_date

            doc.title = row[3]  # title
            doc.storage_filename = row[4]  # import_filename
            doc.source_name = row[5] #import_source
            doc.comment = row[6] #description
            doc.page_count = row[8] #page_count
            doc.filesize = row[9] #file_size
            doc.created_at = row[10] #created_at
            doc.updated_at = row[11] #updated_at
            doc.deleted_at = row[12] #deleted_at

            doc.url_filename = row[13]  # id

            doc.created_by_id = self.acting_user_id
            doc.updated_by_id = self.acting_user_id
            doc.filetype = "pdf"
            doc.subtype = ""


            doc.save()
            doc.set_tags(row[7]) #tags


    def import_from_dropme(self, dbconn):
        raise NotImplementedError
