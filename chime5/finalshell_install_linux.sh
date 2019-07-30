#! /bin/bash

source /etc/profile

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar 

install_path=""
package_download_url=http://dl.hostbuf.com/finalshell2/finalshell_linux.zip?v=$RANDOM
package_save_name=finalshell_data_linux.zip

function checkOS_TYPE(){
    if [[ ! -z "`uname | grep Darwin`" ]];then
        OS_TYPE=osx
		install_path=/Applications
    elif [[ ! -z "`uname | grep Linux`" ]];then
        OS_TYPE=linux
		install_path=/usr/lib
    else
        echo "Unsupported operating systems!"
        exit 1
    fi
}

function checkos(){
    if [[ -f /etc/redhat-release ]];then
        OS=centos
    elif [[ ! -z "`cat /etc/issue | grep bian`" ]];then
        OS=debian
    elif [[ ! -z "`cat /etc/issue | grep Ubuntu`" ]];then
        OS=ubuntu
    else
        echo "unknow"
    fi
	echo $OS
}

function install(){
   echo  "  正在安装FinalShell..."
   if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
   fi
   rm -f $package_save_name
   if [[ $OS_TYPE = "osx" ]]; then
   n=0
   until [ $n -ge 10 ]
   do
      echo "Downloading finalshell_data.zip..."
      curl -L -o $package_save_name $package_download_url && break
      n=$[$n+1]
      sleep 2
   done
    elif [[ $OS_TYPE = "linux" ]]; then
		if ! wget -O $package_save_name $package_download_url ; then
			echo "Download software failed!"
			exit 1
		else
			echo "Download complete!"
		fi
    else
        echo "Unsupported operating systems!"
        exit 1
    fi
	
	unzip -o $package_save_name  -d $install_path
	
	cd $install_path/FinalShell/app/
	
	#sudo chmod 775 ./unpack200;
	#./unpack200 finalshell.pack.gz finalshell.jar
	#rm -f finalshell.pack.gz
	#./unpack200 lib-run/bcprov-jdk15on-160.pack.gz lib-run/bcprov-jdk15on-160.jar
	#rm -f lib-run/bcprov-jdk15on-160.pack.gz
	
	\cp img/finalshell.png /usr/share/icons/hicolor/scalable/apps
	\cp finalshell.desktop /usr/share/applications
	chmod +x /usr/share/applications/finalshell.desktop
		
	sudo find /usr/lib/FinalShell -type f -exec chmod 644 {} \;
	sudo find //usr/lib/FinalShell -type d -exec chmod 755 {} \;
	sudo chmod 755 /usr/lib/FinalShell/FinalShell;
	#sudo chmod 755 /usr/lib/FinalShell/app/unpack200;
	#sudoer=$(who am i | awk '{print $1}');
	sudoer=$USER
	sudo chown -R $sudoer /usr/lib/FinalShell
	sudo chown -R $USER:$USER /home/$USER/fsdownload/
	sudo setcap cap_net_raw,cap_net_admin=eip /usr/lib/FinalShell/FinalShell
	#/usr/lib/FinalShell/FinalShell
	echo  "  FinalShell安装完成"
	
	
}

checkOS_TYPE
checkos
install
