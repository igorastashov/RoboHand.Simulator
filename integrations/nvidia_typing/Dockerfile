# Runtime overlay: existing pinned NVIDIA runtime and existing upstream entrypoint.
ARG BASE_IMAGE=robohand/so101-tutorial:7aec2ed-20261115
FROM ${BASE_IMAGE}
ARG SOURCE_SHA256
ARG ADAPTATION_SHA256
LABEL org.so101.source-sha256=${SOURCE_SHA256}
LABEL org.robohand.base-commit=7aec2ed26dce8c88ae007a2714680cce572e1466
LABEL org.robohand.adaptation-sha256=${ADAPTATION_SHA256}
COPY source/so101_typing /workspace/isaaclab/source/so101_typing
COPY scripts /workspace/isaaclab/scripts
COPY configs /workspace/isaaclab/configs
