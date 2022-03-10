#!/usr/bin/env python3.1

import multiprocessing
import csv

import logging

from optparse import OptionParser

import shutil
import os

import time

import re

import subprocess
import signal

import heapq

import inspect

def getCsvValues(aFile):
    with open(aFile, 'r' ) as f:
        reader = csv.DictReader(f, delimiter=';', quotechar='"')
        for values in reader:
            yield values

def matchbasic(aDict, name):
    matcher = '[a-zA-Z0-9 -_]*'
    if not re.match(matcher, aDict[name]):
        raise ValueError('%s does not match "%s" at %s'%(key,matcher,aDict))

class Config:
    configuration_keys = ['identifier']
    

    def validate(self, aDict): 
        for key in self.configuration_keys:
            if key not in aDict:
                raise KeyError('%s not found from %s'%(key,aDict))
            
        matchbasic(aDict, 'identifier')

        
        return aDict

    def read_properties(self, aFile):
        properties = list(getCsvValues(aFile))
        
        properties = [self.validate(i) for i in properties if i != None ]
        
        self.properties = properties
        self.propertyfile = aFile
    
    
    
    def setkey(self):
        keyed = {}
        for entry in self.properties:
            if entry['identifier'] in keyed:
                raise( KeyError(entry['identifier'] + ' occurs twice'))
            keyed[entry['identifier']] = entry
        self.properties = keyed
            
    def __init__(self, aFile):
        self.propertyfile = None
        self.properties   = None
        self.read_properties(aFile)
        self.setkey()
        

    


class ApplicationConfig(Config):
    #TODO: add constants for the entry names and use em ...
    configuration_keys = [
        'identifier',
        'workpath',
        'poller-processes',
        'logfile',
        'logging-level',
        'address-configuration-file',
        'resultlog-file'
        ]
    
    def validate(self,aDict):
        aDict = Config.validate(self, aDict)
        matchbasic(aDict, 'workpath')
        
        aDict['poller-processes'] = int(aDict['poller-processes'])
        
        return aDict


class AddressConfig(Config):
    configuration_keys = [
        'identifier',
        'address',
        'polling-interval',
        'timeout',
        'validation-regexp'
        ]
    
    def validate(self, aDict): 
        aDict['polling-interval'] = int(aDict['polling-interval'])
        aDict['timeout'] = int(aDict['timeout'])
        return aDict
            

    
    def read_properties(self, aFile):
        Config.read_properties(self, aFile)
        
        def setInterval(aDict):
            return aDict
            
        self.properties = map(setInterval, self.properties)



def getChildren(pid):
    p = popen('ps --no-headers -o pid --ppid %d' % pid)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]


class ExecutionTimeout(Exception):
    pass

class Alarm(Exception):
    pass


def alarmHandler(signum, frame):
    raise Alarm


def execute(applicationConfigDict, addressConfigDict, workpath, logfilepath,cmd):
    
    timeoutInSec = addressConfigDict['timeout']
    
    print('cmd: '+ cmd)
    print('workpath: '+ workpath)
    print('timeout: '+ str(timeoutInSec))
    
    now = time.strftime("%Y-%m-%d-%H-%S")
    print('now: '+ now)
    
    timeout_occured = False


    p = subprocess.Popen(cmd, shell = True, cwd = workpath, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    
    signal.signal(signal.SIGALRM, alarmHandler)
    signal.alarm(timeoutInSec)
    try:
        stdoutdata, stderrdata = p.communicate()
        signal.alarm(0)  # reset the alarm
        print('cmd '+cmd+' done.')
    except Alarm:
        print('Cmd '+cmd+' execution took too long.')
        pids = [p.pid] + getChildren(p.pid)
        
        print('Terminating pids: '+ str(pids) )

        for pid in pids:
            print('Sending SIGKILL to: ' +str(pid))
            os.kill(pid, signal.SIGKILL)
        timeout_occured = True
    
    now2 = time.strftime("%Y-%m-%d-%H-%S")
    
    return {'returncode':p.returncode, 'execution_start':now, 'execution_end':now2, 'timeout_occured': timeout_occured}


def createdir(directory):
    if  os.path.isdir(directory):
        return directory
    print('creating:' + directory)
    
    os.makedirs(directory)





def makeworkpath(archivepath):
    

    return fullworkpath


def run_and_analyse(applicationConfigDict, addressConfigDict, logQueue):
    try:
        print('run_and_analyse', addressConfigDict)
        
        archivepath = applicationConfigDict['workpath'] + '/' + addressConfigDict['identifier']
        createdir(archivepath)
        
        now = time.strftime("%Y-%m-%d-%H-%S")
        workpath = archivepath + '/' + now
        createdir(workpath)
        print('paths done')
        
        
        logfilepath = workpath + '.tmp'
        screencapturepath = workpath + '.png'
        
        cmd = "phantomjs '../../../src/loader.js' '%s' '../%s.png'"%(addressConfigDict['address'], now)
        cmd = cmd+" > '../%s.tmp' 2>&1"%now

        
        print('calling', applicationConfigDict)
        
        resultDict = execute(applicationConfigDict, addressConfigDict, workpath, logfilepath, cmd)
        
        try:
            open(screencapturepath, 'r')
            resultDict['screencapture'] = screencapturepath
        except:
            pass
        
        
        print('logfileHack')
    
        logfile, sitefile = logfileHack(logfilepath)
        resultDict['logfile'] = logfile
        resultDict['sitefile'] = sitefile


        
        print(logfile, sitefile)
        
        print('logfile analysis')
        
        if logfile != None:
            with open(logfile) as f:
                logs = f.read()
                resultDict['page loaded'] =  'Loading OK.' in logs.split('\n')
                try:
                    resultDict['loading time'] = re.findall('Loading time ([\d]+) msec',logs)[0]
                except:
                    pass
        
        print('sitefile analysis')
    
        if sitefile != None:
            with open(sitefile) as f:
                site = f.read()
                resultDict['validation regexp found'] = len(re.findall(addressConfigDict['validation-regexp'], site)) != 0
        
        logQueue.put(resultDict)
    except Exception as e:
        print('EXCEPTION')
        print(e)
        print('trace',inspect.trace())

    return


    
            

def logfileHack(logfilepath):
    try:
        s = open(logfilepath,'r').read()
    except:
        return None, None
    #fails, if the javascript prints smth like this :)
    sep = 'Page content:\n------8<----8<--------8<---\n'
    sepindex= s.find(sep)
    if sepindex == -1:
        return {}
    logs = s[:sepindex +len(sep)]
    reallogfile = logfilepath[:-3]+'log'
    print(reallogfile)
    with open(reallogfile,'w') as f:
        f.write(logs)
    
    
    site = s[sepindex +len(sep):]    
    sitefile = logfilepath[:-3]+'html'
    with open(sitefile,'w') as f:
        f.write(site)
    
    return reallogfile, sitefile

def resultLogger(applicationConfigDict, addressConfigDict, logQueue):
    print('logging process starts')
    headers = ['returncode', 'execution_start','execution_end','timeout_occured',
               'screencapture', 'logfile','sitefile', 'page loaded', 'loading time', 'validation regexp found']
    
    filefound = os.path.isfile(applicationConfigDict['resultlog-file'])
    with open(applicationConfigDict['resultlog-file'],'w') as f:
        print('file opened', applicationConfigDict['resultlog-file'])
        #fails, if header names have \" or \n or ; .. or smth like that
        if not filefound:
            f.write( '"' + '";"'.join(headers) + '"\n')
        writer = csv.DictWriter(f, headers, restval='', delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        next = logQueue.get()
        while next != 'quit':
            print('logger:',next)
            writer.writerow(next)
            #lets hope there is no internal buffer at DictWriter .. :|
            f.flush()
            next = logQueue.get()

            


def yieldTimes(now, addressDict):
    interval = addressDict['polling-interval']
    while True:
        now+=interval
        yield now

    
def scheduler(applicationConfigDict, addressConfigDictlist, logQueue, quitQueue):
    #this can be done in a much better way, but I guess this is enough for now
    print('creating the worker pool')

    workerpool = multiprocessing.Pool(processes = applicationConfigDict['poller-processes'])
    
    now = time.time()
    print('creating the polling heap')
    print(addressConfigDictlist)
    yielderDict = dict([( polled['identifier'],yieldTimes(now,polled)) for polled in addressConfigDictlist.values() ])
    pollingheap = [ [now+1, polled['identifier']] for polled in addressConfigDictlist.values()]
    
    
    while quitQueue.empty():
        next = heapq.heappop(pollingheap)
        print(next)

        target, polled = next
        now = time.time()
        to_sleep = target - now
        
        if to_sleep > 0:
            print('sleeping', to_sleep)
            time.sleep(to_sleep)
        
        task = workerpool.apply_async(run_and_analyse, (applicationConfigDict, addressConfigDictlist[polled], logQueue,))
        
        next[0] = yielderDict[polled].__next__()
        
        heapq.heappush(pollingheap, next)

    workerpool.close()
    workerpool.join()






if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-p", "--application-configuration-file", dest="appconffilename",
                  help="Application specific configuration. Default is %default", metavar="FILE",
                  default = "defaultconfigs/application-config.csv")
    
    parser.add_option("-n", "--application-configuration-name", dest="appconfname",
                  help="'unique name'.  Default is %default", 
                  default = "debug", type="string")
    
    
    (options, args) = parser.parse_args()

    application_configs  = ApplicationConfig(options.appconffilename)
    
    appconfindex = options.appconfname
    application_config = application_configs.properties[appconfindex]

    LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

    level = LEVELS.get(application_config['logging-level'], logging.NOTSET)
    logging.basicConfig(level=level, filename = application_config['logfile'])
    
    logging.debug('-------------------------------------------------')   
    logging.debug('Application configuration read, logging enabled.')
    logging.debug('Application configuration:')
    logging.debug(application_config)
    
    address_config  = AddressConfig(application_config['address-configuration-file'])
    
    logging.debug('address configuration:')
    logging.debug(address_config.properties)
    
    manager = multiprocessing.Manager()
    logQueue = manager.Queue()
    
    logProcess = multiprocessing.Process(target=resultLogger, args=(application_config, address_config.properties,logQueue,))
    logProcess.start()
    
    
    manager = multiprocessing.Manager()
    quitQueue = manager.Queue()
    
    chedulingprocess = multiprocessing.Process(target =  scheduler, 
                                               args = (application_config, address_config.properties, logQueue, quitQueue,)
                                               )
    chedulingprocess.start()
    
    while True:
        print('q quits')
        s = input()
        if s == 'q':

            quitQueue.put('quit')
            chedulingprocess.join()
            
            logQueue.put('quit')
            logProcess.join()
            break

