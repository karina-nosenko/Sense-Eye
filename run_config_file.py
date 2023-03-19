import yaml
import subprocess
import subprocess
import os
import signal
# Read the configuration file
with open('configuration.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
# Run the Python server
# subprocess.Popen([config['python']['command'], config['python']['file_path'], str(config['python']['port'])])

# Set the working directory to the directory where the Node.js application is located
# os.chdir(config['node']['working_directory'])

# Run the Node.js server
# subprocess.run(["npm", "run", "dev"], shell=True)
# print([config['node']['command'], config['node']['argument_1'], config['node']['argument_2']],config['node']['working_directory'])

process1 = subprocess.Popen([config['python']['sudo_command'], config['python']['command'], config['python']['file_name']])
process2 = subprocess.Popen([config['node']['command'], config['node']['argument_1'], config['node']['argument_2']],cwd=config['node']['working_directory'])
# process3 = subprocess.Popen([config['video']['sudo_command'], config['video']['command'], config['video']['file_name']])

process1.communicate()
process2.communicate()
# process3.communicate()

process1.terminate()
process2.terminate()
# process3.terminate()

# pid1 = process1.pid
# pid2 = process2.pid
# pid3 = process3.pid

# os.kill(pid1, signal.SIGTERM)
# os.kill(pid2, signal.SIGTERM)
# os.kill(pid3, signal.SIGTERM)
