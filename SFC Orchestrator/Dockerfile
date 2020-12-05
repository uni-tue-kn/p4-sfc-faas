#FROM p4lang/pi:stable
FROM cslev/p4controller


# Install dependencies
RUN apt-get update && \
	apt-get install -y apt-utils python-pip ssh

RUN	DEBIAN_FRONTEND=noninteractive apt-get install -y python-libvirt 

RUN pip install --no-cache-dir pylxd simplejson tabulate urllib3 getmac Inotify paramiko pylxd python-dotenv cryptography==2.5

WORKDIR /opt/msc-steinert

COPY . .

COPY ./certs/orchestrator.key /root/.ssh/id_rsa

CMD ["sh", "./start.sh"]
