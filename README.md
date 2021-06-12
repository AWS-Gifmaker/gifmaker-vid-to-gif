# gifmaker-vid-to-gif

### Manual deployment

docker build -t gif-maker-vid-to-gif:latest .

docker login -u AWS -p $(aws ecr get-login-password --region us-east-1) 201374217398.dkr.ecr.us-east-1.amazonaws.com
docker tag gif-maker-vid-to-gif:latest 201374217398.dkr.ecr.us-east-1.amazonaws.com/gif-maker-vid-to-gif:latest
docker push 201374217398.dkr.ecr.us-east-1.amazonaws.com/gif-maker-vid-to-gif:latest

aws lambda update-function-code --region us-east-1 --function-name vid-to-gif \
    --image-uri 201374217398.dkr.ecr.us-east-1.amazonaws.com/gif-maker-vid-to-gif:latest