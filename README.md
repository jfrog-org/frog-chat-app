# JFrog Advanced Security Demo 

**Setup Demo**
```
$ git clone ssh://git@git.jfrog.info/sr/sectools.git
$ cd sectools/demo_jas
$ docker build . -t demo_jas
$ docker run -d -p 1337:80 --env-file ./.env.prod demo_jas
$ docker exec <container_id> python manage.py create_db
$ docker exec <container_id> python manage.py seed_db

# To view docker container id:
$ docker ps
```

**Python Version:** `3.11.8`