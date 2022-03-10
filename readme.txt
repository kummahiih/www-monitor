

This program (on my side) is based on previous studies at http://kks.cabal.fi/kumma:
 * http://kks.cabal.fi/PyparsingBug 
      * Phantomjs
      * Pyparsing for parsing
                * at some point this could be used as page validation instead of now used finder regexps
      * The R Project for Statistical Computing.
 * http://kks.cabal.fi/PyevolveTesting
      * an alternative for Phantomjs

Requirements, reasons, install instructions, caveats:
 - REQUIREMENT: PhantomJS 1.2
    - REASON: "PhantomJS is an optimal solution for headless testing of web-based applications, site scraping, pages capture, SVG renderer, PDF converter and many other use cases." 
      - at least easier to use than Mozilla's Python interface ..  see http://kks.cabal.fi/PyevolveTesting 
    - REASON: evaluates javascript onload events
       - javascript is used everywhere and it is important to check if it works.
    - REASON: can render the contents of a png -file.
       - these can be used on the optional 'single page user interface'

    - INSTALL: build instructions at http://code.google.com/p/phantomjs/wiki/BuildInstructions
    - INSTALL: use version 1.2  ("git checkout 1.2"). That version was used, because it was the latest stable version. 
    - INSTALL: add phantomjs/bin/phantomjs to your path

    - CAVEAT: PhantomJS 1.2 lacks IO support, so I can not write page content after  to a file). 
       - Have to write it on QT side or wait http://code.google.com/p/phantomjs/issues/detail?id=129
       - Currently writes  contents to console... just better to wait the next version, because it's clearly coming:
          - See http://groups.google.com/group/phantomjs/browse_thread/thread/678137703dc82483?pli=1  
          - PhantomJS 1.3 is still in the development. It is scheduled to be released on September 23, 2011.
          
 - REQUIREMENT: Linux. 
    - REASON: currently the subprocess execution and subprocess tree termination (finding the pids) is a hack 

 - REQUIREMENT: Python 3.1
    - REASON: multiprocessing -module
      - http://docs.python.org/library/multiprocessing.html
      - " effectively side-stepping the Global Interpreter Lock by using subprocesses instead of threads. "
    - REASON: logging- module
       - CAVEAT: no support for multiprocessing
    
    - INSTALL: to install at Ubuntu, write: "$sudo apt-get install python3.1", other operating systems, see http://www.python.org/download/releases/3.1/
   

DESIGN:

Control                      View       (multiprocessing, wrapping, debugging tools)               Model

App|Scheduling process |  logging process | a work event for a work process at pool         | phantomjs |   R

Process init:
 |-------------------------->.
 |->|----------------------->|----> UI view
 |  |--------------------------------------->.
 |  |                        |<--------------|
 |  |                        |----> UI view
 
 (Process rampdown goes in the same way)

Configuration update:
 |->|------conf update------>|-------------->|
 |  |                        |----> UI view
 
Then on a scheduling loop:
 |  |-----schedule-------------------------->|
 |  |                        |               |----------------------------------------------------->.thumbnails, contents after onload, error logs, load times
 |  |                        |               |<-----------------------------------------------------.                            
 |  |                        |<--------------|
 |  |                        |               |
 |  |                        |----> UI view

(and perhaps .. let's see)
 |  |<---------------------------------------|

(and perhaps configuration update from the App after the 'scheduling loop')

(and perhaps at the future also:)
 .  .                        |---------------|
 .  .                        |               |---------------------------------------------------->. statistical analysis
 .  .                        |<--------------------------------------------------------------------.
 .  .                        |----> logfile, UI (with javascript visualizations :)
 .  .                        |
 .  .

 


App:
 - creates the other processes
 - user's commands from configuration files and whatnot 
 - Configuration:
	 - The configuration files are saved to CSV- files, because those can be easily manipulated on Excel, LibreOffice or such. 
	   - Easy to replace
	   - I wanted to test this there, no real reason
	   - Quite easy to add new features (!= easy to create plugins) 
	       - I have not considered doing plugins. Plugin framework needs some extra effort. 
	           - See projects like Trac and PyEvolve for ideas

Scheduling process:
 - generates the timed events for a worker pool
 
logging process:
 - writes lines to a log file   
   - difficulties with logging module --> NOT DONE. debug logs are printed to stdout
 - updates monitor UI
    - written in csv -format. the default file is www-data/result.csv

Work processes:
 - wrap the timeouts, error handling,  debugging magic and such


phantomjs:
 - thumbnails, javascript execution

R: 
 - statistical analysis



USAGE:

(put that phantomjs to your path first)

help:

www-monitor$ src/monitor-www.py -h
Usage: monitor-www.py [options]

Options:
  -h, --help            show this help message and exit
  -p FILE, --application-configuration-file=FILE
                        Application specific configuration. Default is
                        defaultconfigs/application-config.csv
  -n APPCONFNAME, --application-configuration-name=APPCONFNAME
                        'unique name'.  Default is debug


to execute, run:
www-monitor$ src/monitor-www.py

by writing 'q' and then enter, you can terminate the monitoring.

you can examine the results from:

$ cat www-data/result.csv 
"returncode";"execution_start";"execution_end";"timeout_occured";"screencapture";"logfile";"sitefile";"page loaded";"loading time";"validation regexp found"
"0";"2011-07-22-04-39";"2011-07-22-04-42";"False";"www-data/Google search/2011-07-22-04-39.png";"www-data/Google search/2011-07-22-04-39.log";"www-data/Google search/2011-07-22-04-39.html";"True";"2260";"True"
"0";"2011-07-22-04-43";"2011-07-22-04-46";"False";"www-data/Google mail/2011-07-22-04-43.png";"www-data/Google mail/2011-07-22-04-43.log";"www-data/Google mail/2011-07-22-04-43.html";"True";"1747";"True"
"0";"2011-07-22-04-39";"2011-07-22-04-47";"False";"www-data/Google mail/2011-07-22-04-39.png";"www-data/Google mail/2011-07-22-04-39.log";"www-data/Google mail/2011-07-22-04-39.html";"True";"6671";"True"
"0";"2011-07-22-04-48";"2011-07-22-04-51";"False";"www-data/Google mail/2011-07-22-04-48.png";"www-data/Google mail/2011-07-22-04-48.log";"www-data/Google mail/2011-07-22-04-48.html";"True";"1938";"True"


If you want to change the configurations, see defaultconfigs/debug-polling-config.csv  and defaultconfigs/application-config.csv

