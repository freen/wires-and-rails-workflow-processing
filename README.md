# Wires and Rails: Workflow Post-Processing Tasks

The app currently runs on a `t2.medium` EC2 instance.

## Pre-commit hook

Enforces `pylint` success on commit.

```
ln -sf ../../bin/pre-commit .git/hooks/pre-commit
```

## Local development

Start the docker swarm locally:

```
$ docker swarm init
$ docker stack deploy -c docker-compose.yml WARWP
```

`docker ps` should look like this:

```
➜  wires-and-rails-workflow-processing git:(master) ✗ docker ps
CONTAINER ID        IMAGE                                              COMMAND                  CREATED             STATUS              PORTS               NAMES
a0813aa4d93c        redis:latest                                       "docker-entrypoint.s…"   2 minutes ago       Up 2 minutes        6379/tcp            WARWP_redis.1.scoef9b4fwcym4nbmag43lyho
9404635b7177        freen/wires-and-rails-workflow-processing:latest   "/usr/bin/supervisor…"   2 minutes ago       Up 2 minutes                            WARWP_cron-and-queue.1.uwb2ruo7aoo74pucqgar7cxbn
```

Log into the `cron-and-queue` container for testing / debugging:

```
➜  wires-and-rails-workflow-processing git:(master) ✗ docker exec -it 9404635b7177 /bin/bash
root@9404635b7177:/app# 
```

NOTE: `ocropy` isn't very OSX friendly. For development purposes, testing ocropy commands should take place in the Docker container.
