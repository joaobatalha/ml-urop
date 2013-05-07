from datetime import datetime, timedelta

def convert():
    seconds = float(raw_input("Time in seconds: "))
    time = datetime(1,1,1) + timedelta(seconds=seconds)
    print "game clock: %d:%d" % (time.minute, time.second)

if __name__ == "__main__":
    while(True):
        convert()
