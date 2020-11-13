#!/bin/bash
#SBATCH --job-name=check_alex
#SBATCH --begin=now+30minutes
#SBATCH --partition=rondror
#SBATCH --dependency=singleton
#SBATCH --time=00:20:00
#SBATCH --mail-type=FAIL
#SBATCH --output=/home/users/lxpowers/analyze_running/out/slurm-%j.out

## Insert command for checker.py, as we had in the original crontab before crons were disabled on sherlock

sbatch $0
~/miniconda3/bin/python3.4 analyze_jobs.py  
