# %%
# !pip install fabric

# %%
from fabric import SerialGroup, ThreadingGroup, Group
import threading
from queue import Queue
global_res = Queue(maxsize=0)

# %%
# tools = ['sfuzz','smartfuzz', 'ilf', 'confuzzius', 'smartian']
# tool = 'smartian'
# tool_id = tools.index(tool)
import numpy as np

def split_contract_list(contract_list_path, num_workers=10):
    with open(contract_list_path, 'r') as f:
        contract_list = f.readlines()
    total_len = len(contract_list)
    task_list = np.array_split(contract_list, num_workers)
    all_parts_list = []
    for i in range(len(task_list)):
        # print (task_list[i])
        with open(f'{contract_list_path}_part{i}', 'w') as f:
            f.writelines(task_list[i])
        all_parts_list.append(f'{contract_list_path}_part{i}')
    return all_parts_list

all_parts_list = split_contract_list('file_list/solidifi/solidifi_smartian_format_solc.txt', num_workers=10)

# %%
# worker_list = list(range(10,60))#[::5]
# tools = ['sfuzz','smartfuzz', 'ilf', 'confuzzius', 'smartian']
# tools = ['mythril','smartfuzz','sfuzz', 'ilf', 'smartian','confuzzius']
tools = ['smartfuzz','mythril','sfuzz', 'ilf', 'smartian','confuzzius']
worker_list = list(range(1,61))#list(range(11,21))
host_list = [f'worker-{idx:03d}' for idx in worker_list]
num_workers = 10
print (worker_list)
print (host_list)
worker_params = {}
for idx, worker_id in enumerate(worker_list):
    # print (idx//num_workers)
    # print (worker_id, num_workers)
    worker_params[f'worker-{worker_id:03d}'] = { 'tool': tools[(worker_id-1)//num_workers],
                            'file': all_parts_list[(worker_id-1)%num_workers]
                          }
from pprint import pprint
pprint (worker_params)

# %%

from paramiko.client import SSHClient
import paramiko
import threading
# exit(0) #checkpoint
MAX_JOBS = 20
TIME_OUT = 3600
benchmark_path = 'benchmarks/smartbench-dataset/solidity/solidifi++/'
part_file_prefix = '/users/minh/github/smartbench-runner/'
extra_args = ""
# result_dir = "/users/minh/github/smartbench-results/ase-23/B3_run3_test_1min"
result_dir_1 = "results/solidifipp_final/run1"
result_dir_2 = "results/solidifipp_final/run2"
result_dir_3 = "results/solidifipp_final/run3"

tool_timeout = TIME_OUT*4
# new_host_list = host_list
def run_analysis_list(host):
    print ("running on {}".format(host))
    parts_file = worker_params.get(host).get('file')
    tool_name = worker_params.get(host).get('tool')
    smart_bench_run_1 = f"./smartbench.sh analyze -t {tool_name} --benchmark-dir {benchmark_path} --timeout {TIME_OUT} --jobs {MAX_JOBS} " + \
                f"--test-config-file {part_file_prefix+parts_file} {extra_args} --result-dir {result_dir_1} --only-create-containers --install-remote-docker"
    smart_bench_run_2 = f"./smartbench.sh analyze -t {tool_name} --benchmark-dir {benchmark_path} --timeout {TIME_OUT} --jobs {MAX_JOBS} " + \
                f"--test-config-file {part_file_prefix+parts_file} {extra_args} --result-dir {result_dir_2} --only-create-containers --install-remote-docker"
    smart_bench_run_3 = f"./smartbench.sh analyze -t {tool_name} --benchmark-dir {benchmark_path} --timeout {TIME_OUT} --jobs {MAX_JOBS} " + \
                f"--test-config-file {part_file_prefix+parts_file} {extra_args} --result-dir {result_dir_3} --only-create-containers --install-remote-docker"
    command = f"cd /data/minh/smartbench-runner ; {smart_bench_run_1}; {smart_bench_run_2} ; {smart_bench_run_3}"
    # command = f"cd /data/minh/smartbench-runner ; {smart_bench_run_3}"
    # command = f"source ~/miniconda3/bin/activate py39-smartbench && cd ~/github/smartbench-runner/ && ./smartbench.sh analyze -t {tool_name} " + \
    #             f"-f {benchmark_path} --timeout {TIME_OUT} --jobs {MAX_JOBS} " + \
    #             f"--target-contracts-file {parts_file} {extra_args} --result-dir {result_dir} --create-docker-container"
    print (f"{host} : {command}")
    # res = c.run(command, disown=True)
    # print (res)
    # retu  rn
    # return res
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
    client.connect(host)
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    for line in stdout.readlines():
        print (host, line)
    for line in stderr.readlines():
        print (host, line)
    return
# group = Group(*new_host_list)
threads = list()
for index in range(len(host_list)):
    # run_analysis_list(group[index], 'smartian')
    x = threading.Thread(target=run_analysis_list, args=(host_list[index], ))
    threads.append(x)
    x.start()
print ("before join")
for index, thread in enumerate(threads):
    thread.join()
print ("done")
