
import time

def get_time(seconds):
    try:
        seconds = int(seconds)
        minutes = seconds // 60
        seconds = seconds % 60
        return "{:02d}:{:02d}".format(minutes, seconds)
    except TypeError:
        pass


if __name__ == "__main__":
    get_time()