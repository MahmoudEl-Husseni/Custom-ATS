import PyPDF2

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


import io
import os

class PDFReader :

    def __init__(self, path : str = None, drive_id : str = None, ) -> None:
        self.path = path
        self.drive_id = drive_id

        # set up the Google Drive API
        SCOPES = ['https://www.googleapis.com/auth/drive']
        SERVICE_ACCOUNT_FILE = 'secrets/service_account.json'
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )

        self.service = build('drive', 'v3', credentials=self.credentials)
        self.fh = io.BytesIO()



    def read_pdf_text(self, path : str = None ) -> str:
        '''
        Read the text from a pdf file

        Args:
        path : str : path to the pdf file
        '''

        path = path if path else self.path
        
        with open(path, 'rb') as f : 
            pdf = PyPDF2.PdfReader(f)
            text = "".join([page.extract_text() for page in pdf.pages])
            return text


    def extract_data_from_pdf_id(self, file_id : str = None) -> str:
        '''
        
        Extract text from a pdf file in Google Drive
        '''
        file_id = file_id if file_id else self.drive_id

        # Download the PDF file
        request = self.service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(self.fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
        self.fh.seek(0)

        # Save the PDF to a file
        with open('downloaded_file.pdf', 'wb') as f:
            f.write(self.fh.read())

        text = self.read_pdf_text('downloaded_file.pdf')

        # remove the downloaded file
        os.remove('downloaded_file.pdf')

        return text