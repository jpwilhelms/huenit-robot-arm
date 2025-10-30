"""
moves a staple of objects to a new location
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
    getLoc, getDeg, moveG1,
    suctionAngle
)

def main():
    input( "position on empty staple location" )
    staple_bottom = getLoc()
    input( "position on staple" )
    staple_top = getLoc()
    input( "position on target" )
    staple_target = getLoc()
    number_of_objects = int( input( "number of objects: " ) )
    print( f"cards: {number_of_objects}" )
    thickness = (staple_top[2] - staple_bottom[2]) / number_of_objects
    print( f"thickness of single card: {thickness}" )
    unsetFreeMod()
    move_height = staple_top[2] + 20
    pressure_reduce = 2
    rotate = 0

    moveZ0( move_height )
    above_staple = staple_top.copy()
    above_staple[2] = move_height
    above_target_staple = staple_target.copy()
    above_target_staple[2] = move_height

    for i in range( number_of_objects ):
        moveG1( above_staple )

        if rotate != 0:
            suctionAngle( 0 )

        source_pos = staple_top.copy()
        source_pos[ 2 ] -= (i * thickness) - pressure_reduce
        moveG1( source_pos )
        suctionOn()
        sleep( 0.3 )
        moveG1( above_staple )
        sleep( 2 )
        moveG1( above_target_staple )

        if rotate != 0:
            suctionAngle( rotate )

        dest_pos = staple_target.copy()
        dest_pos[ 2 ] += (i+1) * thickness
        moveG1( dest_pos )
        suctionOff()
        sleep( 0.3 )
        moveG1( above_target_staple )

if __name__ == "__main__":
    main()