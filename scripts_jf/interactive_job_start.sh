#!/bin/bash
srun -p general -t 4:00:00 --mem-per-cpu 16G --nodes=1 --ntasks-per-node=4 --cpus-per-task=1 --pty /bin/bash
