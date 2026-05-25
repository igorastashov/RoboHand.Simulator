# RoboHand.Simulator

ROS 2 workspace for EB300 simulation: kinematic model, Gazebo physics, bringup.

## Workspace layout

```
robohand_ws/src/
  robohand_description/   # URDF/xacro (all link sizes in config)
  robohand_gazebo/          # worlds, gz_ros2_control (phase 2)
  robohand_bringup/         # sim + rviz launch files (phase 2)
```

## Prerequisites (WSL2 Ubuntu 22.04)

See [docs/wsl-ros2-setup.md](docs/wsl-ros2-setup.md).

## Quick start (after ROS 2 Humble is installed)

```bash
cd /mnt/d/__projects__/RoboHand/RoboHand.Simulator/robohand_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
ros2 launch robohand_description display.launch.py
```

## Tuning geometry

Edit `robohand_description/config/kine_eb300_approx.yaml` — all link lengths, joint limits, and inertial guesses are there. No mesh required; links are primitive boxes/cylinders.

## Phases

1. **Now:** RViz display + configurable skeleton
2. **Next:** Gazebo world + ros2_control + pick/place cube
3. **Later:** Replace approx dims with measured EB300 values from assembly/STL
