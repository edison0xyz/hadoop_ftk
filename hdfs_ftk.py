import sys
import argparse

# Global variable
VERSION = 1.0
OUTPUT_FILE_SPECIFIED = False
output_directory = ''
verbosity = False


if sys.version_info < (3, 0, 0):
    sys.stderr.write("HDFS FTK requires python version 3.0 and above, please upgrade your python installation.")
    sys.exit(1)

def vwrite(x):
    print(verbosity)
    if verbosity:
        sys.stdout.write(x)


def parse_arguments(self, args):
    print(args.verbose is not None)

    if args.verbose is not None:
        verbosity = True

    if args.o is not None:
        output_directory = args.o
        vwrite("Output directory: " + output_directory)
        OUTPUT_FILE_SPECIFIED = True

    if args.d is not None:
        for i in range(args.d):
            sys.stdout.write("Path to Device {0}\n".format(i))

    sys.stderr.write(args.f)


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