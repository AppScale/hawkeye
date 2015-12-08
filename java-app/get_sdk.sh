JAVA_SDK_VERSION=1.8.3
JAVA_SDK_ZIP=appengine-java-sdk-${JAVA_SDK_VERSION}.zip

cd ../../
if [ -e ${HOME}/${JAVA_SDK_ZIP} ]; then
        cp ${HOME}/${JAVA_SDK_ZIP} .
else
        wget http://googleappengine.googlecode.com/files/${JAVA_SDK_ZIP}
fi

unzip ${JAVA_SDK_ZIP}
rm ${JAVA_SDK_ZIP}

cd -
