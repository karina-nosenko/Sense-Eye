import yaml
import subprocess
import subprocess
import os
# Read the configuration file
with open('configuration.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
# Run the Python server
# subprocess.Popen([config['python']['command'], config['python']['file_path'], str(config['python']['port'])])

# Set the working directory to the directory where the Node.js application is located
# os.chdir(config['node']['working_directory'])

# Run the Node.js server
# subprocess.run(["npm", "run", "dev"], shell=True)
print([config['node']['command'], config['node']['argument_1'], config['node']['argument_2']],config['node']['working_directory'])
subprocess.Popen([config['python']['command'], config['python']['file_name']],shell = True)
subprocess.Popen([config['node']['command'], config['node']['argument_1'], config['node']['argument_2']],cwd=config['node']['working_directory'],shell=True)
