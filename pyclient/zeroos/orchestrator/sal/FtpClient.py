from ftplib import FTP
from urllib.parse import urlparse
from io import BytesIO


class FtpClient:
    def __init__(self, url):
        self.parsed_url = urlparse(url)

    def upload(self, content, filename):
        with FTP() as ftp:

            port = self.parsed_url.port or 21
            ftp.connect(self.parsed_url.hostname, port=port)
            ftp.login(user=self.parsed_url.username, passwd=self.parsed_url.password)
            if self.parsed_url.path:
                ftp.cwd(self.parsed_url.path)
            bytes = BytesIO(content)
            ftp.storbinary('STOR ' + filename, bytes)

    def download(self, content, filename):
        with FTP() as ftp:
            port = self.parsed_url.port or 21
            ftp.connect(self.parsed_url.hostname, port=port)
            ftp.login(user=self.parsed_url.username, passwd=self.parsed_url.password)
            buff = BytesIO()
            ftp.retrbinary('RETR ' + self.parsed_url.path, buff.write)
            return buff.getvalue().decode()
