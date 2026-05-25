# WSL2 + ROS 2 Humble + Gazebo (EB300 sim)

Ubuntu 22.04 in WSL2. Run commands inside WSL unless noted.

## 1. ROS 2 Humble base

```bash
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list
sudo apt update
sudo apt install -y ros-humble-desktop ros-dev-tools
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

## 2. Gazebo Fortress + ROS bridge (phase 2)

```bash
sudo apt install -y ros-humble-ros-gz
```

## 3. Build this workspace

```bash
cd /mnt/d/__projects__/RoboHand/RoboHand.Simulator/robohand_ws
source /opt/ros/humble/setup.bash
sudo rosdep init 2>/dev/null || true
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## 4. DexP gamepad in WSL (phase 3)

On **Windows** (PowerShell admin once):

```powershell
winget install dorssel.usbipd
usbipd list
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID> -a
```

In WSL:

```bash
sudo apt install -y ros-humble-joy
ros2 run joy joy_enumerate_devices
ros2 run joy joy_node
```

Package `robohand_gamepad_teleop` lives in **RoboHand.Control** (added in phase 3).

## 5. Arduino serial in WSL (phase 4, real hardware)

Same `usbipd` flow for Mega USB. Flash firmware from Windows with `arduino-cli`; control from WSL via `/dev/ttyACM0`.

## Verify

```bash
ros2 launch robohand_description display.launch.py
# RViz: add RobotModel if empty; use joint_state_publisher_gui sliders
```
