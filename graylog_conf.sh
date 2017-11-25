#!/bin/sh

# Copy current graylog conf file to temp file
file_path='/etc/graylog/server/server.conf'

# Generate Secret Password
secret_password=$(pwgen -N 1 -s 96)

# Create Username
read -p 'Username for graylog WebGUI login? : ' username

# Create Username password
read -p "What will be the ${username} user password? : " password

# Configure necessary parts of graylog configuration file
sed -i "/^password_secret/c\password_secret = ${secret_password}" ${file_path}
sed -i "/^#root_username/c\root_username = ${username}" ${file_path}

# Convert password provided into hash password
password=$(echo -n ${password} | shasum -a 256 | awk -F' ' '{print $1}')
sed -i "/^root_password_sha2/c\root_password_sha2 = ${password}" ${file_path}

# Set Elasticsearch IP
get_elasticsearch_ip()
{
elasticsearch=$(dpkg -l | grep elasticsearch | wc -l)
if [ ${elasticsearch} -eq 0 ]; then
	read -p 'What will be the Elasticsearch host IP? : ' elasticsearch_ip
	if [ -z ${elasticsearch_ip} ]; then
		echo "\n***Nothing was entered***\n"
		get_elasticsearch_ip
	fi
else
	elasticsearch_ip=127.0.0.1
	ES_conf='/etc/elasticsearch/elasticsearch.yml'
	sed -i "/^#cluster.name/c\cluster.name: graylog" ${ES_conf}
	sed -i "/^#network.host/c\network.host: ${elasticsearch_ip}" ${ES_conf}
fi
}

get_elasticsearch_ip
sed -i "/^#elasticsearch_hosts/c\elasticsearch_hosts = http://${elasticsearch_ip}:9200" ${file_path}

# Set MongoDB IP
get_mongodb_ip()
{
mongodb=$(dpkg -l | grep mongodb-server | wc -l)
if [ ${mongodb} -eq 0 ]; then
	read -p 'What will be the MongoDB host IP? : ' mongodb_ip
	if [ -z ${mongodb_ip} ]; then
		echo "\n***Nothing was entered***\n"
		get_mongodb_ip
	fi
else
	mongodb_ip=localhost
fi
}

get_mongodb_ip
sed -i "/^mongodb_uri/c\mongodb_uri = mongodb://${mongodb_ip}/graylog" ${file_path}

# Set Graylog IP to local ip
get_graylog_ip()
{
read -p 'What is the interface name to be used for graylog? : ' int_name
if [ -z ${int_name} ]; then
	echo "\n***Nothing was entered***\n"
	get_graylog_ip
fi
}

get_graylog_ip
graylog_ip=$(/sbin/ifconfig ${int_name} | grep "inet " | awk -F' ' '{print $2}' | awk '{print $1}')
sed -i "/^rest_listen_uri/c\rest_listen_uri = http://${graylog_ip}:9000/api/" ${file_path}
sed -i "/^#web_listen_uri/c\web_listen_uri = http://${graylog_ip}:9000/" ${file_path}

