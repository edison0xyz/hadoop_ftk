# Hadoop File System Forensics Toolkit (HDFS FTK)
View and extract files from an offline image of Hadoop file system.

Supports:
* Support for multiple datanodes
* Support of fsimage XML format
* Search filenames and filter by filetype
* File recovery while preserving metadata


### Motivation
In Hadoop File Systems, metadata such as filename, access time and file system hierachy information is stored in the namenode. The actual data is stored in the datanodes in _blocks_. Although HDFS has command client tools to manage the extraction files, it only works with a running cluster of HDFS machines.
This python script aims to provide investigators with the ability to perform forensics analysis of offline evidence captures of Hadoop File System images.

## Instructions

### PreRequisites
* Python 3.x
* PrettyTable: `pip install prettytable`

### Usage

```
Hadoop Forensics File System Forensics Tool Kit (HDFS FTK) ver. 1.0
DEBUG MODE ON: Test values will be used for fsimage, output and datanode directories.
usage: hdfs_ftk.py [-h] [-v] [-displayfsimage] [-showfilesonly] [-showdironly]
                   [-filterByName FILTERBYNAME] [-d D] [-o O] [-r R] -f F

HDFS Forensics Toolkit.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode
  -displayfsimage       Print out fsimage table
  -showfilesonly        Show files only
  -showdironly          Show directories only
  -filterByName FILTERBYNAME
                        Filter fsimage display by filename
  -d D                  Number of Datanodes
  -o O, -output O       output directory
  -r R, -recover R      Recover file given ID number

Required named arguments:
  -f F, -fsimage F      Path to fsimage

```

#### Example commands:

* To view contents of HDFS File System: `python hdfs_ftk.py -f fsimage.xml`
* Display fsimage: `python hdfs_ftk.py -f test/fsimage.xml -displayfsimage`
* Extract block id `16386` from HDFS with three datanodes: `python hdfs_ftk.py -f test/fsimage.xml -v -r 16386 -o /output -d 3`

#### Demo videos
* Extracting files and displaying fsimage information: https://youtu.be/I1I08ixInxI


### License
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

## Future works
* Large file recovery: Files more than the blocksize specified in the configurations are broken into several blocks. This tool is unable to recover large data files.