## diversity.R
## Generate diversity information offline for a EMG project

#added arguments from script call
version = commandArgs(TRUE)[1] #pipeline version in an accepted version "3.0", "4.0", "4.1"
dir_name = commandArgs(TRUE)[2] #directory to use "cr_otus" for v3, 'taxonomy-summary for v4
file_ext = commandArgs(TRUE)[3] #extension for files to be considered "_otu_table.txt" for v3, "fasta.mseq.tsv" for v4
file_tag = commandArgs(TRUE)[4] #prefix for files: "" for v3, "SSU"/"LSU" for v4

# Simple check that we are in a project directory
currentdir = tail(strsplit(getwd(),'/')[[1]],n=1)
if ((nchar(currentdir) != 9) | (substr(currentdir,3,3) != "P"))
    stop("This script must be run from a project directory")
## Drop into directory containing the run folders
setwd(version)
## Load required libraries
library(ebimetagenomics)

## Run on a project
## Assuming current directory contains run folders...
dirlist = grep("??R??????_FASTQ",list.dirs(recursive=FALSE),value=TRUE)
tab = NULL
#added to create a tag for file ("SSU"/"LSU" for v4)
if (nchar(file_tag) > 2)
    {out_file_tag=paste(file_tag,"_", sep ="")
} else {out_file_tag = file_tag}

for (dir in dirlist) {
    dirname = strsplit(dir,.Platform$file.sep)[[1]][-1]
    run = strsplit(dirname,'_')[[1]][1]
    #added the file tag if there is subfolder (none for v3, "SSU/" or "LSU/" for v4
    otufile = file.path(dirname,paste(dir_name,file_tag,sep="/"),
                        paste(dirname,file_ext,sep=""))
    if (! file.exists(otufile)) {
       ## message(paste("Skipping", run))
        cat("Skipping ",run,"\n",sep="")
        next
    }
    message(run)
    tryCatch({
        otu = read.otu.tsv(otufile)
        svg(paste(run,"svg",sep="."))
        summ = analyseOtu(otu)
        dev.off()
        tab = rbind(tab,summ)
        rownames(tab)[dim(tab)[1]] = run
        #added the suffix ("SSU"/"LSU") to the tad plot files
        file.rename(from=paste(run,"svg",sep="."),
                    to=file.path(dirname,"charts",paste(out_file_tag,"tad-plots.svg",sep="")))
       cat("Processed ",run,"\n",sep="")
    }, error = function(cond) {if (file.exists(paste(run,"svg",sep="."))) file.remove(paste(run,"svg",sep=".")); cat("Failed on run ",run,": ",cond,"\n",sep="")})
}
#added the suffix ("SSU"/"LSU") to the diversity files
df=data.frame("Run"=rownames(tab),tab)
if (nrow(df)) {
    write.table(df,file.path("project-summary",paste(out_file_tag,"diversity.tsv", sep="")),
            sep="\t",row.names=FALSE)
}else
    message("No diversity data available")
#added the suffix ("SSU"/"LSU") to the message
cat("---Completed ",paste(currentdir,file_tag),"\n",sep="")


## eof


