userdir = unlist(strsplit(Sys.getenv('R_LIBS_USER'),.Platform$path.sep))[1L]
if (!file.exists(userdir))
    dir.create(userdir, recursive = TRUE)
install.packages(c('ebimetagenomics'),
                 repos='https://mirrors.ebi.ac.uk/CRAN/',
                 lib=userdir)

