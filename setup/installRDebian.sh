echo "deb http://cran.rstudio.com/bin/linux/debian stretch-cran34/" >> /etc/apt/sources.list
apt-key adv --keyserver keys.gnupg.net --recv-key 'E19F5F87128899B192B1A2C2AD5F960A256A04AF'
apt-get update
apt-get -y --allow-unauthenticated upgrade
apt-get -y --allow-unauthenticated install r-base libopenblas-base libcurl4-openssl-dev libxml2-dev 

