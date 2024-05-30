#! /bin/sh 

VERSION=0.3

wget -q -O /tmp/output.zip "https://downloads.sourceforge.net/project/ddrescueview/Releases/v${VERSION}/Linux-x86_64/ddrescueview-linux-x86_64-${VERSION}.zip?ts=gAAAAABmWB7P3ZwM7CDDU1ijm9D5i3eEVYX7O6jGr5EMCnCgUXgcUXa7oeBUosI56R0oKxncsFKei8fS-I2NHpvcQKpWu6XhvQ%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fddrescueview%2Ffiles%2FReleases%2Fv${VERSION}%2FLinux-x86_64%2Fddrescueview-linux-x86_64-${VERSION}.zip%2Fdownload" && unzip /tmp/output.zip ddrescueview && rm /tmp/output.zip && chmod +x ddrescueview
