
import csv
import argparse
from collections import deque
from copy import deepcopy


class SimProcess:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.start_time = None
        self.completion_time = None


def read_workload(filename):
    processes = []

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            process = SimProcess(
                row["pid"],
                int(row["arrival"]),
                int(row["burst"]),
                int(row["priority"])
            )
            processes.append(process)

    return processes

    
def fcfs_schedule(processes, quantum=None):
    timeline = []
    time = 0

    for p in sorted(processes, key=lambda p: p.arrival_time):
        time = max(time, p.arrival_time)

        p.start_time = time
        time += p.burst_time
        p.completion_time = time
        p.remaining_time = 0

        timeline.append((p.pid, p.start_time, time))

    return timeline


def sjf_schedule(processes, quantum=None):
    timeline = []
    time = 0
    completed = set()

    while len(completed) < len(processes):
        ready = [
            p for p in processes
            if p.arrival_time <= time and p.pid not in completed
        ]

        if not ready:
            time = min(
                p.arrival_time for p in processes
                if p.pid not in completed
            )
            continue

        p = min(ready, key=lambda p: (p.burst_time, p.arrival_time))

        p.start_time = time
        time += p.burst_time
        p.completion_time = time
        p.remaining_time = 0

        timeline.append((p.pid, p.start_time, time))
        completed.add(p.pid)

    return timeline

def calculate_metrics(processes):
    results = []

    for p in processes:
        turnaround = p.completion_time - p.arrival_time
        waiting = turnaround - p.burst_time
        response = p.start_time - p.arrival_time

        results.append({
            "pid": p.pid,
            "arrival": p.arrival_time,
            "burst": p.burst_time,
            "start": p.start_time,
            "completion": p.completion_time,
            "waiting": waiting,
            "turnaround": turnaround,
            "response": response
        })

    return results



def round_robin_schedule(processes, quantum=4):
    timeline = []
    time = 0
    ready = deque()
    incoming = sorted(processes, key=lambda p: p.arrival_time)
    index = 0
    completed = 0

    while completed < len(processes):
        while index < len(incoming) and incoming[index].arrival_time <= time:
            ready.append(incoming[index])
            index += 1

        if not ready:
            time = incoming[index].arrival_time
            continue

        p = ready.popleft()

        if p.start_time is None:
            p.start_time = time

        start = time
        run_time = min(quantum, p.remaining_time)

        time += run_time
        p.remaining_time -= run_time
        timeline.append((p.pid, start, time))

        while index < len(incoming) and incoming[index].arrival_time <= time:
            ready.append(incoming[index])
            index += 1

        if p.remaining_time == 0:
            p.completion_time = time
            completed += 1
        else:
            ready.append(p)

    return timeline

def priority_schedule(processes, quantum=None):
    timeline = []
    time = 0
    completed = set()

    while len(completed) < len(processes):
        ready = [
            p for p in processes
            if p.arrival_time <= time and p.pid not in completed
        ]

        if not ready:
            time = min(
                p.arrival_time for p in processes
                if p.pid not in completed
            )
            continue

        # Lower number means higher priority.
        # Ties use arrival time, then input order.
        p = min(ready, key=lambda p: (p.priority, p.arrival_time))

        p.start_time = time
        time += p.burst_time
        p.remaining_time = 0
        p.completion_time = time

        timeline.append((p.pid, p.start_time, time))
        completed.add(p.pid)

    return timeline



def mlfq_schedule(processes, quantum=None):
    quantums = [4, 8, 16]
    queues = [deque(), deque(), deque()]
    incoming = sorted(processes, key=lambda p: p.arrival_time)

    timeline = []
    time = 0
    index = 0
    completed = 0
    current = None
    current_level = 0
    slice_used = 0

    while completed < len(processes):
        # Periodically move waiting processes to the top queue.
        if time > 0 and time % 50 == 0:
            if current is not None:
                queues[0].append(current)
                current = None

            waiting = []
            for q in queues:
                while q:
                    waiting.append(q.popleft())

            for p in waiting:
                p.mlfq_level = 0
                p.slice_used = 0
                queues[0].append(p)

        # Add newly arrived processes.
        while index < len(incoming) and incoming[index].arrival_time <= time:
            p = incoming[index]
            p.mlfq_level = 0
            p.slice_used = 0
            queues[0].append(p)
            index += 1

        # Preempt if a higher-priority queue has work.
        if current is not None:
            if any(queues[level] for level in range(current_level)):
                current.slice_used = slice_used
                queues[current_level].appendleft(current)
                current = None

        # Choose the next process.
        if current is None:
            for level in range(3):
                if queues[level]:
                    current = queues[level].popleft()
                    current_level = level
                    slice_used = current.slice_used
                    break

        if current is None:
            time += 1
            continue

        if current.start_time is None:
            current.start_time = time

        # Execute one unit of CPU time.
        start = time
        time += 1
        current.remaining_time -= 1
        slice_used += 1

        if timeline and timeline[-1][0] == current.pid and timeline[-1][2] == start:
            timeline[-1] = (current.pid, timeline[-1][1], time)
        else:
            timeline.append((current.pid, start, time))

        if current.remaining_time == 0:
            current.completion_time = time
            completed += 1
            current = None
            slice_used = 0

        elif slice_used == quantums[current_level]:
            # Use up a full quantum, then move down.
            next_level = min(current_level + 1, 2)
            current.mlfq_level = next_level
            current.slice_used = 0
            queues[next_level].append(current)

            current = None
            slice_used = 0

    return timeline



def run_algorithm(processes, algo, quantum=4):
    # Each algorithm needs its own copy of the processes.
    jobs = deepcopy(processes)

    algorithms = {
        "fcfs": fcfs_schedule,
        "sjf": sjf_schedule,
        "rr": round_robin_schedule,
        "priority": priority_schedule,
        "mlfq": mlfq_schedule
    }

    if algo == "rr":
        timeline = algorithms[algo](jobs, quantum)
    else:
        timeline = algorithms[algo](jobs)

    results = calculate_metrics(jobs)

    n = len(results)
    averages = {
        "waiting": sum(p["waiting"] for p in results) / n,
        "turnaround": sum(p["turnaround"] for p in results) / n,
        "response": sum(p["response"] for p in results) / n
    }

    return timeline, results, averages


def print_results(algo, timeline, results, averages):
    print("\nAlgorithm:", algo.upper())

    print("\nGantt Timeline:")
    for pid, start, end in timeline:
        print(f"{start} -- {pid} -- {end}")

    print("\nProcess Metrics:")
    print(f"{'PID':<8}{'Waiting':<12}{'Turnaround':<14}{'Response':<12}")

    for p in results:
        print(
            f"{p['pid']:<8}"
            f"{p['waiting']:<12}"
            f"{p['turnaround']:<14}"
            f"{p['response']:<12}"
        )

    print("\nAverage Waiting Time:", f"{averages['waiting']:.2f}")
    print("Average Turnaround Time:", f"{averages['turnaround']:.2f}")
    print("Average Response Time:", f"{averages['response']:.2f}")


def compare_algorithms(processes, quantum=4):
    names = ["fcfs", "sjf", "rr", "priority", "mlfq"]

    print("\nCPU Scheduling Comparison")
    print(f"{'Algorithm':<15}{'Waiting':<14}{'Turnaround':<16}{'Response':<12}")
    print("-" * 57)

    for name in names:
        timeline, results, averages = run_algorithm(
            processes, name, quantum
        )

        print(
            f"{name.upper():<15}"
            f"{averages['waiting']:<14.2f}"
            f"{averages['turnaround']:<16.2f}"
            f"{averages['response']:<12.2f}"
        )



def main():
    parser = argparse.ArgumentParser(
        description="CISC 3320 CPU Scheduling Simulator"
    )

    parser.add_argument(
        "--workload",
        required=True,
        help="CSV file containing the processes"
    )

    parser.add_argument(
        "--algo",
        choices=["fcfs", "sjf", "rr", "priority", "mlfq"],
        help="Scheduling algorithm to run"
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare all five algorithms"
    )

    parser.add_argument(
        "--quantum",
        type=int,
        default=4,
        help="Round Robin time quantum (default: 4)"
    )

    args = parser.parse_args()

    if args.quantum <= 0:
        parser.error("Quantum must be greater than zero.")

    if not args.algo and not args.compare:
        parser.error("Choose --algo or --compare.")

    processes = read_workload(args.workload)

    if not processes:
        parser.error("The workload file is empty.")

    if args.compare:
        compare_algorithms(processes, args.quantum)
    else:
        timeline, results, averages = run_algorithm(
            processes, args.algo, args.quantum
        )
        print_results(args.algo, timeline, results, averages)


if __name__ == "__main__":
    main()
