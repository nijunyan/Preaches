import time
import subprocess as sp

def modify_text():
    with open('PreachesListDone.txt', "w+") as f:
        read_data = f.read()
        f.seek(0)
        f.truncate()

while True:
    extProc = sp.Popen(['python','preaches.py']) # runs myPyScript.py
    status = sp.Popen.poll(extProc) # status should be 'None'
    modify_text()
    time.sleep(15*60)
    sp.Popen.terminate(extProc) # closes the process
    status = sp.Popen.poll(extProc) # status should now be something other than 'None' ('1' in my testing)

