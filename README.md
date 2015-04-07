Wemo Power Meter Reader

Simple Python script to log the power reading of Belkin Insight Switches.

Run `python wemo_insight.py HOST` to start polling the power reading from the Wemo Insight.


The script does automatic error recovery and tries to repeat calls on different ports or tries to rebind the IP address if necessary. Debug and error messages are written to stderr. The first connection may need a number of tries to find the device.

It logs the IP and the current power reading in milliwatts as reported by the Wemo device to stdout.

The script disables auto-off and repeatedly sends a command to turn the meter on.

Typically one would run this as `nohup python wemo_insight.py HOST > log 2> errorlog &` to log both measurements and errors into files.
