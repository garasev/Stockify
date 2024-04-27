docker build -t tg-app .

docker run -it -e BOT_TOKEN=token  --rm --name tg-app tg-app