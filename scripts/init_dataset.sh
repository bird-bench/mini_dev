#!/usr/bin/env bash
set -eu

# --- Data and Path Config ---
# dataset download url
PRIMARY_URL="https://bird-bench.oss-cn-beijing.aliyuncs.com/minidev.zip"
SECONDARY_URL="https://drive.google.com/file/d/1UJyA6I6pTmmhYpwdn8iT9QKrcJqSQAcX/view?usp=sharing"

# dataset file name
MINIDEV_ZIP="llm/mini_dev_data/minidev.zip"

# where to save the unzip dateset files
DATA_DIR="data"

if [ ! -f "${MINIDEV_ZIP}" ]; then
    echo "${MINIDEV_ZIP} not exist."
    echo "Download dataset..."

    if curl -# -L -o "${MINIDEV_ZIP}" --connect-timeout 5 "${PRIMARY_URL}"; then
        echo "Download finished."
        echo
    else
        echo "Can't connect to Aliyun, change to Google Drive."
        if curl -# -L -o "${MINIDEV_ZIP}" --connect-timeout 5 "${SECONDARY_URL}"; then
            echo "Download finished."
            echo
        else
            echo "Fail to download Mini_dev dataset, check your network"
            exit 1
        fi
    fi
fi

echo "Unzip dataset..."
echo
mkdir -p "${DATA_DIR}"
unzip "${MINIDEV_ZIP}" -d "${DATA_DIR}"

echo "Everything is ready~"
