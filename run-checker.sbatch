#!/bin/bash
#SBATCH --job-name=sim_checker
#SBATCH --begin=now+8hours
#SBATCH --partition=rondror
#SBATCH --dependency=singleton
#SBATCH --time=00:20:00
#SBATCH --mail-type=FAIL


sbatch $0
ml load python/3.6.1
python3 analyze_jobs.py  
