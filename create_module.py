from os import makedirs, listdir, system
from os.path import isfile, isdir, join
from shutil import copyfile

module_types = ('Sensore', 'Consumatore', 'Remoto')
module_name = input('Nome modulo: ')
print('Tipologia modulo: ')
print('1) Sensore')
print('2) Consumatore')
print('3) Remoto')
module_type = int(input('Inserire numero: '))
if module_type > 3 or module_type < 1:
    print('Valore non accettabile')
    exit()
signals_list = input('Quali sono i segnali accettati? (Seprarare le parole con virgola, per esempio "reset, stop"): ')
topics_list = '[]'
if module_type != 1:
    topics_list = input('Quali sono i moduli che deve ascoltare?'
                         ' (Seprarare le parole con virgola, per esempio "manager, ant, gps"): ')
print('- - - - - - - - - - - - -')
module_name = module_name.replace(' ', '_')
print('Nome modulo: ', module_name)
print('Tipologia modulo: ', module_types[module_type])
signals_list = signals_list.replace(' ', '')
signals_list = signals_list.split(',')
print('Segnali accettati: ', signals_list)
if module_type != 1:
    topics_list = topics_list.replace(' ', '')
    topics_list = topics_list.split(',')
    print('Sensori da ascoltare: ', topics_list)
confirm = input('Vuoi confermare? (Y/n) ')
if confirm != 'Y' and confirm != 'y':
    print('Operazione annullata')
    exit()
makedirs(f'./{module_name}/src/common_files', exist_ok=True)
copyfile('./example_module/Dockerfile', f'./{module_name}/Dockerfile')
files = [f for f in listdir('./example_module/src') if isfile(join('./example_module/src', f))]
for file in files:
    file_dest = join(f'./{module_name}/src', file)
    file_src = join('./example_module/src', file)
    copyfile(file_src, file_dest)
files = [f for f in listdir('./common_files') if isfile(join('./common_files', f))]
for file in files:
    file_dest = join(f'./{module_name}/src/common_files', file)
    file_src = join('./common_files', file)
    copyfile(file_src, file_dest)
# signals_list = ['reset']
# module_type = 2
# module_name = 'pippo'
# topics_list = ['manager', 'gps']
with open('./example_module/src/main.py') as f:
    main = ''.join(f.readlines())
    # print(main)
    message_handler = ''
    if module_type == 1:
        mqtt_init = f"mqtt = MqttSensor(sys.argv[1], 1883, '{module_name}'," \
                    f" {str(signals_list)}, settings, message_handler)"
    elif module_type == 2:
        main = main.replace('MqttSensor', 'MqttConsumer')
        mqtt_init = f"mqtt = MqttConsumer(sys.argv[1], 1883, '{module_name}', {str(topics_list)}" \
                    f" {str(signals_list)}, settings, message_handler)"
        message_handler += f"    try:\n"
        for topic in topics_list:
            message_handler += f"        if topic == 'sensors/{topic}':\n"
            message_handler += f"            # questo è solo un esempio, deserializzo i dizionari\n"
            message_handler += f"            {topic}_dict: dict = json.loads(message)\n"
        message_handler += f"    except Exception as e:\n"
        message_handler += f"        print(e)\n"

    elif module_type == 3:
        main = main.replace('MqttSensor', 'MqttRemote')
        mqtt_init = f"mqtt = MqttRemote(sys.argv[1], 1883, '{module_name}', {str(topics_list)}" \
                    f" {str(signals_list)}, settings, message_handler)"
    main = main.replace('#$$mqtt start$$#', mqtt_init)
    main = main.replace('#$$message handler$$#', message_handler)
    with open(f'./{module_name}/src/main.py', 'w') as fw:
        fw.write(main)
system(f'git add {module_name}')
print('Modulo creato')
