cd ../../
if [ -e ${HOME}/appengine-java-sdk-1.8.1.zip ]; then
        cp ${HOME}/appengine-java-sdk-1.8.1.zip .
else
        wget http://googleappengine.googlecode.com/files/appengine-java-sdk-1.8.1.zip
fi
unzip appengine-java-sdk-1.8.1.zip
rm appengine-java-sdk-1.8.1.zip
cd -
