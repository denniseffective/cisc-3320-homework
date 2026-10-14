# CISC 3320 - Homework 3
## CPU Scheduling Simulator

**Student:** Dennis Rostov  
**Course:** CISC 3320 - Operating Systems  
**Professor:** Swann Thantsin  
**Assignment:** Homework 3

### Project Description

For this assignment, I am building a CPU scheduling simulator in Python. The purpose is to see how different scheduling algorithms decide which process gets the CPU and how that affects waiting time, turnaround time, and response time.

The simulator reads process information from a CSV file. Each process has an ID, arrival time, CPU burst time, and priority number.

The goal is to run the same workload through five scheduling algorithms and compare their results.

### Scheduling Algorithms

1. **First Come, First Served (FCFS):** Runs processes based on their arrival order. Once a process starts, it runs until completion.

2. **Shortest Job First (SJF):** Selects the process with the shortest CPU burst among the processes that have already arrived. This implementation is non-preemptive.

3. **Round Robin (RR):** Gives each process a maximum of 4 time units. If a process does not finish, it goes back into the ready queue.

4. **Priority Scheduling:** To be implemented. The plan is to use non-preemptive priority scheduling, where smaller priority numbers represent higher priority.

5. **Multi-Level Feedback Queue (MLFQ):** To be implemented using three queues with different time quantums.

### Process Information

The program uses a `SimProcess` class to store:

- Process ID
- Arrival time
- Burst time
- Remaining CPU time
- Priority
- First start time
- Completion time

### Scheduling Metrics

The simulator calculates three metrics:

**Turnaround Time = Completion Time - Arrival Time**

**Waiting Time = Turnaround Time - Burst Time**

**Response Time = First Start Time - Arrival Time**

Waiting time tells us how long a process spends waiting for the CPU. Turnaround time measures the total time from arrival to completion. Response time measures how long it takes for a process to receive the CPU for the first time.

### Workload Files

**sample.csv**

This file contains the four processes used in Lectures 5 and 6. I use it to check my calculations against the examples from class.

**custom.csv**

This file contains five processes with different arrival times, burst times, and priorities. It is used to test the simulator with another workload.

### Running the Program

The completed program will be run using Python 3 from the terminal.

Example commands:

`python simulator.py --workload sample.csv --algo fcfs`

`python simulator.py --workload sample.csv --algo rr`

`python simulator.py --workload sample.csv --compare`

These commands will work after the command-line interface and remaining algorithms are added.

### Testing

The sample workload from Lecture 5 gives the following expected average waiting times:

- FCFS: 7.50
- SJF: 4.50
- Round Robin (quantum = 4): 8.50

I will compare the simulator's results against these values to check that the scheduling and metric calculations are correct.

### Current Progress

The process class, CSV reader, FCFS, SJF, Round Robin, and metric calculation function have been implemented.

The remaining tasks are to implement Priority Scheduling and MLFQ, add the command-line interface, test the complete simulator, and write the final comparison report.