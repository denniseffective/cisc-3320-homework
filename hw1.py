import os


def main():
    # Print the process ID and parent process ID
    print("PID:", os.getpid())
    print("PPID:", os.getppid())

    # List the environment variables
    print("\nEnvironment Variables:")
    for key, value in os.environ.items():
        print(f"{key}={value}")

    # List the open file descriptors for this process
    print("\nOpen File Descriptors:")
    try:
        for fd in os.listdir("/proc/self/fd"):
            print(fd)
    except OSError as error:
        print("Error reading /proc/self/fd:", error)


if __name__ == "__main__":
    main()
