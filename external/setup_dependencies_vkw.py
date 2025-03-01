from os import environ, name as os_name
from pathlib import Path
# from shutil import copyfile  # not used yet
from subprocess import call


def create_paths_if_invalid(*paths):
    for path in paths:
        path = Path(path)  
        if not path.exists():
            path.mkdir()


if __name__ == '__main__':
    dirname = Path(__file__).resolve().parent
    proj_path_vulkan = dirname / 'Vulkan'  

    if os_name == 'nt':
        os_path_vulkan = Path(environ['VULKAN_SDK'])
        call(['robocopy', os_path_vulkan / 'include', proj_path_vulkan / 'include', '/E'])
        call(['robocopy', os_path_vulkan / 'Lib', proj_path_vulkan / 'lib64', '/E'])
        call(['robocopy', os_path_vulkan / 'Lib32', proj_path_vulkan / 'lib32', '/E'])
    else:
        create_paths_if_invalid(proj_path_vulkan)
        print('Not working for any other OS other than Windows')
