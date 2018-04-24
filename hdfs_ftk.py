import sys

if sys.version_info < (2, 6, 0):
    sys.stderr.write("HDFS FTK requires python version 2.6 and above, please upgrade your python installation.")
    sys.exit(1)

def main():
    print("HADOOP FORENSICS FILE SYSTEM FORENSICS TOOL KIT")



if __name__ == "__main__":

    try:
        main()
    except Exception:
        raise
    except KeyboardInterrupt:
        print("Interrupted")