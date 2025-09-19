Cron job will look like this:

*/10 * * * * mosquitto-pub -t system/info -m "$(python3 /home/kelz/scripts/system_data.py)"
