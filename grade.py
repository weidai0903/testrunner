import os
import sys
import time
import shutil
import subprocess as sp

def parseTest(msg, student, killed, options):
    ''' parse stderr and figure out what's wrong'''
    separator = '\n==============================\n'
    # open source file and check style
    p = sp.Popen([options['EDITOR'], options['TESTTARGET']])
    p.wait();
    style = raw_input("enter style comments:")
    # handled exceptional scripts
    optional = "";
    out = "";
    if (killed):
        print student, '\'s test is killed, need manual test and save output file'
        processed = False
        while not processed:
            done = raw_input("manual test finished? (yes/no)").strip().lower()
            if done == 'yes' or done == 'y':
                optional = raw_input("enter optional comments and test output: ")
                processed = True
    else:
        out = parseError(msg, options)
    # write result
    result = open(student, 'w+')
    output = 'style comments:\n' + style + separator + \
             'other comments:\n' + optional + separator + \
             'test output:\n' + out
    result.write(output)
    result.close()

def parseError(msg, options):
    err = 0
    for c in msg:
        if c == 'F' or c == 'E': # failure or error
            err = err + 1
        elif c == '\n':
            break
    out = '\n\nFailed tests deductions: ' + str(err * options['FAILEDTESTPOINTS'])
    return msg + out

def runTests(options):
    fNames = os.listdir(options['FOLDER'])
    if not os.path.exists(options['RESULTS']):
        os.makedirs(options['RESULTS'])
    count = 0
    for fName in fNames:
        if not fName.endswith('.py'): 
            continue
        print(fName)
        shutil.copyfile(options['FOLDER'] + fName, options['TESTTARGET'])
        try :
            p = sp.Popen([options['TESTCMD'], options['TESTSCRIPT']], stdout=sp.PIPE, stderr=sp.PIPE);
            t = 0
            ret = None
            killed = False
            while ret is None:
                ret = p.poll()
                if ret is not None:
                    break
                if t > options['TLIMIT']:
                    killed = True
                    ret = p.kill()
                    break;
                time.sleep(options['TINTERVAL'])
                t = t + options['TINTERVAL']
            if (ret is not 0):
                parseTest(p.communicate()[1], options['RESULTS'] + fName + '.txt', killed, options)
                print "this guy failed the tests"
            else:
                parseTest("all tests passed", options['RESULTS'] + fName + '.txt', killed, options)                
                print "this guy passed all tests!"
        except:
            print "Unexpected error:", sys.exc_info()[0]
        os.remove(options['TESTTARGET'])
        try:
            os.remove(options['TESTTARGET'] + 'c')
        except:
            print 'no pyc file created'
        count = count + 1
    print 'count :', count

def main():

    options = {
        'TLIMIT':2,
        'TINTERVAL':0.1,
        'FOLDER':'submissions/',
        'RESULTS':'results/',
        'TESTCMD': 'python',
        'TESTSCRIPT':'number_personalities_test.py',
        'TESTTARGET':'number_personalities.py',
        'FAILEDTESTPOINTS':5,
        'EDITOR':'vim'
        }

    runTests(options)

main()
