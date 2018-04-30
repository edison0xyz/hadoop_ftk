import sys, os, glob
import argparse
import xml.etree.ElementTree
from prettytable import PrettyTable
import shutil

# Debug
DEBUG = True # When debugging mode is switched on, script will run with sample values from the test/ directory.


# Global variable
VERSION = 1.0
OUTPUT_FILE_SPECIFIED = False
output_directory = ''
verbosity = False
fsimage_path = ''
datanodes = [] # paths to the datanodes
SEARCH_TERM = ''

SHOW_DIRECTORY = True # enabled by default
SHOW_FILES = True # enabled by default 

if sys.version_info < (3, 0, 0):
    sys.stderr.write("HDFS FTK requires python version 3.0 and above, please upgrade your python installation.")
    sys.exit(1)


def vwrite(x):

    if verbosity:   # write to console only if verbosity is switched on
        sys.stdout.write(x)
        sys.stdout.write("\n")
        sys.stdout.flush()



def dump_file(block_id):
    vwrite("DUMP_FILE: Attempting to extract from block id: " + block_id)

    vwrite("Traversing through " + str(datanodes))

    # validity check on datanodes
    vwrite("Checking datanodes' path validity...")
    cnt = 0
    for data_path in datanodes:
        flag = "Valid" if os.path.isdir(data_path) else "Not valid"
        if os.path.isdir(data_path) is False:
            cnt += 1
        vwrite(data_path + " : " + flag)

    if cnt < len(datanodes):
        print("Number of valid datanode path: " + str(len(datanodes) - cnt) + " / " + str(len(datanodes)))
    else:
        sys.stderr.write("All datanodes path are not valid. No data to lookup from. Aborting.")
        sys.stderr.flush()
        sys.exit(1)

    # to write
    vwrite("Finding file with block id: " + block_id)
    for path in datanodes:
        matches = []
        for dirpath, subdirs, files in os.walk(path):
            for x in files:
                if block_id in x and '.meta' not in x:
                    matches.append(os.path.join(dirpath, x))

    if len(matches) == 0:        
        sys.stderr.write("No matches found.")
        sys.stderr.flush()
        sys.exit(1)
    else:
        # copy to output directory
        cnt = 0
        for match in matches:
            shutil.copy2(match, output_directory)
            cnt += 1
    print(str(cnt) + " files extracted successfully into " + output_directory)

def recover(id_no):
    vwrite("Recovering ID: " + id_no)

    # construct tree from xml document
    e = xml.etree.ElementTree.parse(fsimage_path).getroot()  # root of xml tree
    inode_section = e[1]  # get inode_section which contains information about the inodes
    for inode in inode_section.findall('inode'):
        identifier = inode[0].text

        if identifier == id_no:
            vwrite("Identifier matches the given inode (inode: " + id_no + ")")

            # check for file type; throws error and exit program if directory recovery is attempted
            file_type = inode[1].text  # Type
            if file_type == 'DIRECTORY':
                sys.stderr.write("You are attempting to recover a directory. "
                                 "HDFS FTK only supports file extraction at this moment!")
                sys.exit(1)  # exit program

            for block in inode.findall('blocks'):
                # each <block> contains block_id, nuimBytes and genStamp
                block_id = block[0][0].text  # get block_id
                vwrite("Retrieving from block id: " + block_id)  # retrieve if found
                dump_file(block_id) # find file and dump to output directory


def print_fsimage_info():
    e = xml.etree.ElementTree.parse(fsimage_path).getroot()
    entries = []

    inode_section = e[1]  # get inode_section which contains information about the inodes
    for inode in inode_section.findall('inode'):
        identifier = inode[0].text
        file_type = inode[1].text  # Type
        file_name = inode[2].text  # Name
        # modified_time =  inode[4].text # modified time
        file_size = ''
        if file_name is None:
            file_name = '/'  # root node

        # extracting block level details
        for block in inode.findall('blocks'):
            # each <block> contains block_id, numBytes and genStamp
            file_size = block[0][2].text  #numbytes
        if SEARCH_TERM in file_name:
            if SHOW_DIRECTORY and "DIRECTORY" in file_type:
                entries.append([identifier, file_type, file_name, file_size])
            if SHOW_FILES and "FILE" in file_type:
                entries.append([identifier, file_type, file_name, file_size])
            

    # Output data in a pretty pretty table
    t = PrettyTable(['iNode', 'Type', 'Name', 'Size (in bytes)'])
    for entry in entries:
        t.add_row(entry)
    print(t)
    print("To recover a file for ID: n, append `-r n` and specify an output folder through `-o /output_directory`")
    print("Example command: python hdfs_ftk.py -f fsimage -r 16300 -o /output_directory/ -d 3")


def parse_arguments(args):

    if args.verbose is True:
        print("Verbose mode on.")
        global verbosity
        verbosity = True


    # Get fsimage path
    global fsimage_path
    fsimage_path = args.f
    if DEBUG:
        fsimage_path = 'test/fsimage.xml'  # testing fsimage path

    # check if file exists

    if os.path.isfile(fsimage_path) is False:
        sys.stderr.write("fsimage file not found. Exiting..")
        sys.stderr.flush()
        sys.exit(1)


    # extract output directory
    if args.o is not None:
        global output_directory
        output_directory = args.o
        if DEBUG:
            output_directory = 'test/output/'
        OUTPUT_FILE_SPECIFIED = True
        if os.path.isdir(output_directory) is False:
            vwrite("Directory not found. Attempting to make directory.")
            os.mkdir(output_directory)
            if os.path.isdir(output_directory) is False:
                sys.stderr.write("Unable to make directory. Check your permissions or directory, perhaps? Exiting. ")
                sys.exit(1)
            else:
                vwrite("Directory " + output_directory + "successfully created.")

    # Verbosity display info
    vwrite("FSImage path: " + fsimage_path)
    vwrite("Output directory: " + output_directory)

    # filters arguments
    if args.filterByName is not None:
        global SEARCH_TERM
        SEARCH_TERM = args.filterByName
        vwrite("ARGS: SEARCH FILE SPECIFIED: " + SEARCH_TERM)

    global SHOW_DIRECTORY, SHOW_FILES
    
    if args.showfilesonly and args.showdironly is True:
        sys.stderr.write("Showing both directory and files")
    elif args.showfilesonly is True:
        SHOW_DIRECTORY = False
    elif args.showdironly is True:
        SHOW_FILES = False

    # Show fsimage info
    if args.displayfsimage is True:
        print_fsimage_info()
        sys.exit(1)




    if args.d is not None:
        global datanodes
        vwrite("Number of datanodes specified: " + str(args.d))

        for i in range(args.d):
            data_path = input('Path to device {}: '.format(i+1))
            sys.stdout.flush()
            datanodes.append(data_path)

        if DEBUG:
            datanodes = [
                'test/datanode1',
                'test/datanode2',
                'test/datanode3'
            ]
        vwrite("Data nodes added: " + str(datanodes))
    if args.r is not None:
        recover(args.r)


def main():
    # Get the version information on every output from the beginning
    # Exceptionally useful for debugging/telling people what's going on
    sys.stderr.write("Hadoop Forensics File System Forensics Tool Kit (HDFS FTK) ver. {0}\n".format(VERSION))
    sys.stderr.flush()

    if DEBUG:
        print("DEBUG MODE ON: Test values will be used for fsimage, output and datanode directories.")

    # parser set-up
    parser = argparse.ArgumentParser(description='HDFS Forensics Toolkit.')

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument("-displayfsimage", action="store_true", help="Print out fsimage table")
    parser.add_argument("-showfilesonly", action="store_true", help="Show files only")
    parser.add_argument("-showdironly", action="store_true", help="Show directories only")

    parser.add_argument("-filterByName", help="Filter fsimage display by filename")

    parser.add_argument("-d", type=int,
                        help="Number of Datanodes")
    parser.add_argument("-o", "-output",
                        help="output directory")
    parser.add_argument("-r", "-recover",
                        help="Recover file given ID number")
    requiredNamed = parser.add_argument_group('Required named arguments')
    requiredNamed.add_argument("-f", required=True,
                        help="Path to fsimage") # fsimage is a required filed
    args = parser.parse_args()
    parse_arguments(args)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise
    except KeyboardInterrupt:
        print("Interrupted")
