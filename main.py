from internal.app import JiraTUI
import logging

logging.basicConfig(filename="app.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    JiraTUI().run()
