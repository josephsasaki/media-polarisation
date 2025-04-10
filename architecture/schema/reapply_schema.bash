source .env

PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USERNAME} ${DB_NAME} -f schema.sql

echo "Schema successfully reapplied."
