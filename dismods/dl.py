import subprocess
import os

def ydl(url, option):

    if option == "list-formats" or option == "-F":
        cmdopt = "-F"
    elif option != "":
        cmdopt = "-f \"" + option + "\""
    else:
        cmdopt = "-f \"18/sd/mp4+m4a/w\" -S vcodec:h264"
        
    cmd = "yt-dlp " + cmdopt + " \"" + url + "\" -o video.mp4 --max-filesize 25M --no-colors --user-agent \"Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36\""
    
    print(cmd)
    
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as outputexc: 
        with open("output.txt", "w") as f:
            f.write(outputexc.output.decode('UTF-8'))
            f.close()
        return 10
     
    if os.path.exists("video.mp4"):
        return 0
    elif os.path.exists("video.mp4.mkv") or os.path.exists("video.mp4.webm"):
        try:
            os.rename("video.mp4.mkv", "video.mp4.webm")
        except FileNotFoundError:
            pass
        return 1
            
    else:
        with open("output.txt", "w") as f:
            f.write(output.decode('UTF-8'))
            f.close()
        return 11
