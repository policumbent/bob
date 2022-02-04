import glob
import os

files = glob.glob('./modules/**/*.service')
files += glob.glob('./utility/*.service')
files += glob.glob('./ui/*.service')
dest = '/etc/systemd/system/'
bob_dir = os.getcwd()

for source_path in files:
    service_name = os.path.basename(source_path)
    # replace ${BOB_ROOT} in service_file with current_dir
    service_file = open(source_path, 'r')
    service_content = service_file.read()
    service_file.close()
    service_content = service_content.replace('${BOB_ROOT}', bob_dir)
    # write service_content in the destination file
    new_path = os.path.join(dest, service_name)
    service_file = open(new_path, 'w')
    service_file.write(service_content)
    service_file.close()
    os.system(f'systemctl enable {service_name}')

os.system('systemctl daemon-reload')

