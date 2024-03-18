
def check():
    # check fuzzywyzzy
    try:
        import fuzzywuzzy
    except ImportError:
        print("fuzzywuzzy has not been installed..")
        quit()

    # check selenium
    try:
        import selenium
    except ImportError:
        print("selenium has not been installed..")
        quit()

    # request
    try:
        import requests
    except ImportError:
        print("requests has not been installed..")
        quit()

    # beautifulsoup4
    try:
        import bs4
    except ImportError:
        print("beautifulsoup4 has not been installed..")
        quit()

