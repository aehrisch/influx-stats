
# Influx Statistics in Influx

Count the number of points in a given set of Influx databases and write the result to an Influx database.

## Environment variables


Environment Variable | Description
-------------------- | -----------
`LOG_LEVEL`   | set log level (defaults to `INFO`)
`BASE_URL`    | set URL of Influx API
`RESULT_DB`   | database to write results to
`CHECK_DB`    | database to check (count points)
`RESULT_USER` | user name to access RESULT_DB
`RESULT_PASS` | password to access RESULT_DB
`CHECK_USER`  | user name to access CHECK_DB
`CHECK_PASS`  | password to access CHECK_DB

