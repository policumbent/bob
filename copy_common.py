from os import listdir, makedirs
from os.path import isfile, isdir, join
from shutil import copyfile, copy2

files = [f for f in listdir('./common_files') if isfile(join('./common_files', f))]
directories = [f for f in listdir() if isdir(f)]

for directory in directories:
    if directory != 'common_files' and directory[0] != '.' and \
            directory[0] != 'utility' and directory != 'example_module':
        makedirs(f"./{directory}/src/common_files", exist_ok=True)
        for file in files:
            file_dest = join('./{}/src/common_files'.format(directory), file)
            file_src = join('./common_files', file)
            print(file_src, file_dest)
            copyfile(file_src, file_dest)
