#!/bin/bash

# from docker website: https://docs.docker.com/engine/install/ubuntu/
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
"deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# sudo docker run hello-world

sudo update-alternatives --config iptables

echo \
'if grep -q "microsoft" /proc/version > /dev/null 2>&1; then
    if service docker status 2>&1 | grep -q "is not running"; then
        wsl.exe --distribution "${WSL_DISTRO_NAME}" --user root \
            --exec /usr/sbin/service docker start > /dev/null 2>&1
    fi
fi' >> ~/.bashrc

# then activate the bashrc file with
source ~/.bashrc
sudo docker run hello-world


# sudo apt-get -y install apt-transport-https ca-certificates curl gnupg lsb-release
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
# sudo apt-get -y install docker-ce docker-ce-cli containerd.io

# REF
# [1]: https://askubuntu.com/questions/1030179/package-docker-ce-has-no-installation-candidate-in-18-04
# [2]: https://www.paulsblog.dev/how-to-install-docker-without-docker-desktop-on-windows/
# [3]: https://nickjanetakis.com/blog/install-docker-in-wsl-2-without-docker-desktop