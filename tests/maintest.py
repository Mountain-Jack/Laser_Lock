import threading
import time

def main_loop():
    while True:
        print("Main loop running...")
        time.sleep(1)

def user_input():
    while True:
        user_command = input("Enter command: ")
        print(f"User entered: {user_command}")

if __name__ == "__main__":
    print("Starting main loop and user input threads...")
    main_thread = threading.Thread(target=main_loop)
    input_thread = threading.Thread(target=user_input)
    print("Threads started...")
    main_thread.start()
    input_thread.start()

    main_thread.join()
    input_thread.join()
    