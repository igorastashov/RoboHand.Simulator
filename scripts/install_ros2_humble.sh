#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

if [ "$(id -u)" -eq 0 ]; then
  APT="apt-get"
else
  APT="sudo apt-get"
fi

if [ ! -f /usr/share/keyrings/ros-archive-keyring.gpg ]; then
  $APT update
  $APT install -y curl gnupg lsb-release
  curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo "$UBUNTU_CODENAME") main" \
    > /etc/apt/sources.list.d/ros2.list
fi

$APT update
$APT install -y ros-humble-desktop ros-dev-tools python3-colcon-common-extensions

USER_HOME="${SUDO_USER:+$(eval echo ~$SUDO_USER)}"
USER_HOME="${USER_HOME:-$HOME}"
BASHRC="$USER_HOME/.bashrc"
if [ -f "$BASHRC" ] && ! grep -q 'source /opt/ros/humble/setup.bash' "$BASHRC"; then
  echo 'source /opt/ros/humble/setup.bash' >> "$BASHRC"
fi

set +u
source /opt/ros/humble/setup.bash
set -u
echo "ROS2 install OK"
ros2 pkg list 2>/dev/null | wc -l
