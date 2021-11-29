from os import listdir, makedirs
from os.path import isfile, isdir, join
from shutil import copyfile

files = [f for f in listdir('common_files') if isfile(join('common_files', f))]
modules = [f for f in listdir('modules') if isdir(join('modules', f))]

for directory in modules:
    if directory != 'common_files' and directory[0] != '.' and \
            directory != 'utility' and directory != 'example_module':
        makedirs(f"./modules/{directory}/src/common_files", exist_ok=True)
        for file in files:
            file_dest = join('./modules/{}/src/common_files'.format(directory), file)
            file_src = join('common_files', file)
            print(file_src, file_dest)
            copyfile(file_src, file_dest)
