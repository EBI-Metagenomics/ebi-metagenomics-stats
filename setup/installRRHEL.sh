# This script works for Fedora, but may need tweaking for RHEL
# Really NEED R 3.4.x - the subsequent R package installations
# won't work otherwise

sudo yum -y update
sudo yum -y install R libxml2-devel libcurl-devel

