while read variable; do
 formatted=${variable//$'\r'/}
 export $formatted
done < .env