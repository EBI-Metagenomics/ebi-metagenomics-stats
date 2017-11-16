echo "deb http://cran.rstudio.com/bin/linux/debian stretch-cran34/" >> /etc/apt/sources.list
apt-get update
apt-get -y upgrade
apt-get -y install r-base libopenblas-base

