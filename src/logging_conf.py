import logging

LEVEL = logging.INFO
FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
logging.basicConfig(level=LEVEL, format=FORMAT)
logger = logging.getLogger("au-sales-dashboard")
