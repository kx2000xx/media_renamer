import re
import os
import subprocess
import json
from pathlib import Path
import requests
import time

# allowed_types = requests.get("https://raw.githubusercontent.com/kx2000xx/media_renamer/main/allowed_types").json()
# current_year = datetime.datetime.now()
# release_types = allowed_types['release_types']
# platforms = allowed_types['platforms']
# additional_types = allowed_types['additional_types']
# codec_types = allowed_types['codec_types']
# audio_formats = allowed_types['audio_formats']



release_types = ["WEB-DL", "WEBRip", "DVD", "DVDRip", "BluRay", "Bluray", "Blu-Ray","BRrip", "BDRip", "BD", "HDTV", "TVRip"]
platforms = ["AMZN", "NF", "StarzPlay", "SHOFHA", "SHAHID", "CR", "SGO", "AWAAN", "51KW", "WEYYAK", "VIU", "Arabeo", "Roya", "Aloula", "Mahatat", "HilalPlay", "Istikana", "Tabii", "TOOG", "ORBIT", "STCTV", "WATCHIT", "DSNP", "1001TV", "OSN", "BluTV", "TWIST", "DzairPlay", "NoorPlay", "Maraya", "VIKI", "HiTV", "MTV", "IQIYI", "WETV", "FORJA", "WK", "FASELPLUS", "SHASHA", "ADTV", "TenTime", "ElShasha", "TOD", "Almanasa", "Zolal", "MySatGo", "SwitchTV", "WK"]
additional_types = ["EXTENDED","REPACK", "PROPER", "RERIP", "COMPLETE","DUAL", "AUDIO", "Subbed", "DIRECTORS", "CUT", "DC", "DV", "DolbyVision", "HDR", "HDR10", "PLUS", "UNRATED", "LIMITED", "REMUX", "Season", "Pack", "MultiSub", "Arabic", "FanSub", "HardSub", "SoftSub", "REMASTERED", "Reducted", "Multi", "Sub", "Subs", "Dub", "DubS", "3D"]
codec_types = ["x264", "x265", "XviD", "DivX", "AVC"]
audio_formats = ["AAC", "AC3", "DTS", "FLAC", "MP3", "EAC3", "Opus", "DD"]
filebot = "FileBot/filebot.exe"
mediainfo = "MediaInfo/MediaInfo.exe"

with open('config.json') as config_file:
    config_data = json.load(config_file)
API_KEY = config_data['API_KEY']
GROUP = config_data['group']

def execute_tvdb(file, ext, tvdb_id, newformat):
  subprocess.call([
      filebot,
      "-rename", f"files/{file}{ext}",
      "--db", "TheTVDB",
      "--q", f"{tvdb_id}",
      "--format", newformat,
      "--log", "all",
    ])

def execute_tmdb(file, ext, tmdb_id, newformat):
  subprocess.call([
      filebot,
      "-rename", f"files/{file}{ext}",
      "--db", "TheMovieDB",
      "--q", f"{tmdb_id}",
      "--format", newformat,
      "--log", "all",
    ])
  

def export_xml(root, file, newpath):
    
    subprocess.call([
        mediainfo, "--Output=XML", f"--LogFile={newpath}{file}.xml", f"{root}/{file}"
    ])


def create_nfo(root, file, newpath):
    subprocess.call([
        mediainfo, "--BOM", f"--LogFile={newpath}{file}.nfo", f"{root}/{file}"
    ])



def name_check(fullname):
    year = None
    group = fullname.rsplit('-', 1)[1].split('.')[0]
    fullname = fullname.rsplit('-', 1)[0]

    try:
        match = re.match(r'^(.*?)\.S(\d+)E(\d+)', fullname)
        show_name = match.group(1).replace('.',' ')
        season_number = f"S{int(match.group(2)):02d}"
        episode_number = f"E{int(match.group(3)):02d}"
        sse = f"{show_name.replace(' ', '.')}.{season_number}{episode_number}."
    except:
        match = re.match(r'^(.*?)\.(\d{4})', fullname)
        show_name = match.group(1).replace('.',' ')
        year = match.group(2)
        sse = f"{show_name.replace(' ','.')}.{year}"
    strings = fullname.replace(sse, "").strip().split('.')
    
    additional_info = []
    for string in strings:
        if re.match(r'(\d+p)', string):
            resolution = string
        elif string in release_types:
            release_type = string
        elif string in platforms:
            platform = string
        elif string in codec_types:
            codec_type = string
        elif string in audio_formats:
            if string == "MP3":
                audio_format = string
            else:
                audio_format = f"{string}{fullname.split(string)[1][0:4]}"
        elif re.match(r'^(\d+)bit', string):
            bit = string
        elif string in additional_types:
            additional_info.append(string)
    if year:
        if "WEB" in release_type:
            return show_name, year, resolution, release_type, platform, codec_type, bit, audio_format, group, additional_info
        else:
            return show_name, year, resolution, release_type, None, codec_type, bit, audio_format, group, additional_info
    else:
        if "WEB" in release_type:
            return show_name, season_number, episode_number, resolution, release_type, platform, codec_type, bit, audio_format, group, additional_info
        return show_name, season_number, episode_number, resolution, release_type, None, codec_type, bit, audio_format, group, additional_info


def export():
  for root, _, files in os.walk("files"):
    if root != "files":
        parent_path = root.split('\\')
        parent_path.pop(0)
    else:
        parent_path = ""
    for file in files:
        try:
            show_name, season_number, episode_number, resolution, release_type, platform, codec_type, bit, audio_format, group, additional_info = name_check(file)
            newpath = "nzb/"
            for folder in parent_path:
                newpath = newpath + folder + '/'
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            create_nfo(root, file, newpath)
            export_xml(root, file, newpath)
        except:
            movie_name, year, resolution, release_type, platform, codec_type, bit, audio_format, group, additional_info = name_check(file)
            newpath = "nzb/"
            for folder in parent_path:
                newpath = newpath + folder + '/'
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            create_nfo(root, file, newpath)
            export_xml(root, file, newpath)


def renamer():
  files = os.listdir("files")
  extensions = [os.path.splitext(file)[1] for file in files]
  files_without_extensions = [os.path.splitext(file)[0] for file in files]
  #group = GROUP
  release_type = ""
  tvdb_id = None
  tmdb_id = None
  platform = ""
  for file, ext in zip(files_without_extensions, extensions):
      grouptxt = os.listdir("files/"+file)
      group = None
      for g in grouptxt:
          if g.endswith('.txt'):
              group = g.split('.txt')[0]
              break
      name = file.split(" ")
      print(name)
      additional_type = []
      for word in name:
        if "TVDB" in word:
          tvdb_id = word.split("TVDB")[1]
        elif "TMDB" in word:
          tmdb_id = word.split("TMDB")[1]
        elif word in release_types:
          release_type = word.strip()
        elif word in platforms:
          platform = word.strip()
        elif word in additional_types:
          additional_type.append(word.strip())
      
      
      if tvdb_id:
          newformat = "{n.replace(' ', '.')}.{s00e00}.{vf}"
      elif tmdb_id:
          newformat = "{n.replace(' ', '.')}.{y}.{vf}"


      if release_type == "WEBRip" or release_type == "WEB-DL":
          if platform:
            newformat = newformat + f".{platform}" 
          elif platform == None:
            newformat = newformat + ".{" + f"{platforms}"+".find{ file.name.contains(it) }?.toUpperCase() ?: ''}.{source.upper()}"
          else:
            print("WEB Release without platform?!")
            exit(1)
      else:
        platform = None

      
      newformat = newformat + f".{release_type}."+ "{vc}.{bitdepth}bit.{ac}.{channels}"
      if additional_type:
        for a in additional_type:
          newformat = newformat + f".{a}"
      
      newformat = newformat + f"-{group}"

      if tvdb_id and release_type:
        execute_tvdb(file, ext, tvdb_id, newformat)
        tvdb_id = None
      elif tmdb_id and release_type:
        execute_tmdb(file, ext, tmdb_id, newformat)
        tmdb_id = None
      else:
        print("Something went wrong, Release Type is not defined or TVDBxxxx/TMDBxxxx doesn't exist")

# Windows Command for reference
# "ngPostv4.16.1_x64\ngPost.exe" -i "files\%%~nxf" -o "nzb\%%~nxf.nzb" -c "ngPostv4.16.1_x64\ngPost.conf" --gen_par2

DELETE = config_data['Delete-After-Upload']  # Delete files after complete
main_path = Path()
files_path = main_path / 'files'
nzb_path = main_path / 'nzb'
ngPost_exe = main_path / 'ngPostv4.16.1_x64/ngPost.exe'
ngPost_conf = main_path / 'ngPostv4.16.1_x64/ngPost.conf'


def delete_with_parent(path: Path):
    parent = Path(path.parent)  # store the parent to use it later

    # This checks if the path is files path, then ignore it
    if path == files_path:
        pass

    elif path.is_file():  # check if the path is a file
        path.unlink()  # delete the file
        if not any(parent.iterdir()):  # check if parent folder is empty
            delete_with_parent(parent)  # call the function again to delete the parent folder

    elif path.is_dir():  # check if the path is folder
        if not any(path.iterdir()):  # Check if the folder is empty
            path.rmdir()  # delete the empty folder
            if not any(parent.iterdir()):  # check if parent folder is empty
                delete_with_parent(parent)  # call the function again to delete the parent folder


def run_ngpost():

    # Note: There is a weired behavior when iterate on glob result, returns an error when iterating
    # on the last file, so as a workaround it will be appended on a list, then process the list
    files_glob = files_path.glob('**/*')
    files = []
    for file in files_glob:
        if file.exists():
            files.append(file)

    # Start processing the files
    for file in files:
        if file.exists():  # Check if the file exists, just in case some files deleted by user or other ways
            if file.is_file():  # Check if the file is actually a file, not a directory or folder
                print('processing ', file)
                relative_file_path = file.relative_to(files_path)
                source_file_path = files_path / relative_file_path
                nzb_file_path = nzb_path / relative_file_path.with_name(relative_file_path.name + '.nzb')

                # If nzb folder is not created, then create the whole tree
                if not nzb_file_path.parent.exists():
                    nzb_file_path.parent.mkdir(parents=True, exist_ok=True)

                COMMAND = [
                    f'{ngPost_exe}',
                    '-i',
                    f'{source_file_path}',
                    '-o',
                    f'{nzb_file_path}',
                    '-c',
                    f'{ngPost_conf}',
                    '--gen_par2',
                    '-x'
                ]
                subprocess.run(COMMAND)

                # If file deletion is enabled
                if DELETE:
                    delete_with_parent(file)  # Delete the file, and delete container folder if empty

            # This is useful for deleting empty folders, it will work only if folder is empty,
            # otherwise it does not do anything.
            elif file.is_dir():
                delete_with_parent(file)




def post_arabnzb():
   url = f"http://149.56.108.243/api?t=nzbadd&apikey={config_data['API_KEY']}"

   # Path to the main directory
   folder_path = "nzb"

   def find_nzb_files(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.nzb'):
                    file, _ = os.path.splitext(file)
                    yield os.path.join(root, file)

    # Find all NZB files in the specified folder and its subdirectories
   nzb_files = find_nzb_files(folder_path)

    # Iterate through each NZB file and send it to the API
   for nzb_file in nzb_files:
        files = {'file': open(f"{nzb_file}.nzb", 'rb'), 'nfo': open(f"{nzb_file}.nfo", 'rb'), 'mediainfo': open(f"{nzb_file}.xml", 'rb')}
        match = re.match(r'^(.*?)\.(\d{4}).(\d+p)', nzb_file)
        if "3D" in nzb_file and match:
            response = requests.post(url+"&cat=2060", files=files)
        elif ("Blu-Ray" in nzb_file or "BluRay" in nzb_file or "Bluray" in nzb_file) and re.match(r'^(.*?)\.(\d{4}).(\d+p)', nzb_file) and match:
            response = requests.post(url+"&cat=2050", files=files)
        else:
            response = requests.post(url, files=files)

        # Check the response status code
        if response.status_code == 200:
            print(f"File {nzb_file} sent successfully")
            print(response.text)
        else:
            print(f"Error uploading {nzb_file}: {response.text}")




print("================Start Point====================")
print("1) Renamer")
print("2) export xml & nfo files")
print("3) start ngpost")
print("4) Post to arabnzb")
choice = input("\n\n>>>>")
if choice == '1':
    renamer()
    input("Check Names Manually then Press Enter to continue....")
    export()
    run_ngpost()
    post_arabnzb()
elif choice == '2':
    export()
    run_ngpost()
    post_arabnzb()
elif choice == '3':
    run_ngpost()
    post_arabnzb()
elif choice == '4':
    post_arabnzb()
