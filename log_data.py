from devices.ocpn3 import OPCN3

import time




def main():


    item = OPCN3(settings_file="./settings.yaml")
    item.wake()

    starttime = time.time()

    print(item.read_last(item.gadget_id))

    done = False
    # print("Logging started.  Press Ctrl-C to stop.")
    while not done:

        try:

            reading = item.get_particulates()
            item.write_reading(item.gadget_id, **reading)

            # print(f"logging {item.gadget_id} t:{reading['temp']}, rh: {reading['rh']}, pms: {reading['pm01']}, {reading['pm25']}, {reading['pm10']}")


        except KeyboardInterrupt:
            done = True
            item.sleep()

        except Exception as e:
            print(f"Error {e}")

        time.sleep(10)

if __name__ == '__main__':
    main()

