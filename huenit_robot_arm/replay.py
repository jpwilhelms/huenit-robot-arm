"""
Records all movements in free mod, then replays them
"""

import time
from time import sleep

from robot_control.robot import (
    pumpOn, pumpOff, pump,
    valveOn, valveOff,
    suctionOn, suctionOff,
    gripper,
    set_current_position,
    moveAngle, moveAngle_noM400,
    moveZ0_M400, moveZ0,
    freeMod, unsetFreeMod,
    getLoc, getDeg,
    suctionAngle
)

def main():
    store = []
    delay = 0.1

    while len(store) < 50:
        deg = getDeg()
        print("degree:", deg)
        store.append( deg )
        sleep( delay )

    print( store )

    unsetFreeMod()
    print( "starting replay" )
    sleep( 3 )

    while True:
        first = True
        for deg in store:
            if first:
                moveAngle( deg[0], deg[1], deg[2] )
                first = False
            else:
                moveAngle_noM400( deg[0], deg[1], deg[2] )
            sleep( delay )

if __name__ == "__main__":
    main()