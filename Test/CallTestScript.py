import subprocess
import argparse
import os
from datetime import date
import RunAllTests
import shutil
import stat

class TestSetInfo(object):
    def __init__(self, testDir, testList, summaryFile, passedTests, repoSrc, pullBranch):
        self.testDir = testDir
        self.testList = testList
        self.summaryFile = summaryFile
        self.passedTests = passedTests
        self.pullBranch = pullBranch
        self.repoSrc = repoSrc

def cleanupString(string):
    string = string.replace('\t', '')
    return string.replace('\n', '').strip()

def cloneRepo(repoSrc, repoDst, pullBranch):
    # make dir if it doesnt exist, clean dir if it does exist
    if not os.path.isdir(repoDst):
        os.makedirs(repoDst)
    else:        
        filesToDelete = [f for f in os.listdir(repoDst)]
        for f in filesToDelete:
            path = repoDst + '\\' + f
            #change permissions to allow deletion 
            os.chmod(path, stat.S_IWUSR)
            if os.path.isdir(path):
                #change permissions to allow deletion in the dir tree
                for root, subdirs, files in os.walk(path):
                    for s in subdirs:
                        os.chmod(os.path.join(root, s), stat.S_IWUSR)
                    for f in files:
                        os.chmod(os.path.join(root, f), stat.S_IWUSR)
                shutil.rmtree(path)
            else:
                os.remove(path)

    subprocess.call(['git', 'clone', repoSrc, repoDst, '-b', pullBranch])

def sendEmail(recipientsFile, subject, body, attachments):
    sender = 'clavelle@nvidia.com'
    recipients = str(open(recipientsFile, 'r').read());
    subprocess.call(['blat.exe', '-install', 'mail.nvidia.com', sender])
    command = ['blat.exe', '-to', recipients, '-subject', subject, '-body', body]
    for a in attachments:
        command.append('-attach')
        command.append(a)
    subprocess.call(command)

def main():
    testConfigFile = 'TestConfig.txt'
    emailRecipientFile = 'EmailRecipients.txt'
    parser = argparse.ArgumentParser()
    parser.add_argument('-config', '--testconfig', action='store', help='Allows user to specify test config file')
    parser.add_argument('-ne', '--noemail', action='store_true', help='Do not send emails, overriding/ignoring setting in test config')
    parser.add_argument('-ss', '--showsummary', action='store_true', help='Show a testing summary upon the completion of each test list')
    parser.add_argument('-gr', '--generatereference', action='store_true', help='Instead of running testing, generate reference for each test list')
    args = parser.parse_args()

    if args.testconfig:
        if os.path.exists(args.testconfig):
            testConfigFile = args.testconfig
        else:
            print 'Fatal Error, failed to find user specified test config file ' + args.testconfig
            sys.exit(1)

    testConfig = open(testConfigFile)
    contents = file.read(testConfig)
    argStartIndex = contents.find('{')
    testResults = []
    while argStartIndex != -1 :
        argEndIndex = contents.find('}')
        argString = cleanupString(contents[argStartIndex + 1 : argEndIndex])
        argList = argString.split(',')
        if len(argList) < 5:
            print 'Error: only found ' + str(len(argList)) + ' args. Need at least 5 (refDir, testList, repoSrc, repoDst, repoBranch)'
            continue

        refDir = argList[0].strip()
        testList = argList[1].strip()
        repoSrc = argList[2].strip()
        repoDst = argList[3].strip()
        pullBranch = argList[4].strip()

        #clone repo and move into test dir
        cloneRepo(repoSrc, repoDst, pullBranch)
        prevWorkingDir = os.getcwd()
        workingDir = repoDst + '\\Test'
        os.chdir(workingDir)

        #run tests
        testingResults = RunAllTests.main(True, args.showsummary, args.generatereference, refDir, testList, pullBranch)
        #testing results is list of lists 
        for result in testingResults:
            setInfo = TestSetInfo(workingDir, testList, result[0], result[1], repoSrc, pullBranch)
            testResults.append(setInfo)

        #move out of repo back to previous location
        os.chdir(prevWorkingDir)

        #advance buffer to the next test config
        contents = contents[argEndIndex + 1 :]
        argStartIndex = contents.find('{')

    if not args.noemail and not args.generatereference:
        body = 'Ran ' + str(len(testResults)) + ' test sets:\n'
        attachments = []
        anyFails = False
        for r in testResults:
            attachments.append(r.summaryFile)
            if not r.passedTests:
                anyFails = True
                result = 'Fail'
            else:
                result = 'Success'
            body += r.testDir + '\\' + r.testList
            if r.pullBranch:
                body += ' (' + r.repoSrc + ' ' + r.pullBranch + ') '
            body += ': ' + result + '\n'
        if anyFails:
            subject = '[FAIL]'
        else:
            subject = '[SUCCESS]'
        dateStr = date.today().strftime("%m-%d-%y")
        subject += ' Falcor automated testing ' + dateStr
        sendEmail(emailRecipientFile, subject, body, attachments)

if __name__ == '__main__':
    main()
