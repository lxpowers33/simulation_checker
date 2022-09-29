# simulation_checker

Slurm job names for simulation needs to be in following format 
{project}\_{condition}\_v{version #}\_{rep #}

# Setup 
1. Clone the repository into your home directory. 

        cd ~
        git clone https://github.com/lxpowers33/simulation_checker.git
    
2. Add your simulation information to run_config.py file using the appropriate format. The run_config.py file contains a list of dictionaries. Just add a new dictionary on a new line:

        {'c':['MK6_WT'], 'max':1000, 'v':[1], 'r':[1,2,3,4,5,6], 'p':'GPR40', 'd': '/oak/stanford/groups/rondror/projects/MD_simulations/amber/GPR40/jpaggi'},

      Above 'MK6_W' is the condition name, '1' is the condition version, '1,2,3,4,5,6' are the rep directories, 'GPR40' is the project name used in your job names, '/oak/stanford/groups/rondror/projects/MD_simulations/amber/GPR40/jpaggi' is the directory containing the condition directory.

3. Then run sbatch run-checker.sbatch to start the recurring job:

        sbatch run-checker.sbatch
        
4. Jobs should start running in 8 hours. If you wish to start jobs immediatley: 

        sbatch run-checker-now.sbatch
        
5. As jobs run, the running time should be written to the log file called log_file.txt. 

