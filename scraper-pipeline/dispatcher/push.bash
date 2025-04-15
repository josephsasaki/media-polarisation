docker build --platform linux/amd64 --provenance=false -t c16-media-polarisation-dispatcher-scraper-ecr .
docker tag c16-media-polarisation-dispatcher-scraper-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-media-polarisation-dispatcher-scraper-ecr:latest
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-media-polarisation-dispatcher-scraper-ecr:latest