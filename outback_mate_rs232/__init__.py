# https://www.wmrc.edu/projects/BARenergy/manuals/outback-manuals/Mate_Serial_Comm_R302.pdf

import time
import serial
import sys
import pprint
import logging
pp = pprint.PrettyPrinter(indent=4)

logger = logging.getLogger(__name__)

class Mate:
    def __init__(self, port, system_voltage):
        self.port = port
        self._ssv = [12, 24, 48]    # supported system voltages
        self.system_voltage = system_voltage if system_voltage in self._ssv else None
        if self.system_voltage is None:
            err = "System voltage of %s not in %s "%(system_voltage, self._ssv)
            raise ValueError(err)
            
        self.data_raw = {}          # Data as strings from the unit
        self.data_interp = {}       # Data parsed into sensible values as needed
    
    def run(self):
        with serial.Serial(port=self.port, baudrate=19200, timeout=1) as ser:
            #  DTR (pin 4) be driven high (set) and that RTS (pin 7) be driven low (cleared)
            ser.setDTR(True)
            ser.setRTS(False)

            try:
                while True:
                    d = ser.read_until(terminator=b"\r")
                    self.parse(d)
            except KeyboardInterrupt:
                logger.info("interrupted by keyboard")
            except:
                logger.error(sys.exc_info())

    def parse(self, d):
        dd = self.qualify(d)
        if dd:
            dd = dd[1:-1]
            dv = dd.split(",")
            dk = ["address",
                  "inverter_current",
                  "charge_current",
                  "buy_current",
                  "ac_in_volt",
                  "ac_out_volt",
                  "sell_current",
                  "fx_op_mode",
                  "fx_error_mode",
                  "fx_ac_mode",
                  "fx_batt_volt",
                  "fx_misc",
                  "fx_warning_mode",
                  "chksum"]
            ddict = dict(zip(dk, dv))
            self.data_raw[ddict["address"]] = ddict
            
            if self.verify_checksum(dd):
                self.interp_store_data(ddict["address"])
            else:
                logger.error("Error cannot verify checksum of %s"%(dd))


    def interp_store_data(self, k):
        dk = self.data_raw[k]
        dk["fx_op_mode"] = self.fx_op_mode_to_str(dk["fx_op_mode"], k)
        dk["fx_error_mode"] = self.fx_error_to_str(dk["fx_error_mode"], k)
        dk["fx_ac_mode"] = self.fx_ac_mode_to_str(dk["fx_ac_mode"], k)
        dk["fx_misc"] = self.fx_misc_to_str(dk["fx_misc"], k)
        dk["fx_warning_mode"] = self.fx_warn_mode_to_str(dk["fx_warning_mode"], k)

        self.data_interp[dk["address"]] = dk
        self.callback_on_data(k)

    def fx_op_mode_to_str(self, mode, k):
        "mode is the '5' or '3' for example"
        mode = int(mode)

        modes = {
            0: "Inv Off",
            1: "Search",
            2: "Inv On",
            3: "Charge",
            4: "Silent",
            5: "Float",
            6: "EQ",
            7: "Charger Off",
            8: "Support",
            9: "Sell Enabled",
            10: "Pass Through",
            90: "FX Error",
            91: "AGS Error"
        }

        return modes.get(mode, "Unknown Mode '" + str(mode) + "'")

    def fx_error_to_str(self, err, k):
        "err is the value 0 to 256 for example"
        err = int(err)
        if err != 0 :
            self.callback_on_error(k)

        errors = {
            "Low VAC Input": bool(err>>0 & 1),
            "Stacking Error": bool(err>>1 & 1),
            "Over Temp": bool(err>>2 & 1),
            "Low Battery": bool(err>>3 & 1),
            "Phase Loss": bool(err>>4 & 1),
            "High Battery": bool(err>>5 & 1),
            "Shorted Output": bool(err>>6 & 1),
            "Backfeed": bool(err>>7 & 1)
        }

        return errors

    def fx_ac_mode_to_str(self, mode, k):
        "mode is the '5' or '3' for example"
        mode = int(mode)

        modes = {
            0: "No AC",
            1: "AC Drop",
            2: "AC Use",
        }

        return modes.get(mode, "Unknown Mode '" + str(mode) + "'")

    def fx_misc_to_str(self, misc, k):
        "misc is integer 0-256"
        misc = int(misc)

        misc_dict = {
            "230V Unit": bool(misc>>0 & 1),
            "Aux Output On": bool(misc>>7 & 1)
        }

        return misc_dict

    def fx_warn_mode_to_str(self, mode, k):
        "mode is the '005' or '003' for example"
        mode = int(mode)

        if mode != 0:
            self.callback_on_warning(k)

        mode_dict = {
            "AC Input Freq High": bool(mode>>0 & 1),
            "AC Input Freq Low": bool(mode>>1 & 1),
            "Input VAC High": bool(mode>>2 & 1),
            "Input VAC Low": bool(mode>>3 & 1),
            "Buy Amps > Input Size": bool(mode>>4 & 1),
            "Temp Sensor Failed": bool(mode>>5 & 1),
            "Comm Error": bool(mode>>6 & 1),
            "Fan Failure": bool(mode>>7 & 1)
        }

        return mode_dict

    def verify_checksum(self, datastr):
        return True

    def qualify(self, d):
        try:
            dd = d.decode("UTF-8")
        except UnicodeDecodeError:
            logger.warn("Can't decode %s"%(d))
            return

        try:
            if len(dd) > 2:
                s = dd[0]
                e = dd[-1]
            else:
                logger.warn("Low Length Error '%s'"%(dd))
                return
        except ValueError:
            logger.warn("Value parse error %s"%(d))
            return
        if s == "\n" and e == "\r":
            return dd
        else:
            logger.warn("start/end error on %s"%(d))
            return
        
    def callback_on_data(self, address):
        # Override this for callback when new data arrives
        # This only runs if the data was parsed
        logger.debug("Callback for data on address '%s'"%(address))

    def callback_on_warning(self, address):
        # Override this for callback when data keys have warning flags
        # This only runs if the data was parsed
        logger.warn("Callback for warning(s) on address '%s'"%(address))

    def callback_on_error(self, address):
        # Override this for callback when data keys have warning flags
        # This only runs if the data was parsed
        logger.error("Callback for error(s) on address '%s'"%(address))

if __name__ == "__main__":
    m = Mate(port="/dev/ttyUSB1",system_voltage=12)
    m.run()


    


