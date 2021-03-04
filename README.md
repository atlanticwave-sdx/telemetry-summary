## Name
```
Telemetry Summary Component
```

## Installation
```
Requires Python 3.7 or above
https://github.com/atlanticwave-sdx/telemetry-summary.git
cd telemetry_summary
python3 -m venv venv
source venv/bin/activate
pip install -r docs/requirements.txt
./telemetry_summary
```

## Usage
```
 ./telemetry_summary.py [-f setting_filename]
	-f setting_filename.ini or --file=setting_filename.ini
	-h or --help: prints this help

By default, the application will assume the fact to get all the setting values needed from the config.ini file.

In that file is specified all the attributes used to execute this component, such as:
- if it is a local connection
- Hostname 
- Connection port
- Database name
- Username in case of remote connection
- Password in case of remote connection
- If the connection is through SSL
- If the connection has to verify SSL

In the ini file, others attributes are specified in different sections, such as:

[TOPOLOGY]
A small definition of the topology to be used during the inspection

[MAP]
It covers all the attributes being followed up as part of the database schema.
```