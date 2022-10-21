####################################################################################################

from DatasheetExtractor import setup_logging
setup_logging()

import logging
logging.info('Start ...')

####################################################################################################

from DatasheetExtractor.frontend.QmlApplication import Application

####################################################################################################

# application = Application()
Application.setup_gui_application()
application = Application.create()
application.exec_()
