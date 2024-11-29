import subprocess
import os
if os.name == 'nt':
    from win10toast import ToastNotifier


def notify_user(subject, message):
    print(subject, message)
    if os.name == 'nt':
        ToastNotifier().show_toast(subject, message, duration=5, threaded=True)
    elif os.name == 'darwin':
        os.system("""osascript -e 'display notification "{}" with title "{}"'""".format(subject, message))
    elif os.name == 'posix':
        subprocess.run(['notify-send', subject, message])