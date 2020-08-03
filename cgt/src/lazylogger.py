# -*- coding: utf-8 -*-
"""
Created on Mon May 11 22:53:07 2020

@author: j.h.pickering@leeds.ac.uk
"""

import logging
import logging.handlers

def set_up_logging(
        file_name, 
        stderr_level = logging.DEBUG, 
        file_level = logging.DEBUG,
        file_size_limit = 5000,
        number_back_ups = 5,
        append = False):
    """
    set up the root python logger, which will be the base of all default 
    loggers in this Python virtual machine. Once run calls to getLogger, will
    produce a handler passing messages to this root, there is no need to 
    specify format, but you can set a local level. Only messages above a 
    handlers level will be passed on: DEBUG 10, INFO 20, WARNING 30, ERROR 40,
    CRITICAL 50.
    
    Note the logging module works by locating root in the Python virtual 
    machine (PVM), which allows it to be accessed by all objects, in all 
    threads, running on that PVM. A result for interactive users is that to 
    change setting between runs of your code, you will have to restart the 
    kernal of you PVM.
    
    Parameters
    ----------
    file_name : string, required
        name or full path of the log file.
    stderr_level : logging MESSAGE LEVEL, optional
        the level for displaying messages on stdout. 
        The default is DEBUG
    file_level : logging MESSAGE LEVEL, optional
        the level for storing messaged in file. 
        The default is DEBUG
    file_size_limit : int, optional
        the size to which the log file is allowed to grow before copying to a 
        backup file
        The default is 5000, approx a page of A4.
    number_back_ups : int, optional 
        the number of backup log files
        The default is 5.
    append : boolean, optional
        if true the log file is appended to the existing logfile with a new
        file started every 5kB, used files are stored in (max 5) backups. The 
        default is False.

    Returns
    -------
    None.
    """
            
    # stream handlers default to stderr
    c_handler = logging.StreamHandler()
    
    # file handeler 
    if append:
        # append to log file each time is run cyclic with 5 backups
        f_handler = logging.handlers.RotatingFileHandler(
                file_name, 
                mode='a', 
                maxBytes=file_size_limit,
                backupCount=number_back_ups)
    else:
        f_handler = logging.FileHandler(file_name, mode='w')
    
    # set the name of the handler so it can be recognized later for removal
    f_handler.set_name(file_name)

    # Create formatters and add them to the handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    c_handler.setLevel(stderr_level)
    f_handler.setLevel(file_level)
    
    # add the handeler to the root logger, this will now be the default for
    # all loggers defined in this python virtual machine. 
    logging.basicConfig(handlers=[c_handler, f_handler])
    
def end_logging(file_name):
    """
    clean up after loggin by flusing and closing log file, if code is run in an 
    interactive Python session the interpreter will maintain the open log file 
    between runs

    Returns
    -------
    None.
    """
    
    for handler in logging.getLogger().handlers[:]:
        if handler.get_name() == file_name:
            handler.flush()
            handler.close()

# test & demonstration
######################
           
def test():
    class MyFunctor(object):
        def __init__(self, x, y, z):
            self._x = x
            self._y = y
            self._z = z
        
        def inner(self, x, y, z):
            logger = logging.getLogger("MyFunctor")
            logger.setLevel(logging.WARNING)
            logger.critical("critical")
            logger.error('This is an error')
            logger.warning('This is a warning')
            logger.info("information")
        
            return self._x*x + self._y*y + self._z*z
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.critical("critical")
    logger.error('This is an error')
    logger.warning('This is a warning')
    logger.info("information")
    
    f = MyFunctor(1, 1, 1)
    print("inner product: {}".format(f.inner(3, 4, 5)))

if __name__ == "__main__":
    set_up_logging("mylog.log", append=True)
    test()
    end_logging("mylog.log")
        