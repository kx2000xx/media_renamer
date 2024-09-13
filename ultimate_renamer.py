import re
import os
import subprocess
import time
release_types = ["WEB-DL", "WEBRip", "DVD", "DVDRip", "BluRay", "BRrip", "BDRip", "BD", "HDTV", "TVRip"]
platforms = ["AMZN", "NF", "StarzPlay", "SHOFHA", "SHAHID", "CR", "SGO", "AWAAN", "51KW", "WEYYAK", "VIU", "Arabeo", "Roya", "Aloula", "Mahatat", "HilalPlay", "Istikana", "Tabii", "TOOG", "ORBIT", "STCTV", "WATCHIT", "DSNP", "1001TV", "OSN", "BluTV", "TWIST", "DzairPlay", "NoorPlay", "Maraya", "VIKI", "HiTV", "MTV", "IQIYI", "WETV", "FORJA", "WK", "FASELPLUS", "SHASHA", "ADTV", "TenTime", "ElShasha", "TOD", "Almanasa", "Zolal", "MySatGo", "SwitchTV", "WK"]
additional_types = ["EXTENDED","REPACK", "PROPER", "RERIP", "COMPLETE","DUAL", "AUDIO", "MULTI", "Dubs", "Dub", "Subbed", "DIRECTORS", "CUT", "DC", "DV", "DolbyVision", "HDR", "HDR10", "PLUS", "UNRATED", "LIMITED", "REMUX", "Season", "Pack", "MULTiSUB", "Arabic", "Subs", "FanSub", "HardSub", "SoftSub", "REMASTERED", "Reducted"]
filebot = "FileBot/filebot.exe"

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

files = os.listdir("files")
extensions = [os.path.splitext(file)[1] for file in files]
files_without_extensions = [os.path.splitext(file)[0] for file in files]
group = "Pirates"
release_type = ""
tvdb_id = None
tmdb_id = None
platform = ""
for file, ext in zip(files_without_extensions, extensions):
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



# TMDB1726 BluRay
# TMDB912770 WEBRip
# TMDB1144911 BluRay REMUX HDR10 PLUS