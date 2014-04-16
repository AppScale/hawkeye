cd ../../
if [ -e ${HOME}/appengine-java-sdk-1.8.0.zip ]; then
        cp ${HOME}/appengine-java-sdk-1.8.0.zip .
else
        wget http://googleappengine.googlecode.com/files/appengine-java-sdk-1.8.0.zip
fi
unzip appengine-java-sdk-1.8.0.zip
rm appengine-java-sdk-1.8.0.zip
cd -
