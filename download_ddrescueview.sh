#! /bin/sh 

VERSION=0.4.5

wget -q -O - "https://downloads.sourceforge.net/project/ddrescueview/Test%20builds/v${VERSION}/Linux-x86_64/ddrescueview-linux-x86_64-${VERSION}.tar.xz?ts=gAAAAABmWDAUiUQ_-mlSeU6jZCMbuKd99X-rD5OSUlYRG3hkDv91Lgl6DJPhUzGXPnA5DIT8Z0C6PryXhJqhDKZIIzc3LyEtYg%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fddrescueview%2Ffiles%2FTest%2520builds%2Fv${VERSION}%2FLinux-x86_64%2Fddrescueview-linux-x86_64-${VERSION}.tar.xz%2Fdownload" | tar -Jxvf - ddrescueview-linux-x86_64-${VERSION}/ddrescueview && mv ddrescueview-linux-x86_64-${VERSION}/ddrescueview . && rmdir ddrescueview-linux-x86_64-${VERSION} && chmod +x ddrescueview
