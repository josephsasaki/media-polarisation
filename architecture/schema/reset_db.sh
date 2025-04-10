SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/../.env"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -d $DB_NAME -c "\i $SCRIPT_DIR/schema.sql"