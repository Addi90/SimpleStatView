import curses
from io import FileIO
import os,sys
import time
import optparse

# time (s) terminal display gets refreshed
refresh_time = 1


def get_cpu_thermal_zone():
    count = 0
    while(1):
        try:
            type_file = open("/sys/class/thermal/thermal_zone" + str(count) + "/type")
            if "x86" in type_file.read():
                return "/sys/class/thermal/thermal_zone" + str(count)
            count +=1    
        except Exception:
            return None


def read_temp_info(path : str):

    if(path is not None):
        temp_file = open(path+"/temp")
        temp = temp_file.read()
        return temp[:-4]
    else: 
        return "ERR"

    
def read_mem_info():
    proc_mem_info = open("/proc/meminfo")
    mem_stats = []
    total = 0
    free = 0
    avail = 0
    for line in proc_mem_info:
        if "MemTotal" in line:
            total = refactor_stat_info(line)
        elif "MemFree" in line:
            free = refactor_stat_info(line)
        elif "MemAvailable" in line:
            avail = refactor_stat_info(line)       
    mem_stats = ([total,free,avail])
    return mem_stats


def readCpuInfo():
    procCpuInfo = open("/proc/cpuinfo")
    cpuInfo = []
    name = 0
    cpuNum = 0
    freq = 0
    for line in procCpuInfo:
        if "processor" in line:
            cpuNum = refactor_stat_info(line)
        elif "cpu MHz" in line:
            freq = refactor_stat_info(line)
        elif "model name" in line:
            name = refactor_stat_info(line)
        elif line == "\n":
            cpuInfo.append([name,cpuNum,freq])
    return cpuInfo


def refactor_stat_info(stat_line : str):
    ref_stat_info = stat_line.split(":",1)[1].replace('\n','').replace(' ','')
    return ref_stat_info


def drawCpuCoreInfo(scr, cpuList, height, width):
    i=0
    cnt = 0
    colWidth  = 30
    for cpu in cpuList:
        mhzTxt = f"CPU{cpu[1].rjust(3,' ')}: {cpu[2].rjust(9,' ')} MHz"
        mhzCenter = int((colWidth)/2-(len(mhzTxt)/2))

        if colWidth*(i+1) > width:
            cnt +=1
            i=0
        if i == 0:
            scr.addstr(5+cnt,(colWidth*i),'|')

        scr.addstr(5+cnt,(colWidth*i)+mhzCenter,mhzTxt)
        scr.addstr(5+cnt,(colWidth*i)+colWidth,'|')

        i+=1
    return


def draw(scr):
    tzone_path = get_cpu_thermal_zone()
    currTemp = minTemp = maxTemp = read_temp_info(tzone_path)
    scr.clear()
    scr.refresh()
    curses.start_color()
    curses.curs_set(False)
    oldHeight, oldWidth = scr.getmaxyx()

    while(1):
        # check if terminal size has changed, resize
        height, width = scr.getmaxyx()

        if oldHeight is not height or oldWidth is not width:
            oldHeight, oldWidth = height, width
            scr.erase()  # erase the old contents of the window
            
        # get stats, build strings to be displayed
        currTemp = read_temp_info(tzone_path)
        if currTemp > maxTemp:
            maxTemp = currTemp
        if currTemp < minTemp:
            minTemp = currTemp
        cpuTemp = f"[ CPU Temp:  Curr.: {currTemp.rjust(3,' ')}°C | Min.: {minTemp.rjust(3,' ')}°C | Max.: {maxTemp.rjust(3,' ')}°C ]"

        cpuList = readCpuInfo()
        cpuName = f"[ CPU: {cpuList[1][0]} ]"

        mem_data = read_mem_info()
        mem_text = f"[ Memory:  Total: {mem_data[0].rjust(12,' ')} | Avail.: {mem_data[2].rjust(12,' ')} | Free: {mem_data[1].rjust(12,' ')} ]"
        
        # calc. row positioning of infos
        cpuNameCenter = int((width/2)-(len(cpuName)/2))
        cpuTempCenter = int((width/2)-(len(cpuTemp)/2))
        memCenter = int((width/2)-(len(mem_text)/2))
        
        # display infos on terminal
        scr.addstr(1,cpuNameCenter,cpuName)
        scr.addstr(2,cpuTempCenter,cpuTemp)        
        scr.addstr(3,memCenter,mem_text)        

        drawCpuCoreInfo(scr,cpuList,height,width)

        scr.refresh()
        time.sleep(refresh_time)



def main():
    parser = optparse.OptionParser()
    # refresh time
    parser.add_option('-t',
        help="Set refresh time in Seconds",
        action="store",
        default=1
        )
    args, remainder = parser.parse_args()
    refresh_time = args.t   

    curses.wrapper(draw)

    return

if __name__ == "__main__":
    main()