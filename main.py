from server import run
import logging
log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

logo = """
 ______               _____          __           __
/_  __/__ __ _  ___  / ___/__  ___  / /________  / /
 / / / -_)  ' \/ _ \/ /__/ _ \/ _ \/ __/ __/ _ \/ / 
/_/  \__/_/_/_/ .__/\___/\___/_//_/\__/_/  \___/_/  
             /_/                                    
"""

if __name__ == "__main__":
    print(logo)
    run()
