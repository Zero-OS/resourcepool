import logging

class Utiles:
    def __init__(self):
        self.config = {}
        self.logging = logging
        self.log('api_testing/api_testing.log')

    def log(self, log_file_name='log.log'):
        log = self.logging.getLogger()
        fileHandler = self.logging.FileHandler(log_file_name)
        log.addHandler(fileHandler)
        self.logging.basicConfig(filename=log_file_name, filemode='rw', level=logging.INFO,
                                 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        '''
        How to use:
            self.logging.debug("This is a debug message")
            self.logging.info("Informational message")
            self.logging.error("An error has happened!")
        '''
