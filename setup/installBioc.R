userdir = unlist(strsplit(Sys.getenv('R_LIBS_USER'),.Platform$path.sep))[1L]
source('http://bioconductor.org/biocLite.R')
biocLite('phyloseq',lib=userdir)
biocLite('DESeq2',lib=userdir)

