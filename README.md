# An AI chatbot made for ze assignment lmeo
# NOTE: the ai-server is non functional in other systems other than with AMD RADEON 6600m GPU. If you still want to run it, the compose file with .bak is the one you want

## How to run the system
### pre-requisites
- Docker installed
- Docker compose plugin installed
- a brain (optional)

#### FOR NORMAL PEOPLE
Run the following a shell
```bash
docker compose up -d
```

#### FOR DEVS
Run 
```bash
docker compose up --watch --remove-orphans
```
NOTE: when updating the repo without the watch daemon running you need to rebuild with ```docker compose build``` and then re run.


# GLHF ᓀ‸ᓂ
