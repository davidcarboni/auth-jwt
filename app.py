import os
import logging
from src.auth import app

debug = bool(os.getenv("FLASK_DEBUG"))
logging_level = logging.DEBUG if debug else logging.WARNING
logging.basicConfig(level=logging_level)
logging.getLogger(__name__).info("Debug is " + str(debug))

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=os.getenv("PORT", "5000"),
        debug=debug
    )
