SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/.env"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -d $DB_NAME -c "\i $SCRIPT_DIR/schema.sql"


PGPASSWORD=gIRRAFEShAVEsMALLnECKS41010 psql -h c16-media-polarisation-rds.c57vkec7dkkx.eu-west-2.rds.amazonaws.com -p 5432 -U c16MediaSentimentpuorG -d media_polarisation -c "\i $SCRIPT_DIR/schema.sql"