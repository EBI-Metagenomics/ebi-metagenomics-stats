Rscript -e "install.packages('ebimetagenomics',repos='https://mirrors.ebi.ac.uk/CRAN/',lib=unlist(strsplit(Sys.getenv('R_LIBS_USER'),.Platform\$path.sep))[1L])"

