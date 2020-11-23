'''
utils.py

This python module contains useful functions that are needed for the
 CrystalGrowthTracker application.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2020
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
'''

import socket
from sys import platform as _platform
import datetime

def find_hostname_and_ip():
    """Finds the hostname and IP address to go in the log file.

    Args:
       No arguments

    Returns:
       host (str): Name of the host machine executing the script.
       ip_address (str): IP adress of the machine that runs the script.
       operating_system (str): Operating system of the machine that runs the script.

    """
    host = 'undetermined'
    ip_address = 'undetermined'
    operating_system = 'undetermined'

    try:
        host = socket.gethostbyaddr(socket.gethostname())[0]
    except socket.herror:
        host = "undetermined"

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # doesn't even have to be reachable
        my_socket.connect(('10.255.255.255', 1))
        ip_address = my_socket.getsockname()[0]
    except socket.error:
        ip_address = '127.0.0.1'
    finally:
        my_socket.close()

    if _platform in ("linux", "linux2"):
        # linux
        operating_system = 'Linux'
    elif _platform == "darwin":
        # MAC OS X
        operating_system = 'Mac OSX'
    elif _platform == "win32":
        # Windows
        operating_system = 'Windows'
    elif _platform == "win64":
    # Windows 64-bit
        operating_system = 'Windows'

    return host, ip_address, operating_system

def timestamp():
    ''' Gets the date and time from the operating system and turns it into
        a string used as a time stamp. This function allows consistency in the
        format of the time stamp string.
        Args:
            NONE
        Returns:
            timestamp (str):  In the format of year_month_day_hour_minute_second.
    '''
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
