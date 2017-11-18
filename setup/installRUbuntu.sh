echo "https://cran.rstudio.com/bin/linux/ubuntu artful/" >> /etc/apt/sources.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9
apt-get update
apt-get -y upgrade
apt-get -y install r-base libopenblas-base libcurl4-openssl-dev libxml2-dev

