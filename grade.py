import os
import sys
import time
import shutil
import subprocess as sp

def parseTest(msg, student, killed, options):
    ''' parse stderr and figure out what's wrong'''
    result = open(student, 'w+')
    if (killed):
        out = 'process killed (possibly infinite loop), need manual test'
    else:
        out = parseError(msg, options)
    result.write(out)
    result.close()

def parseError(msg, options):
    err = 0
    for c in msg:
        if c == 'F':
            err = err + 1
        elif c == '\n':
            break
    out = 'Point deductions: ' + str(err * options['FAILEDTESTPOINTS'])
    out = out + '\nDetails:\n'
    return out + msg

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
            p = sp.Popen(['python', options['TESTSCRIPT']], stdout=sp.PIPE, stderr=sp.PIPE);
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
        'TESTSCRIPT':'number_personalities_test.py',
        'TESTTARGET':'number_personalities.py',
        'FAILEDTESTPOINTS':5
        }

    runTests(options)

main()
