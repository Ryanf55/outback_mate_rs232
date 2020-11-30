# outback_mate_rs232
Python API for Outback Power Systems Mate using RS232

This is a really simple python module to talk to a Outback Mate using python. 



It is formatted as a python package, so after cloning, go to the directory above outback_mate_rs232. 
` $ python3 -m pip install -e outback_mate_rs232/`

## Hardware required

* Outback Mate connected to Outback system
* RS232 cable
* RS232 to USB adapter

## Data Access

In the `Mate.data_raw` data member, entries are keyed with the address of the inverter or charge controller. The data is as-arrived from the RS232 interface. 
If you don't want to use the user manual to interpret bit fields and error keys, instead use `Mate.self.data_interp`. Some of the fields are dictionaries of the error bitfields showing true/false for the error states.

## Related projects

* [pymate](https://github.com/jorticus/pymate) -> Python API that can emulate a mate
  * outback_mate_rs232 does not replace the mate, but instead uses the Mate's RS232 to receive data
  * Pymate will offer more features, but requiring soldering custom hardware 
  * Pymate also has a [RS232 module](https://github.com/jorticus/pymate/blob/master/pymate/matecom.py) but its functionality is more limited than here
  
## Limitations

* This module only reads data from RS232 and does not support any of the controls (yet)
* This module does not perform checksum error checking on the data

## Further notes

* There are callbacks created for data arrival, data warnings and data errors. Rebind these as needed.



