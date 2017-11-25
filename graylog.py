from subprocess import call

# Install Necessary python modules
call(["apt", "-y", "install", "python3-colorama"])
call(["apt", "-y", "install", "python3-wget"])

from colorama import Fore, init
init(autoreset=True)
import wget
import fileinput

# Update repository
print(Fore.GREEN + "\n*** Running apt update command ***\n")
call(["apt", "update"])

# Upgrade packages
print(Fore.GREEN + "\n*** Running apt upgrade command ***\n")
call(["apt", "upgrade", "-y"])

# Install necessary packages for complete graylog setup
print(Fore.GREEN + "\n*** Installing necessary packages ***\n")
call(["apt", "-y", "install", "apt-transport-https", "openjdk-8-jre-headless", "uuid-runtime", "pwgen"])

# Install Elasticsearch locally
elasticsearch_answer = input("\nWould you like Elasticsearch installed locally? ").lower()
if elasticsearch_answer.startswith('y'):
  print(Fore.GREEN + "\n*** Installing Elasticsearch ***\n") 
  call(["wget", "https://artifacts.elastic.co/GPG-KEY-elasticsearch"])
  call(["apt-key", "add", "GPG-KEY-elasticsearch"]) 
  with open('/etc/apt/sources.list.d/elastic-5.x.list', 'w') as f:
    f.write('deb https://artifacts.elastic.co/packages/5.x/apt stable main\n')
  f.closed
  call(["apt", "update"])
  call(["apt", "-y", "install", "elasticsearch"])
  call(["systemctl", "daemon-reload"])
  call(["systemctl", "enable", "elasticsearch.service"])

# Install MongoDB locally
mongodb_answer = input("\nWould you like MongoDB installed locally? ").lower()
if mongodb_answer.startswith('y'):
  print(Fore.GREEN + "\n*** Installing MongoDB ***\n")
  call(["apt", "-y", "install", "mongodb-server"])

# Download graylog package
graylog_package_url = 'https://packages.graylog2.org/repo/packages/graylog-2.3-repository_latest.deb'
graylog_filename = wget.download(graylog_package_url, out="/tmp")
print(Fore.GREEN + "\n*** Downloading and Installing Graylog package ***\n")
graylog_filename

# Install graylog package
call(["dpkg", "-i", "/tmp/graylog-2.3-repository_latest.deb"])

# Update repository and install graylog
call(["apt", "update"])
call(["apt", "-y", "install", "graylog-server"])
call(["systemctl", "daemon-reload"])
call(["systemctl", "enable", "graylog-server.service"])

# Configure graylog configuration file
print(Fore.GREEN + "\n*** Configuring Graylog ***\n")

# Run shell script to configure server.conf
call(["sh", "/root/Graylog-Script/graylog_conf.sh"])

# Remove unnecessary files created during script
call(["rm", "/root/Graylog-Script/GPG-KEY-elasticsearch"])
call(["rm", "/tmp/graylog-2.3-repository_latest.deb"])

# Start Elasticsearch & Graylog Server
print(Fore.GREEN + "\n*** Starting Elasticsearch ***\n")
call(["systemctl", "start", "elasticsearch.service"])

print(Fore.GREEN + "\n*** Starting Graylog ***\n")
call(["systemctl", "start", "graylog-server.service"])

