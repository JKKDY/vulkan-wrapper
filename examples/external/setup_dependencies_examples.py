import os
import subprocess
from urllib.request import urlretrieve
from shutil import copytree, copyfile
import zipfile
import requests
from pathlib import Path


assert os.name == 'nt', "Platforms other than windows not yet suported"

GLFW_REPO = "glfw/glfw"
GLM_REPO = "g-truc/glm"
STB_REPO = "nothings/stb"
GLI_REPO = "g-truc/gli"
ASSIMP_REPO = "assimp/assimp"

CWD = os.path.dirname(__file__)




def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def copy(src, dst):
    if not os.path.exists(dst):
        copytree(src, dst)

def copy_file(src, dst):
    if not os.path.exists(dst):
        copyfile(src, dst)

def download(url, dst):
    if not os.path.exists(dst):
        urlretrieve(url, dst)

def unzip(zip_path):
     if not os.path.exists(str(zip_path)[:-4]):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(CWD)

def clone(repo):
    path = os.path.basename(repo)
    mkdir(path)
    if len(os.listdir(path)) == 0: # only install if folder is not empty
        subprocess.run(['git', 'clone', f'https://github.com/{repo}.git', path])
    return os.path.basename(repo)[0:-4]


def get_release_URL(repo:str, suffix:str):
    request_url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(request_url)

    if response.status_code != 200:
        print(f"Failed to get latest release for {repo}: HTTP {response.status_code}")
        exit(-1)

    data = response.json()
    latest_version = data["tag_name"] 
    clean_version = latest_version.lstrip("v")  # Remove leading "v" if present

    for asset in data.get("assets", []):
        if suffix in asset["name"]:
            return asset["browser_download_url"]
    
    # If no exact match, construct based on convention
    return f"https://github.com/{repo}/releases/download/{latest_version}/{repo.split('/')[-1]}-{clean_version}{suffix}"


def install_glfw():
    print("Installing GLFW")
    glfw_url_32 = get_release_URL(GLFW_REPO, ".bin.WIN32.zip")
    glfw_url_64 = get_release_URL(GLFW_REPO, ".bin.WIN64.zip")
    print(f"GLFW URL 32 {glfw_url_32}")
    print(f"GLFW URL 64 {glfw_url_64}")

    download_path_64 = Path(os.path.basename(glfw_url_64))
    download(glfw_url_64, download_path_64)
    download_path_32 = Path(os.path.basename(glfw_url_32))
    download(glfw_url_32, download_path_32)
    print("Downloaded glfw")
    
    unzip(download_path_32)
    unzip(download_path_64)
    print("Extracted glfw")

    extract32 = download_path_32.stem
    extract64 = download_path_64.stem
    mkdir("glfw")
    copy(os.path.join(extract32, 'include/GLFW'), Path("glfw") / "include/glfw")
    copy(os.path.join(extract32, 'lib-vc2022'), Path("glfw") / "Win32")
    copy(os.path.join(extract64, 'lib-vc2022'), Path("glfw") / "x64")
    print("Copied glfw files")



def build_assimp(build_type, arch):
    assert build_type == "Debug" or build_type == "Release"
    assert arch == "x64" or arch == "Win32"

    ASSIMP_SOURCE_DIR = Path(os.path.abspath("assimp"))  # Points to /assimp
    ASSIMP_BUILD_DIR = ASSIMP_SOURCE_DIR / f"build_{arch}"  # Build inside /assimp/build
    ASSIMP_LIB_DIR = ASSIMP_SOURCE_DIR / f"{arch}"  # Build inside /assimp/build

    mkdir(ASSIMP_BUILD_DIR)
    mkdir(ASSIMP_LIB_DIR)

    cmake_configure_cmd = [
        "cmake", "..",
        "-G", "Visual Studio 17 2022", 
        "-A", arch,
        f"-DCMAKE_BUILD_TYPE={build_type}",  
        "-DASSIMP_BUILD_TESTS=OFF",  # Disable tests for faster build
    ]
    subprocess.run(cmake_configure_cmd, cwd=ASSIMP_BUILD_DIR, check=True)

    cmake_build_cmd = [
        "cmake",
        "--build", ".",
        "--config", build_type
    ]
    subprocess.run(cmake_build_cmd, cwd=ASSIMP_BUILD_DIR, check=True)

    copy_file(ASSIMP_BUILD_DIR / "bin"/ build_type / "assimp-vc143-mt.dll", ASSIMP_LIB_DIR / "assimp-vc143-mt.dll")
    copy_file(ASSIMP_BUILD_DIR / "lib"/ build_type / "assimp-vc143-mt.lib", ASSIMP_LIB_DIR / "assimp-vc143-mt.lib")

    copy_file(ASSIMP_SOURCE_DIR / "build_x64/include/assimp/config.h", ASSIMP_SOURCE_DIR / "include/assimp/config.h")



if __name__ == "__main__":
    clone(GLM_REPO)
    clone(STB_REPO)
    clone(GLI_REPO)
    clone(ASSIMP_REPO)

    install_glfw()

    build_assimp("Release", "x64")
    build_assimp("Release", "Win32")
