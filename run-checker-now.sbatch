#!/bin/bash
#SBATCH --job-name=check_alex
#SBATCH --begin=now
#SBATCH --partition=rondror
#SBATCH --dependency=singleton
#SBATCH --time=00:30:00
#SBATCH --mail-type=FAIL
#SBATCH --output=/home/users/lxpowers/analyze_running/out/slurm-%j.out

## Insert command for checker.py, as we had in the original crontab before crons were disabled on sherlock

~/miniconda3/envs/conda2.7/bin/python analyze_jobs.py  
