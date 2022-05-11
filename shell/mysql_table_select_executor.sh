#/bin/bash
echo "Welcome to MySQL multiple table select & executor!"

echo -n "Your username? : "
read INPUT
MYSQL_USER_NAME=$INPUT

echo -n "Your database? : "
read INPUT
MYSQL_DATABASE=$INPUT

echo -n "Your command? (ex. DROP TABLE) : "
read INPUT
MYSQL_COMMAND=$INPUT

echo -n "Your table name pattern? (ex. xe%) : "
read INPUT
MYSQL_TABLE_PATTERN=$INPUT

SELECT_QUERY="SELECT CONCAT('"$MYSQL_COMMAND" ', t.TABLE_NAME, ';') FROM information_schema.tables as t WHERE t.TABLE_SCHEMA = '"$MYSQL_DATABASE"' AND t.TABLE_NAME LIKE '"$MYSQL_TABLE_PATTERN"';"
#echo $SELECT_QUERY

SELECT_RESULT=$(mysql -u $MYSQL_USER_NAME -p -N -B -e "$SELECT_QUERY")

QUERY_RESULT_LOG="query_result.log"
echo "$SELECT_RESULT" > $QUERY_RESULT_LOG
echo "Execute following command(s) in MySQL?(y/n)"
echo "$SELECT_RESULT"
echo -n "Execute followed command(s) in MySQL?(y/n) : "

read INPUT
case $INPUT in
	y)
		mysql -u root -p < $QUERY_RESULT_LOG
		echo "Command executed!"
		;;
	*)
		echo "Command canceled!"
		;;
	esac

exit 0


