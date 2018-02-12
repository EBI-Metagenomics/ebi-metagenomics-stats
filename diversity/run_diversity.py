#!/usr/bin/env python3

import subprocess
import tempfile
import shutil
import re
import os
import sys
import argparse
import json

__author__ = 'hudenise, scp 2018'


def parameters_according_to_version(pv):
    '''
    function to set parameters according to the pipeline version
    input pipeline version
    return list_arg: list of file names containing the otu counts and associated lineages
    return file_name: 14 characters extension for the files containing the otu counts and associated lineages
    return dirs: list of the names of directory where diversity.tsv and tad.svg files will be stored once created
    return extension: number of extra characters that need to be added to the 14 (see file_name) to get file names
    return dir_type: name of directory where the files containing the otu counts and associated lineages are stored
    '''
    list_arg = []
    extension=0
    dirs = ['project-summary','charts']
    if pv == '3.0':
       file_name = "_otu_table.txt"
       dir_type = "cr_otus"
       list_arg.append(file_name)
    if pv == '4.0' or pv == '4.1':
       file_name = "fasta.mseq.tsv"
       extension = 5
       dir_type = "taxonomy-summary"
       list_arg.append("_SSU."+file_name)
       list_arg.append("_LSU."+file_name)
    return list_arg, file_name, dirs, extension, dir_type

def create_destination_structure (source_path, dest_path, version):
    '''
    function to generate the accepted structure in the destination directory if this option is precised
    input source_path: path to original result directory
    input dest_path: path to destination directory (provided with -d option)
    input version: pipeline version
    return new_dest_path: destination path with study_id
    return final_dest_path: destination path with study_id and pipeline version
    '''
    study_id = source_path.split("/")[-1]
    new_dest_path = create_new_path (study_id, dest_path)
    final_dest_path =  create_new_path (version, new_dest_path)
    return new_dest_path, final_dest_path

def create_new_path (new_folder, given_path):
    '''
    function to check if path exist to a folder and create it if not present
    input: new_folder: folder to look for in the given path
    input: given_path: path to directory where to look for the new_folder
    return new_path: path to given_path with new_folder
    '''
    if not os.path.exists(os.path.join(given_path,new_folder)):
         os.mkdir (os.path.join(given_path,new_folder))
    new_path = os.path.join(given_path,new_folder)
    return new_path

def run_ids_from_paths(path, pv):
    '''
    function to extract the run_id to consider from path obtained by os.walk
    input path to each file
    input pv: pipeline version
    return run_id
    '''
    pr = re.compile('.*version_'+pv + '/(.*?)/')
    m = pr.match(path)
    return m.group(1)

def get_files (path, dest, pv):
    '''
    function to get the path to the files and parameters according to the pipeline version
    input path to the result directory
    input pv pipeline version
    no return
    call the run_diversity function
    '''
    allruns = []
    os.chdir(path)
    otufiles = []
    out_dirs = []
    subfolder =""
    list_arg, file_name, dirs, extension, dir_type = parameters_according_to_version(pv)

    for filetype in list_arg:
        for root, dirs, files in os.walk('.'):
            if "/" in root:
                version=root.split("/")[1]
                if "_"+pv in version:
                    for file in files:
                        if file[-14-extension:] == filetype:
                             fn = os.path.join(root, file)
                             otufiles.append(fn)
                             allruns.append(run_ids_from_paths(fn, pv))
                    for dir in dirs:
                        if dir in dirs:
                             out_dirs.append(os.path.join(root, dir))
        if pv.find("4.") != -1:
            subfolder = filetype[1:4]
        run_diversity(otufiles, allruns, out_dirs, path, dest, pv, dir_type, filetype, subfolder)
 
def run_diversity(otu_files, runs, outdirs, path, dest, version, dir_type, file_name, nametag):
    '''
    function to run the R script in order to generate the diversity.tsv and tag.svg representations
    input otu_files: list of otu files, with their path
    input runs: list of runs to consider
    input outdirs: list of output directories with their path
    input path: path to the project directory
    input version: version of EMG pipeline
    input dir_type: name of directory where the files containing the otu counts and associated lineages are stored
    input file_name: 14 characters extension for the files containing the otu counts and associated lineages
    input nametag: prefix to add to file_names for v4 (SSU or LSU) to differenciate the diversity and tad.svg files. "" for v3
    no return
    call the diversity.R script
    '''
    tmpdir = tempfile.mkdtemp()
    os.chdir(path)
    os.chdir(tmpdir)
    projectname = os.path.abspath(path).split('/')[-1]
    os.makedirs(projectname)
    os.chdir(projectname)
    for file in otu_files:
        d = os.path.dirname(file)
        if not os.path.exists(d):
           os.makedirs(d)
        shutil.copyfile(os.path.join(path, file), os.path.join(file))
    for od in outdirs:
        if not os.path.isdir(od):
            os.makedirs(od)
    version="version_"+version
    #rv = subprocess.call([Rscript, diversity, version, dir_type, file_name, nametag])
    rv = subprocess.call([configSettings["Rscript"],configSettings["diversityR"], version, dir_type, file_name, nametag])
    outfiles = []
    project_tsv = False
#   project_pca = False
    passed_runs = set()
    if rv != 0:
        print('failure on project ' + path)
    else:
        for root, dirs, files in os.walk('.'):
            for file in files:
                # if file == 'pca.svg':
                #     project_pca = True
                #     fn = os.path.join(root, file)
                #     outfiles.append(fn)
                if file[-4:] == '.svg':
                    fn = os.path.join(root, file)
                    outfiles.append(fn)
                    passed_runs.add(run_ids_from_paths(fn, pv))
                if file[-13:] == 'diversity.tsv':
                    project_tsv = True
                    fn = os.path.join(root, file)
                    outfiles.append(fn)
    if not project_tsv:
        print(projectname + ":\tdiversity data not found")
    for run in runs:
        if not run in passed_runs:
            print(projectname + ":\tTAD plots not found")
    os.chdir(path)
    if path != dest:
         study_Dest, Dest = create_destination_structure (path, dest , version)
    else:
        Dest = path   
        study_Dest = path
    for file in outfiles:
        if not os.path.exists(os.path.join(dest, file)):
            file_dir = file.split("/")[2]
            new_Dest = create_new_path (file_dir, Dest)
            if file_dir != 'project-summary':
                 file_sub_dir = file.split("/")[3]
                 create_new_path (file_sub_dir, new_Dest)
            shutil.copyfile(os.path.join(tmpdir, projectname, file), os.path.join(study_Dest, file))
    shutil.rmtree(tmpdir)

acceptedPV = ['3.0','4.0','4.1']
parser = argparse.ArgumentParser(
            description="run_diversity.py is a wrapper to gather the files of interest and call the diversity.R script.\n"
                        "Command: run_diversity.py -s <path to project directory> -p <pipeline version> (options: -d <destination directory> -c <config file>.\n")
parser.add_argument("-s", "--source directory", help="path to project directory", required=True)
parser.add_argument("-pv", "--pipeline version", help="pipeline version in an accepted format ("+", ".join(acceptedPV)+")",
                        required=True)
parser.add_argument("-d","--destination directory", help="path to destination directory", required=False)
# Script access details
parser.add_argument("-c", "--config",
                        type=argparse.FileType('r'),
                        help="path to config file",
                        required=False,
                        metavar="configfile",
                        default="/hps/nobackup/production/metagenomics/production-scripts/diversity-config-prod.json")

args = vars(parser.parse_args())
config_file_path = args['config']
configSettings = json.load(config_file_path)
os.environ['R_LIBS_USER'] = configSettings["os_envi"]
#check that the path is correctly formatted
res_dir = configSettings["res_dir"]
if args["source directory"].startswith("/nfs"):
    res_dir = args["source directory"]
else:
    res_dir = os.path.join(res_dir, args["source directory"])
if res_dir.endswith("/") : res_dir = res_dir[:-1]
if args["destination directory"] and  args["destination directory"].startswith("/"):
    dest_dir =  args["destination directory"]
else: dest_dir = res_dir
#check the pipeline version
if str(float(args["pipeline version"])) in acceptedPV:
    pv = str(float(args["pipeline version"]))
else:
    print ("Please provide an acceptable pipeline version (currently :"+", ".join(acceptedPV)+").")
    sys.exit(1)
#run the diversity script. First get the files then call the R script 
get_files(res_dir, dest_dir, pv)

