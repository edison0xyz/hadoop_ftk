import sys
import argparse
import xml.etree.ElementTree
from prettytable import PrettyTable


# Global variable
VERSION = 1.0
OUTPUT_FILE_SPECIFIED = False
output_directory = ''
verbosity = False
fsimage_path = ''


if sys.version_info < (3, 0, 0):
    sys.stderr.write("HDFS FTK requires python version 3.0 and above, please upgrade your python installation.")
    sys.exit(1)


def vwrite(x):

    if verbosity:   # write to console only if verbosity is switched on
        sys.stdout.write(x)
        sys.stdout.write("\n")
        sys.stdout.flush()


'''
def dump_file(block_id):
    # to write

'''

def recover(id_no):
    vwrite("Recovering ID: " + id_no)

    # construct tree from xml document
    e = xml.etree.ElementTree.parse(fsimage_path).getroot()
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
                sys.exit(1) # exit program

            for block in inode.findall('blocks'):
                # each <block> contains block_id, nuimBytes and genStamp
                block_id = block[0][0].text  # get block_id
                vwrite("Retrieving from " + block_id)  # retrieve if found
                # dump_block_to_file(block_id) # find file and dump to output directory


def print_fsimage_info():
    e = xml.etree.ElementTree.parse(fsimage_path).getroot()
    entries = []

    inode_section = e[1]  # get inode_section which contains information about the inodes
    for inode in inode_section.findall('inode'):
        identifier = inode[0].text
        file_type = inode[1].text  # Type
        file_name = inode[2].text  # Name
        modified_time =  inode[4].text # modified time
        file_size = ''
        if file_type == 'FILE':
            file_size = inode[6].text  # Name

        if file_name is None:
            file_name = '/'

        # extracting block level details
        for block in inode.findall('blocks'):
            # each <block> contains block_id, nuimBytes and genStamp
            file_size = block[0][2].text
        entries.append([identifier, file_type, file_name, file_size])



    # Output data in a pretty pretty table
    t = PrettyTable(['iNode', 'Type', 'Name', 'Size (in bytes)'])
    for entry in entries:
        t.add_row(entry)
    print(t)
    print("To recover a file for tag no. n, append `-tag n` and specify an output folder through `-o /output_directory`")


def parse_arguments(args):

    if args.verbose is True:
        print("Verbose mode on.")
        global verbosity
        verbosity = True

    # extract path to fsimage
    global fsimage_path
    fsimage_path = 'test/fsimage2.xml'
    #fsimage_path = args.f
    vwrite("FSImage path: " + fsimage_path)

    if args.o is not None:
        output_directory = 'test/output/'
        #output_directory = args.o
        vwrite("Output directory: " + output_directory)
        OUTPUT_FILE_SPECIFIED = True

    if args.d is not None:
        for i in range(args.d):
            sys.stdout.write("Path to Device {0}\n".format(i))
    if args.r is not None:
        recover(args.r)


def main():
    # Get the version information on every output from the beginning
    # Exceptionally useful for debugging/telling people what's going on
    sys.stderr.write("Hadoop Forensics File System Forensics Tool Kit (HDFS FTK) ver. {0}\n".format(VERSION))
    sys.stderr.flush()

    # parser set-up
    parser = argparse.ArgumentParser(description='HDFS Forensics Toolkit.')

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")

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

    print_fsimage_info()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise
    except KeyboardInterrupt:
        print("Interrupted")