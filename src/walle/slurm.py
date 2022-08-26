import itertools
from simple_slurm import Slurm  # https://pypi.org/project/simple-slurm/
from collections import OrderedDict
import shutil
import yaml

#%%

# There was some issue finding the GPUs, if it comes back up, try loading these modules
#module load GCC
#module load CUDA/11.4.1
#module load cuDNN

def run_slurm_sweep(execution_file = 'train.py ',
                    submission_name = 'sweep',
                    sweep_file = 'sweep_cfg.yaml',
                    exp_name = 'junk',
                    exp_dir = 'logs/{exp_name}',
                    use_array = True,
                    n_max_active_jobs = 40
                    ):

    move_dir = f'{exp_dir}/$SLURM_JOB_ID/',
    # puts the output files neatly. Trailing / ensures has defined directory
    move_command = f'mv out/o-$SLURM_JOB_ID.out out/e-$SLURM_JOB_ID.err {move_dir}',

    with open(sweep_file) as f:
        sweep_cfg = OrderedDict(yaml.safe_load(f, Loader=yaml.FullLoader))

    assert sweep_cfg.keys()[-1] == 'seed'

    exps = list(itertools.product(*sweep_cfg.values))  # list of tuples
    [exp.insert(0, exp_name) for exp in exps]
    n_exps = len(exps)

    submission_cmds = []
    for i in range(n_exps):

        cur_function = f'python {execution_file} '
        for j, key in enumerate(sweep_cfg.keys):
            cur_function += '--' + key + ' ' + str(exps[i][j]) + ' '

        submission_cmds.append(cur_function)
        
        if not use_array:
            slurm = Slurm(
                mail_type='FAIL',
                partition='sm3090',
                N=1,  # n_node
                n=8,  # n_cpu
                time='0-00:15:00',
                output='out/o-%j.out',
                error='out/e-%j.err',
                gres='gpu:RTX3090:1',
                job_name=submission_name
            )
            # print(slurm)

            slurm.sbatch(f'module purge \n \
                        source ~/.bashrc \n \
                        conda activate sparkle \n \
                        pwd \n \
                        nvidia-smi \n \
                        mkdir -p {move_dir} \n \
                        {cur_function} > {move_dir}/py.out 2> {move_dir}/py.err \n \
                        {move_command}'                      
                        )

    if use_array:
        # creates a file of experiments
        def write_exps_list(submission_cmds):
            with open(r'./exps.tmp', 'w') as fp:
                fp.write(' \n'.join(submission_cmds))
            return 

        write_exps_list(submission_cmds)

        slurm = Slurm(
                mail_type='FAIL',
                partition='sm3090',
                N=1,  # n_node
                n=8,  # n_cpu
                time='0-00:15:00',
                output='out/o-%j.out',
                error='out/e-%j.err',
                gres='gpu:RTX3090:1',
                array=f'0-{n_exps-1}%{n_max_active_jobs}',  # https://help.rc.ufl.edu/doc/SLURM_Job_Arrays %5 for max 5 jobs at a time
                job_name=submission_name
            )

        print(slurm)

        '''
        put the exp file into array
        remove other modules
        get conda paths and cuda / cudnn (if gpu disappears)
        activate the conda env
        print the working dir
        make the output dirs
        run the cmd
        move outputs to output dir
        double curly braces in the f-string prints a curly brace
        '''
        slurm.sbatch(f'mapfile -t myArray < exps.tmp \n \
                    module purge \n \
                    source ~/.bashrc \n \
                    conda activate sparkle \n \
                    pwd \n \
                    nvidia-smi \n \
                    mkdir -p {move_dir} \n \
                    ${{myArray[$SLURM_ARRAY_TASK_ID]}} > {move_dir}/py.out 2> {move_dir}/py.err \n \
                    {move_command}'
                    )

    shutil.copyfile(sweep_file, f'{exp_dir}/{sweep_file}')






