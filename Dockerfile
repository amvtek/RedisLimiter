# this Dockerfile provides development terminal for the RedisLimiter project.
FROM python:3.12-slim-bookworm

# Force to use https for apt-get
RUN echo "deb https://deb.debian.org/debian/ stable main" > /etc/apt/sources.list

RUN <<EOF
rm -f /etc/apt/apt.conf.d/docker-clean
echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
EOF

# Add development utilities
COPY --from=johnnymorganz/stylua:2.0.2 /stylua /usr/local/bin/stylua
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/var/lib/apt,sharing=locked <<EOF
apt-get update
apt-get --no-install-recommends install -y build-essential redis-tools vim
EOF



ARG USERNAME
ARG USER_ID

RUN <<EOF
# remove user USERNAME if it exists
if id -u $USERNAME > /dev/null 2>&1; then
	echo "Deleting user with name $USERNAME"
	userdel -r $USERNAME > /dev/null 2>&1
fi 
		
# remove user USER_ID if it exists
if id -u $USER_ID > /dev/null 2>&1; then
	echo "Deleting user with identifier $USER_ID"
	userdel -r $(id -nu $USER_ID) > /dev/null 2>&1
fi

echo "---"
echo "Creating user $USERNAME"

useradd -m -u $USER_ID -s /usr/bin/bash $USERNAME

echo 'alias rediscli="redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB"' >> /home/${USERNAME}/.bash_aliases
echo 'echo "Use rediscli command, to connect to dockerized redis"' >> /home/${USERNAME}/.bash_aliases
chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.bash_aliases
EOF

USER $USER_ID
WORKDIR /home/${USERNAME}

COPY ./requirements.txt ./

RUN --mount=type=cache,target=/home/${USERNAME}/.cache/pip,sharing=locked <<EOF
python3 -m venv --upgrade-deps --prompt=RDL VENV
VENV/bin/pip install -r requirements.txt
rm requirements.txt
EOF

ENV PATH="/home/${USERNAME}/VENV/bin:${PATH}"

WORKDIR repos

CMD ["bash"]
