import os
import shlex
import signal


class Job:
    def __init__(self, pid, command):
        self.pid = pid
        self.command = command
        self.status = "Running"


jobs = {}
next_job_id = 1


def reap_jobs():
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            break

        if pid == 0:
            break

        for job in jobs.values():
            if job.pid == pid:
                if os.WIFSIGNALED(status):
                    job.status = "Terminated"
                else:
                    job.status = "Done"
                break


def show_jobs():
    for job_id, job in jobs.items():
        print(f"[{job_id}] {job.status} {job.command}")


def foreground(args):
    if len(args) != 2 or not args[1].isdigit():
        print("Usage: fg <job_id>")
        return

    job_id = int(args[1])
    job = jobs.get(job_id)

    if job is None:
        print("Job not found")
        return

    if job.status != "Running":
        print("Job is not running")
        return

    print(job.command)

    try:
        os.waitpid(job.pid, 0)
    except ChildProcessError:
        pass

    del jobs[job_id]


def kill_job(args):
    if len(args) != 2 or not args[1].isdigit():
        print("Usage: kill <job_id>")
        return

    job_id = int(args[1])
    job = jobs.get(job_id)

    if job is None:
        print("Job not found")
        return

    if job.status != "Running":
        print("Job is not running")
        return

    try:
        os.kill(job.pid, signal.SIGTERM)
        os.waitpid(job.pid, 0)
        print(f"[{job_id}] Terminated {job.command}")
        del jobs[job_id]
    except ProcessLookupError:
        reap_jobs()
    except ChildProcessError:
        reap_jobs()


def run_command(args, command, background):
    global next_job_id

    try:
        pid = os.fork()
    except OSError as error:
        print(f"Fork failed: {error}")
        return

    if pid == 0:
        try:
            os.execvp(args[0], args)
        except FileNotFoundError:
            print(f"myshell: {args[0]}: command not found",
                  flush=True)
        except OSError as error:
            print(f"myshell: {error}", flush=True)

        os._exit(1)

    else:
        if background:
            job_id = next_job_id
            next_job_id += 1

            jobs[job_id] = Job(pid, command)
            print(f"[{job_id}] {pid} {command}")
        else:
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass


def main():
    while True:
        reap_jobs()

        try:
            line = input("myshell> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        try:
            args = shlex.split(line)
        except ValueError as error:
            print(f"Parsing error: {error}")
            continue

        if not args:
            continue

        background = False

        if args[-1] == "&":
            background = True
            args.pop()

        if not args:
            continue

        command = " ".join(args)

        if args[0] == "exit":
            break

        elif args[0] == "cd":
            path = args[1] if len(args) > 1 else os.path.expanduser("~")
            try:
                os.chdir(path)
            except OSError as error:
                print(f"cd: {error}")

        elif args[0] == "jobs":
            show_jobs()

        elif args[0] == "fg":
            foreground(args)

        elif args[0] == "kill":
            kill_job(args)

        else:
            run_command(args, command, background)

    for job in jobs.values():
        if job.status == "Running":
            try:
                os.kill(job.pid, signal.SIGTERM)
                os.waitpid(job.pid, 0)
            except (ProcessLookupError, ChildProcessError):
                pass


if __name__ == "__main__":
    main()
