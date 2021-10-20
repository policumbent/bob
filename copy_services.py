import glob
import os
import shutil

files = glob.glob('./**/*.service')
dest = '/etc/systemd/system/'

for file_path in files:
    service_name = os.path.basename(file_path)
    new_path = os.path.join(dest, service_name)
    shutil.copy(file_path, new_path)
    # os.system(f'systemctl enable {service_name}')

os.system('systemctl daemon-reload')

