#!/bin/bash
#SBATCH --job-name=checker_now
#SBATCH --begin=now
#SBATCH --partition=rondror
#SBATCH --dependency=singleton
#SBATCH --time=00:20:00

ml load python/3.6.1
python3 analyze_jobs.py   
