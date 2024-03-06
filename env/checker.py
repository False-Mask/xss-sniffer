
def check():
    # check fuzzywyzzy
    try:
        import fuzzywuzzy
    except ImportError:
        print("fuzzywuzzy has not been installed..")
        quit()


