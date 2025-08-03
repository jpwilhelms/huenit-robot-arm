from robot_control import robot

def main():
    robot.moveG0(0, 200, 0)
    robot.moveG0(0, 300, 0)


if __name__ == "__main__":
    main()