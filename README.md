# Introduction
This is the project for the Udacity Full Stack Web Developer course for the Linux servers module.

# How to use
URL: http://18.221.121.139/ (no longer active)
2 apps to choose: Flask WSGI and static Google Map project
Logging in via OAuth doesn't work because Google doesn't allow IP URLs for callbacks

# How to connect
18.221.121.139:2200 (no longer active)
key will be provided in the reviewer notes

## Configure steps

1. Update all currently installed packages

sudo apt-get update
sudo apt-get upgrade

2. Change the SSH port from 22 to 2200
- Edit /etc/ssh/sshd_config to change Port 22 to Port 2200
- restart SSH using `sudo service ssh restart`

3. Configure the Uncomplicated Firewall (UFW)
- sudo ufw default deny incoming
- sudo ufw default allow outgoing
- sudo ufw allow www
- sudo ufw allow 2200/tcp
- sudo ufw allow 123/tcp
- sudo ufw status
- sudo ufw enable
- sudo ufw status

4. Create grader user
- sudo adduser grader
- add grader file in /etc/sudoers.d
- sudo ssh-keygen and put files in ~grader/.ssh

5. Install Linux Packages
- apache2
- sqlite3 (catalog used sqlite)
- python
- libapache2-mod-wsgi
- pip

6. PIP installs
- httplib2
- flask
- requests
- sqlalchemy
- passlib
- oauth2client
- flask_httpauth

7. Configure apache
- setup WSGI in conf: /etc/apache2/sites-available/000-default.conf
- restart server: sudo apachectl restart
