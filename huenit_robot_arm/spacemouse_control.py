import pyspacemouse
from robot_control.robot import moveAngle, getDeg, unsetFreeMod, openSerial, extract_floats, getLoc
import time


class SpaceMouseControl:
    def __init__(self):
        print("Initializing robot...")
        self.serial = openSerial()
        self.serial.rts = False
        unsetFreeMod()

        # Read the current joint angles
        current_angles = getDeg()
        if len(current_angles) < 3:
            raise RuntimeError("Failed to read current position")
        self.current_angles = tuple(current_angles[0:3])

        print("Connecting to SpaceMouse...")
        if not pyspacemouse.open(callback=self.on_movement, set_nonblocking_loop=True):
            raise RuntimeError("Failed to connect to SpaceMouse")
        print("SpaceMouse connected.")

        self.speed_factor = 10.0
        self.input_threshold = 0.1
        self.target_angles = self.current_angles
        self.is_moving = False
        self.last_move_time = time.time()
        self.move_cooldown = 0.1  # Minimale Zeit zwischen Bewegungen

    def get_current_angles(self):
        """Read the current position"""
        self.send_command("M1008 A2\n")

        # Iterate over lines until the position is found or a timeout occurs
        start_time = time.time()
        while time.time() - start_time < 1.0:  # 1 second timeout
            response = self.serial.readline().decode("utf-8").strip()
            if not response:
                continue

            # Look for a line that starts with "A:"
            if response.startswith("A:"):
                angles = extract_floats(response)
                if len(angles) >= 3:
                    return angles[:3]

        print("Warning: No valid position response received")
        return None

    def send_command(self, command: str) -> str:
        """Send a command directly over the serial link"""
        self.serial.write(str.encode(command))
        return command  # for debugging

    def on_movement(self, state):
        if self.is_moving:
            return

        current_time = time.time()
        if current_time - self.last_move_time < self.move_cooldown:
            return

        # Fetch the current position
        current_pos = getLoc()
        if not current_pos or len(current_pos) < 3:
            return

        has_movement = False
        new_pos = list(current_pos)

        # Forward/backward moves the Y coordinate
        if abs(state.pitch) > self.input_threshold:
            new_pos[1] = current_pos[1] + state.pitch * self.speed_factor  # inverted sign
            has_movement = True

        # Left/right moves the X coordinate
        if abs(state.yaw) > self.input_threshold:
            new_pos[0] = current_pos[0] + state.yaw * self.speed_factor
            has_movement = True

        # Up/down moves the Z coordinate
        if abs(state.z) > self.input_threshold:
            new_pos[2] = current_pos[2] + state.z * self.speed_factor
            has_movement = True

        if not has_movement:
            return

        self.is_moving = True
        try:
            command = f"G0 X{new_pos[0]} Y{new_pos[1]} Z{new_pos[2]}\n"
            self.send_command(command)
            self.send_command("M400\n")
            self.last_move_time = current_time
        finally:
            self.is_moving = False

    def __del__(self):
        if hasattr(self, 'serial'):
            self.serial.close()
        pyspacemouse.close()


if __name__ == "__main__":
    control = SpaceMouseControl()
    print("SpaceMouse control running. Press Ctrl+C to exit.")
    try:
        while True:
            pyspacemouse.read()
    except KeyboardInterrupt:
        print("\nProgram terminated.")
