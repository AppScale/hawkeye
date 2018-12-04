#!/bin/bash

JAVA_SDK_VERSION=1.8.4
JAVA_SDK_ZIP=appengine-java-sdk-${JAVA_SDK_VERSION}.zip
SDK_URL="http://s3.amazonaws.com/appscale-build/${JAVA_SDK_ZIP}"

cd ../../
if [ -e ${HOME}/${JAVA_SDK_ZIP} ]; then
        cp ${HOME}/${JAVA_SDK_ZIP} .
else
        if ! wget ${SDK_URL}; then
                echo "Failed to retrieve SDK from ${SDK_URL}, exiting script"
                cd -
                exit 1
        fi
fi

echo "Extracting ${JAVA_SDK_ZIP} to ${PWD}"

if ! unzip -q ${JAVA_SDK_ZIP}; then
        echo "Failed to unzip SDK correctly, please see errors above"
        rm -f ${JAVA_SDK_ZIP}
        cd -
        exit 1
fi

rm -f ${JAVA_SDK_ZIP}
cd -
