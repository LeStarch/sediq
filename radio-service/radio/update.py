import sys
from .handler import IPC_FILE

def main():
    """ Main function, Hi Lewis!! """
    try:
        frequency = int(sys.argv[1])
        if frequency <= 108e6 and frequency >= 88e6:
            with open(IPC_FILE, "w") as file_handle:
                print(f"Setting to: {frequency}")
                print(f"{frequency}", file=file_handle)
                sys.exit(0)
        else:
            print(f"[ERROR] Frequency out of range [88 MHz-108 MHz]: {frequency}")
    except Exception as exc:
        print(f"[ERROR] Error setting frequency: {exc}")
    sys.exit(1)

if __name__ == "__main__":
    main()
