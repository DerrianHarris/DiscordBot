pip freeze > requirements.txt
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 668591540337.dkr.ecr.us-east-1.amazonaws.com
docker build -t discordbot:latest .
docker tag discordbot:latest 668591540337.dkr.ecr.us-east-1.amazonaws.com/discordbot
docker push 668591540337.dkr.ecr.us-east-1.amazonaws.com/discordbot:latest
aws s3 cp ./.env s3://lildfdiscordbot/env/
aws ecs update-service --cluster LilDFDiscordBotCluster --service lildf-service --task-definition lildf-td:4 --desired-count 1 --force-new-deployment --no-cli-pager > ./ecs_output.log