import os
import re
import subprocess
import time
from datetime import datetime
import signal
from contextlib import contextmanager
from run_config import run_config

class TimeoutException(Exception): pass


@contextmanager
def time_limit(seconds):
	def signal_handler(signum, frame):
		raise TimeoutException("Timed out!")

	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)


def process(item, maxt, log_file):
	'''
	take anything that isn't running and submit a sub
	take anything that is running with MPI error and cancel it, submit a new jobs
	'''
	print(item, maxt)
	core = item['name']+' '+item['time']+' '+item['status']
	if item['valid_time']:
		if float(item['time']) > maxt:
			 log(log_file, core + ' ' + ' over time limit' + '\n')
			 return
	#submit_job(item)
	if item['status'] == 'not running or pending':
		log(log_file, core + ' ' + 'submit' + '\n')
		submit_job(item)
		return
	if item['status'] == 'running MPI error':
		log(log_file, core + ' ' + 'cancel then submit' + '\n')
		cancel_job(item)
		submit_job(item)
		return
	if item['status'] == 'timeout on sim.log':
		log(log_file, core + ' ' + 'should investigate ' + item['path'] + '\n')

	log(log_file, core + ' ' + 'do nothing' + '\n')
	return


def log(log_file, item):
	if logging:
		with open(log_file, "a") as log_f:
			log_f.write(item)
	else:
		print(item)


def cancel_job(item):
	if not dry_run:
		os.system('scancel {}'.format(item['id']))


def submit_job(item):
	if not dry_run:
		os.chdir(item['rep_folder'])
		os.system('sbatch sim_mdstep.sbatch')
		os.chdir('/home/users/lxpowers/analyze_running')


def read_time(rep_folder):
	try:
		with time_limit(10):
			if not os.path.isfile(rep_folder + '/mdinfo'):
				return "0", False
			with open(rep_folder + '/mdinfo') as f:
				l = f.readline()
				l = f.readline().split(' ')
				l = [i for i in l if i != '']
				if (len(l) >= 6):
					return str(float(l[5]) / 1000), True
				else:
					return str(l), False
	except TimeoutException as e:
		return "timeout on mdinfo", False


def check_status(base_directory, project, conditions, versions, reps):
	all_jobs = get_jobs()
	results = []
	print(all_jobs)
	for c_name in sorted(conditions):
		for v in versions:
			for r in reps:
				rep_folder = base_directory + '/' + c_name + '/v' + str(v) + '/rep' + str(r)
				code = '{}_{}_v{}_{}'.format(project, c_name, v, r)
				running, job_id = is_running(code, all_jobs)
				time, valid_time  = read_time(rep_folder)
				status = 'Error'
				if running:
					try:
						with time_limit(10):
							f = rep_folder + '/sim.log'
							print(f)
							with open(f, 'r') as f:
								try:
									lines = f.readlines()
									lines = lines[-min(12, len(lines)):]
									if has_mpi_error(lines):  # MPI error
										status = 'running MPI error'
									else:
										status = 'running'
								except UnicodeDecodeError as e:
									 status = "running but decode error on sim.log"
					except TimeoutException as e:
						status = "timeout on sim.log"
				elif is_pending(code, all_jobs):
					status = 'pending'
				else:
					status = 'not running or pending'
				results.append({'name': code, 'id': job_id, 'rep_folder': rep_folder, 'status': status,
									'path': rep_folder + '/sim.log', 'time': time, 'valid_time':valid_time})
	return results


def has_mpi_error(lines):
	for l in lines:
		if 'MPI' in l:
			return True
	return False


def tail(f, n):
	stdin, stdout = os.popen2("tail -n " + str(n) + " " + f)
	stdin.close()
	lines = stdout.readlines()
	stdout.close()
	return lines

def is_pending(name, all_jobs):
	i = 0
	for job_item in all_jobs:
		if (job_item['name'] == name) and (job_item['status'] == 'PD'):
			i = i + 1
			if (i >= 2):
				return True
	return False

def is_running(name, all_jobs):
	for job_item in all_jobs:
		if (job_item['name'] == name) and (job_item['status'] == 'R'):
			return True, job_item['id']
	return False, None


def get_jobs():
	cmd = 'squeue -u $USER --format "%.18i %.9P %.j %.8u %.2t %.10M %.6D %R"'  # -t PENDING
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
	jobs = pipe.read().decode('utf-8')[:-1].split('\n')
	all_jobs = []
	for job_line in jobs:
		job_info = parse_slurm_job_line(job_line)
		all_jobs.append(job_info)
	return all_jobs


def parse_slurm_job_line(job_line):
	l = job_line.split(' ')
	l = [i for i in l if i != '']
	job_info = {}
	job_info['id'] = l[0]
	job_info['name'] = l[2]
	job_info['status'] = l[4]
	job_info['time'] = l[5]
	return job_info


def run_get_status():
	'''
	For each simulations, get status: not running, MPI error,
	'''
	log_file = "log_file.txt"
	log(log_file, ' Dry run: {}'.format(dry_run))
	log(log_file, datetime.now().strftime("%d/%m/%Y %H:%M:%S \n"))
	GPR40_active = '/oak/stanford/groups/rondror/users/lxpowers/simulations/GPR40/active'
	GPR40_ternary = '/oak/stanford/groups/rondror/users/lxpowers/simulations/GPR40/ternary'
	xan_dir_1 = '/oak/stanford/groups/rondror/users/lxpowers/simulations/Karuna'
	my_kix_dir = '/oak/stanford/groups/rondror/users/lxpowers/simulations/KIX'
	conditions = [{'c':['active_AP8_MK6'], 'v':[3], 'r':[1,2,3,4,5], 'p':'GPR40', 'd':GPR40_active},
		{'c':['active_apo'], 'v':[3], 'r':[1,2,3,4,5], 'p':'GPR40', 'd':GPR40_active},
		{'c':['active_AP8'], 'v':[1], 'r':[1,2,3,4,5], 'p':'GPR40', 'd':GPR40_active},
		{'c':['active_MK6'], 'v':[1], 'r':[1,2,3,4,5], 'p':'GPR40', 'd':GPR40_active},
		{'c':['LIN_MK6'], 'v':[1], 'r':[1,2,3], 'p':'GPR40', 'd':GPR40_ternary},
	{'c':['M1_xan_solution'], 'v':[2], 'r':[4], 'p':'Xan', 'd':xan_dir_1},
		{'c':['KIX_KID'], 'v':[1], 'r':[1,2,3], 'p':'KIX', 'd':my_kix_dir},
		{'c':['KIX_KID_trunc1'], 'v':[1], 'r':[1,2,3], 'p':'KIX', 'd':my_kix_dir},
		{'c':['KIX_KID_trunc2'], 'v':[1], 'r':[1,2,3], 'p':'KIX', 'd':my_kix_dir},
		{'c':['kix_kidmim1'], 'v':[1], 'r':[1,2,3], 'p':'KIX', 'd':my_kix_dir}
	]
	conditions = run_config #[conditions[9]]
	print(conditions)
	for i in conditions:
		if 'max' in i:
		   maxt = i['max']
		else:
		   maxt = 10000
		results = check_status(i['d'], i['p'], i['c'], i['v'], i['r'])
		for item in results:
			process(item, maxt, log_file)

logging = True
dry_run = False
if __name__ == "__main__":
	run_get_status()

