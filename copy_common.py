from os import listdir
from os.path import isfile, isdir, join
from shutil import copyfile, copy2

files = [f for f in listdir('./common_files') if isfile(join('./common_files', f))]
directories = [f for f in listdir() if isdir(f)]

for directory in directories:
    if directory != 'common_files' and directory[0] != '.':
        for file in files:
            file_dest = join('./{}/src'.format(directory), file)
            file_src = join('./common_files'.format(directory), file)
            print(file_src, file_dest)
            copyfile(file_src, file_dest)
