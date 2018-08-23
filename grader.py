#!/usr/bin/python


# IMPORT
#-------
from xml.dom import minidom
import subprocess       # Popen
import os               # os.listdir
import zipfile          # 
import shutil           # To copy files
import glob             # Get all files matching pattern (with wildcards)



# FILE: input/output
# ------------------
def writeStringToFile(filename, string):
    '''Write "string" to "filename"'''

    text_file = open(filename, 'w')
    text_file.write(string)
    text_file.close()



# ZIP: Manupulation, unzip...
# ---------------------------
def getZipFileList(directory):
    '''Compile a list of zip files in the given directory'''

    return filter(lambda x: x.endswith('.zip'), os.listdir(directory))



def isValidZipFile(filename):
    '''Test whether the given file is a valid zip file or not'''

    return zipfile.is_zipfile(filename)



def getFilenamesFromZip(filename):
    '''Extract files in the given zipfile (with filename)'''

    return zipfile.ZipFile(filename, "r").namelist()
   


def extractFromZip(filename, directory):
    '''Extract files from "filename" into "directory"'''
    
    zipfile.ZipFile(filename, "r").extractall(directory)



# XML and DOM
# -----------
def xmlToDOM(filename, tagname):
    '''Given a filename and a root type node (e.g. "assignment" for "./assignment.xml")
    return the root node of that document'''

    doc = minidom.parse(filename)
    if doc.documentElement.nodeName != tagname:
        print "Incorrect root node %s\n" % tagname
        exit()

    return doc.documentElement 



def getUniqueNode(node, tagname, recursive = False, error = True):
    '''Retrieve one single node from a xml document object. Error out if there is more than one'''

    node_list = node.getElementsByTagName(tagname)

    # If not recursive, filter out the nodes not on the next level
    if not recursive:
        node_list = [element for element in node_list if element.parentNode == node]
    
    if error:
        if len(node_list) != 1:
            print "Node %s: invalid number of child nodes (%i) with tag = %s\n" % (node.nodeName, len(node_list), tagname)
            exit()

    return node_list[0]



def getNodeList(node, tagname):
    '''Retrieve all nodes with the given tag name from an xml document object'''

    return node.getElementsByTagName(tagname)



def getTextFromNode(node):
    '''Return the text stored for this node'''

    return node.childNodes[0].nodeValue



def renameZipFiles(zipfile_list):
    '''Remove all non-ascii characters from zip file names'''
    
    new_zipfile_list = []
    # get rid of non-ascii characters added by Moodle (tildes and the like)
    for filezip in zipfile_list:
        filezip = filezip.decode('utf-8')
        ascii_filezip = filezip.encode('ascii', 'ignore')
        os.rename(filezip, ascii_filezip)
        new_zipfile_list.append(ascii_filezip)
        
    return new_zipfile_list
    


# CLASSES
# -------
class Student:
    '''A class that holds all the data about a student'''

    def __init__(self, node):
        self.loadFromNode(node)

    def loadFromNode(self, node):
        '''Read the Student data'''

        self.name      = getTextFromNode(getUniqueNode(node, "name")) 
        self.lastname  = getTextFromNode(getUniqueNode(node, "lastname")) 
        self.username  = getTextFromNode(getUniqueNode(node, "username")) 
        self.searchfor = getTextFromNode(getUniqueNode(node, "searchfor"))

    def getString(self):

        aString =  "student.name      = %s\n" % self.name
        aString += "student.lastname  = %s\n" % self.lastname
        aString += "student.username  = %s\n" % self.username
        aString += "student.searchfor = %s\n" % self.searchfor

        return aString


    def __str__(self):

        return self.getString()



class Cohort:
    '''A container class for a group of students'''

    def __init__(self, node):
        self.loadFromNode(node)


    def loadFromNode(self, node):
        '''Process a list of student objects'''

        self.students = []

        student_node_list = getNodeList(node, "student")

        for student_node in student_node_list:
            student = Student(student_node)
            self.students.append(student)


    def getString(self):
        aString = ""
        for student in self.students:
            aString += student.getString()

        return aString


    def __str__(self):

        return self.getString()



class Class:
    '''A class object'''

    def __init__(self, node):
        self.loadFromNode(node)


    def loadFromNode(self, node):
        '''Process a list of student objects'''

        self.name              = getTextFromNode(getUniqueNode(node, "id")) 
        self.session           = getTextFromNode(getUniqueNode(node, "session")) 
        self.year              = getTextFromNode(getUniqueNode(node, "year")) 
        self.network_directory = getTextFromNode(getUniqueNode(node, "network_directory"))


    def __str__(self):
        aString =  "class.name              = %s\n" % self.name
        aString += "class.session           = %s\n" % self.session
        aString += "class.year              = %s\n" % self.year
        aString += "class.network_directory = %s\n" % self.network_directory

        return aString



class Assignment:
    '''An assignment object'''

    def __init__(self, node):
        self.loadFromNode(node)


    def loadFromNode(self, node):
        '''Process a list of student objects'''

        #Name
        self.name = getTextFromNode(getUniqueNode(node, "name"))

        #Files submitted
        tosubmit_node = getUniqueNode(node, "tosubmit")
        self.tosubmit = []
        files_node_list = getNodeList(tosubmit_node, "file")
        for file_node in files_node_list:
            self.tosubmit.append(getTextFromNode(file_node))

        #Files provided
        tocopy_node = getUniqueNode(node, "tocopy")
        self.tocopy_directory = getTextFromNode(getUniqueNode(tocopy_node, "directory"))
        self.tocopy = []
        files_node_list = getNodeList(tocopy_node, "file")
        for file_node in files_node_list:
            self.tocopy.append(getTextFromNode(file_node))

        #Jobs
        self.jobs    = []
        job_node_list = getNodeList(node, "job")

        for job_node in job_node_list:
            job = Job(job_node)
            self.jobs.append(job)

    
    def getString(self):
        aString =  "assignment.name     = %s\n" % self.name

        aString += "assignment.tosubmit = "
        aString += ', '.join(self.tosubmit) + "\n"

        aString += "assignment.tocopy_directory = %s\n" % self.tocopy_directory

        aString += "assignment.tocopy   = "
        aString += ', '.join(self.tocopy) + "\n"

        for job in self.jobs:
            aString += job.getString()

        return aString


    def __str__(self):

        return self.getString()



class Job:
    '''A class to encapsulate jobs'''

    def __init__(self, node):
        self.loadFromNode(node)

    def loadFromNode(self, node):
        '''Read job data'''

        self.name        = getTextFromNode(getUniqueNode(node, "name"))
        self.description = getTextFromNode(getUniqueNode(node, "description"))
        self.outputfile  = getTextFromNode(getUniqueNode(node, "outputfile"))
        self.command     = getTextFromNode(getUniqueNode(node, "command"))
           

    def run(self):
        '''Function to execute this job. It returns whether it failed or succeded, and the output: the command's 
        output or the error, respectively'''

        # Output
        successful       = True
        output_string = ""

        #DEBUG: start
        print "Running %s" % self.name
        print "Command: '%s'" % self.command
        print "PWD: '%s'" % os.getcwd()
        #DEBUG: end

        '''
        exec_process = subprocess.Popen(self.command,
                                        shell = True,
                                        stdout = subprocess.PIPE,
                                        stderr = subprocess.PIPE,
                                        bufsize = 0)
        exec_output = exec_process.communicate()
        exec_stdout = exec_output[0]
        exec_stderr = exec_output[1]
        '''
        fileout = open(self.outputfile, 'w')
        
        exec_process = subprocess.call(self.command, 
                                        stdout = fileout,
                                        stderr = fileout,
                                        shell = True)
        
        fileout.close();
        '''
        (exec_stdout, exec_stderr) = exec_process.communicate()
        if exec_stderr:
            successful = False
            output_string = exec_stderr
         
        if successful:
            output_string = exec_stdout

        writeStringToFile(self.outputfile, output_string)
        '''

        return successful


    def getString(self):
        aString =  "job.name        = %s\n" % self.name
        aString += "job.description = %s\n" % self.description
        aString += "job.outputfile  = %s\n" % self.outputfile
        aString += "job.command     = %s\n" % self.command

        return aString


    def __str__(self):

        return self.getString()



class GradingManager:
    '''A class to coordinate the grading of an assignment for a given cohort'''

    report_dir = "report"

    def __init__(self, aclass, cohort, assignment):
        
        self.aclass     = aclass
        self.cohort     = cohort
        self.assignment = assignment

    
    def deploy(self, student):
        '''Check presence of student's zip file, uncompress it, check presence of files to be submitted,
        extract the files to be submitted to the students own directory (./'username'/), copy the files
        required for grading'''

        id_string = student.name + " " + student.lastname
        print id_string + ": deploy"

        # compile list of zip files in directory and remove non-ascii characters added by moodle
        zipfile_list = renameZipFiles(getZipFileList("./"))

        # find student's zip file
        student_zip = next((zipfile.decode('UTF-8') for zipfile in zipfile_list if zipfile.find(student.searchfor) != -1), "")
        if student_zip == "":
            print id_string + ": zip file not found (searched for {})".format(student.searchfor)
            return False

        # test whether the file is a valid zip file
        if not isValidZipFile(student_zip):
            print id_string + ": invalid format of zipfile {}".format(student_zip)
            return False
        
        # extract files from the (already tested) valid zip file
        submitted_files = getFilenamesFromZip(student_zip)
        print id_string + ": Files submitted"
        print ', '.join(submitted_files)

        # check whether all the files to be submitted are there
        if (len(submitted_files) != len(self.assignment.tosubmit)):
            print "%i file submitted, %i files expected" %(len(submitted_files), len(self.assignment.tosubmit))
            return False
        for afile in self.assignment.tosubmit:
            if afile not in submitted_files:
                print afile + " not present in submission"
                return False

        # create student directory path
        student_dir = "./" + student.lastname + "." + student.name

        # unzip into students directory
        extractFromZip(student_zip, student_dir)        

        # copy the assignment master files into the students directory
        for filename in self.assignment.tocopy:
            for afile in glob.glob("./tocopy/" + filename):
                shutil.copy(afile, student_dir)

        return True


    def publish(self, username):
        '''Copy the results of the grading process to the network drive'''

        print "%s: publish: Copy results to %s-%s-%s-%s/%s" % (username, self.aclass.name, self.aclass.session, self.aclass.year, self.assignment.name, username)
        
        # create report directory (to store all the output)
        os.chdir(username)

        if not os.path.exists(self.report_dir):
                os.makedirs(self.report_dir)
        
        for job in self.assignment.jobs:
			shutil.copy(job.outputfile, self.report_dir)
			os.remove(job.outputfile)

        os.chdir("../")

    def grade(self):
        '''Deploy, test and publish'''

        for student in self.cohort.students:
            print "--------------------------"
            # if deployment successful
            if self.deploy(student):
                student_dir = "./" + student.lastname + "." + student.name
                # run all jobs
                os.chdir(student_dir)
                for job in self.assignment.jobs:
                    job.run()
                os.chdir("../")
                # publish all results
                self.publish(student.lastname + "." + student.name)
            print "--------------------------\n"



def main():
    '''Test reading an class object from an XML object'''

    cohort = Cohort(xmlToDOM("./cohort.xml", "cohort"))
    aclass = Class(xmlToDOM("./class.xml", "class"))
    assignment = Assignment(xmlToDOM("./assignment.xml", "assignment"))

    #DEBUG
    #print cohort
    print aclass
    print assignment

    grading_manager = GradingManager(aclass, cohort, assignment)
    grading_manager.grade()


if __name__ == "__main__":
        main()



