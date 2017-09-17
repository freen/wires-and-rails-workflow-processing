# Install docker
# https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository
sudo apt-get update
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install -y docker-ce=17.06.2~ce-0~ubuntu

# Deploy key
ssh-keygen -t rsa -b 4096 -C "REPLACE@ME.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

sudo mkdir /app
sudo chown -R ubuntu:ubuntu /app
git clone git@github.com:freen/wires-and-rails-workflow-processing.git /app

# Create .env

sudo su -
cd /app
docker swarm init
docker stack deploy -c docker-compose.yml WARWP
