FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        sudo \
        git \
        curl \
        wget \
        gnupg2 \
        lsb-release \
        build-essential \
        cmake \
        python3-pip \
        python3-colcon-common-extensions \
        python3-rosdep \
        python3-vcstool \
        bash-completion \
    && rm -rf /var/lib/apt/lists/*

# Gazebo (Ignition Fortress) + ros_gz bridge + GUI tooling for ROS 2 Humble
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-humble-ros-gz \
        ros-humble-ros-gz-bridge \
        ros-humble-ros-gz-sim \
        ros-humble-ros-gz-interfaces \
        ros-humble-rviz2 \
        ros-humble-rqt \
        ros-humble-rqt-common-plugins \
        ros-humble-xacro \
        ros-humble-joint-state-publisher \
        ros-humble-joint-state-publisher-gui \
        ros-humble-robot-state-publisher \
        ros-humble-teleop-twist-keyboard \
    && rm -rf /var/lib/apt/lists/*

# ---------- Workspace: user=devuser, HOME=/workspace ---------- #
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=1000

# ros:humble-ros-base (Ubuntu 22.04) has no pre-existing UID 1000 user,
# so create devuser fresh with /workspace as its home.
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m -d /workspace -s /bin/bash ${USERNAME} \
    && mkdir -p /workspace/project /workspace/install /workspace/build /workspace/log \
                /workspace/.cache /workspace/.local /workspace/.config \
    && chown -R ${USERNAME}:${USERNAME} /workspace \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# Container bashrc at /workspace/.bashrc — sources ROS + colcon install overlay.
RUN printf '%s\n' \
    '# Dev container bashrc' \
    'source /opt/ros/humble/setup.bash' \
    '[ -f /workspace/install/setup.bash ] && source /workspace/install/setup.bash' \
    'export PS1="\[\e[36m\]\u\[\e[0m\]@\[\e[35m\]\h\[\e[0m\]:\[\e[33m\]\w\[\e[0m\]\$ "' \
    > /workspace/.bashrc \
    && chown ${USERNAME}:${USERNAME} /workspace/.bashrc

ENV HOME=/workspace
USER ${USERNAME}
WORKDIR /workspace/project
