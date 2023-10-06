import sys
from .handler import send_new_frequency

def main():
    """ Main function, Hi Lewis!! """
    try:
        frequency = int(sys.argv[1])
        send_new_frequency(frequency)
    except:
        print(f"[ERROR] Invalid frequency")
        raise

if __name__ == "__main__":
    main()
