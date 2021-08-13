from django.core.management.base import BaseCommand, no_translations
from django.core.management import call_command
from django.conf import settings
import os
from datetime import datetime

class Command(BaseCommand):
    help="Make database dumps via docker postgres container"

    def add_arguments(self, parser):
        parser.add_argument('-d','--database', type=str, help="Database entry name in django settings")
        parser.add_argument('-p', '--prefix', type=str, help="Archive filename prefix")
        parser.add_argument('-o', '--outdir', type=str, help="Local directory to store the dump")
        parser.add_argument('-b', '--bucket', type=str, help="Spaces bucket to upload resulting file (local copy will be deleted)")

    def upload_and_remove(self, local_file, remote_path, bucket):
        call_command('spaces_upload', bucket=bucket,
                                      key=remote_path,
                                      filepath=local_file)
        print(f"Removing file {local_file}")
        os.unlink(local_file)
         
    @no_translations
    def handle(self, *args, **kwargs):
        dbconfig_name = kwargs.get('database') or 'default'
        output_dir    = kwargs.get('outdir') or ''
        archive_prefix = kwargs.get('prefix') or ''
        
        if not output_dir:
            output_dir=os.path.dirname(archive_prefix)
        if not output_dir:
            output_dir=os.getcwd()

        dbconfig = settings.DATABASES[dbconfig_name]
        clustername = dbconfig['HOST'].split('-')[0]
        outfile = '_'.join( [ p for p in 
                                [
                                    os.path.basename(archive_prefix), 
                                    clustername, 
                                    dbconfig['NAME'],
                                    datetime.now().strftime("%Y%m%d_%H%M%S")
                                ]
                                if p 
                             ]
                            )+".dump"

        
        os.environ["PGPASSWORD"]=dbconfig['PASSWORD']
        BACKUP_CMD=( f"docker run --network=host --rm -v {output_dir}:{output_dir} -w {output_dir} "
                "-e PGPASSWORD "
                "postgres:11 pg_dump -Fc -c --if-exists "
                f"-h {dbconfig['HOST']} "        
                f"-p {dbconfig['PORT']} "
                f"-U {dbconfig['USER']} "
                f"-d {dbconfig['NAME']} "
                f"-f {outfile}"
             )

        print(f"Starting backup of database {dbconfig_name} into local file {output_dir}/{outfile}")
        os.system(BACKUP_CMD)
        print(f"Completed backup of database {dbconfig_name} into local file {output_dir}/{outfile}")

        if kwargs.get('bucket'):
            bucket_path='/'.join( [ p for p in [
                                        os.path.dirname(archive_prefix),      
                                        os.path.basename(outfile)
                                    ] if p 
                                  ]  )

            local_path = '/'.join( [ output_dir, outfile ] )

            self.upload_and_remove(local_path, bucket_path, kwargs['bucket'])
