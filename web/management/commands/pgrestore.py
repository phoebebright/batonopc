from django.core.management.base import BaseCommand, no_translations
from django.core.management import call_command
from django.conf import settings
import os
from datetime import datetime

class Command(BaseCommand):
    help="Make database dumps via docker postgres container"

    def add_arguments(self, parser):
        parser.add_argument('-d','--database', type=str, help="Database entry name in django settings")
        parser.add_argument('-f', '--from', type=str, help="Archive filename")

    @no_translations
    def handle(self, *args, **kwargs):
        dbconfig_name = kwargs.get('database') or 'default'
        dumpfile      = kwargs.get('from') or ''
        
        dbconfig = settings.DATABASES[dbconfig_name]
        currentdir = os.getcwd()
        dirflags=f"-v {currentdir}:{currentdir} -w {currentdir} " 
        if dumpfile.startswith('/'):
            dumpfiledir=os.path.dirname(dumpfile)
            if (dumpfiledir!=currentdir) :
                dirflags=f"{dirflags} -v {dumpfiledir}:{dumpfiledir} "
       
        os.environ["PGPASSWORD"]=dbconfig['PASSWORD']
        RESTORE_CMD=( f"docker run --network=host --rm {dirflags} "
                "-e PGPASSWORD "
                "postgres:11 pg_restore -c -e --if-exists "
                f"-h {dbconfig['HOST']} "        
                f"-p {dbconfig['PORT']} "
                f"-U {dbconfig['USER']} "
                f"-d {dbconfig['NAME']} "
                f"{dumpfile}"
             )

        print(RESTORE_CMD)
        os.system(RESTORE_CMD)
