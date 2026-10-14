# CISC 3320 - Homework 2
## Job Control Shell

Name: Dennis Rostov
Course: CISC 3320 - Operating Systems

### Description
For this homework, I created a basic shell using Python.
The shell can run Linux commands, start background jobs,
display running jobs, bring jobs to the foreground,
and terminate jobs.

### Features
- Background jobs using &
- List jobs using jobs
- Foreground execution using fg
- Terminate jobs using kill
- Automatically reap completed processes
- Support cd and exit
- Handle invalid commands

### How to Run
Open a Linux terminal and enter:

python3 myshell.py

### Commands to Test
sleep 5 &
jobs
sleep 30 &
fg 2
sleep 30 &
kill 3
jobs
exit

### Implementation
I used os.fork() to create child processes and
os.execvp() to execute Linux commands.

Foreground processes use os.waitpid() to wait until
the process finishes. Background processes are
checked using os.waitpid() with os.WNOHANG so
the shell does not block.

I also used a dictionary to store each job's
process ID, command, and status.
