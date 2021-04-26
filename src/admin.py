#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
import ctypes
import sys


def is_user_admin():
    """
    Check if the current user is an 'Admin' whatever that means (root on Unix).

    Return: True or False
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(str(e))
        return False


def run_win_as_admin(wait=True):
    """
    Set the current command to run as an admin.
    This can only be use in Windows
    Args:
        wait: Wait for the cmd to be executed.

    Returns: The process code or None

    """
    import win32con
    import win32event
    import win32process
    from win32com.shell import shellcon
    from win32com.shell.shell import ShellExecuteEx
    python_exe = sys.executable
    cmdLine = [python_exe] + sys.argv

    cmd = '"%s"' % (cmdLine[0],)
    params = " ".join(['"%s"' % (x,) for x in cmdLine[1:]])
    showCmd = win32con.SW_SHOWNORMAL
    lpVerb = 'runas'
    procInfo = ShellExecuteEx(nShow=showCmd,
                              fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                              lpVerb=lpVerb,
                              lpFile=cmd,
                              lpParameters=params)

    if wait:
        procHandle = procInfo['hProcess']
        win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(procHandle)
    else:
        rc = None

    return rc
