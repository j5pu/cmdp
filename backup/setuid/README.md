# setuid

https://www.redhat.com/sysadmin/suid-sgid-sticky-bit

```bash
echo $EUID # effective
id -u # effective
python3 -c "import os; print('os.geteuid()')"
echo $UID  # real   #
id -u -r  # real 
python3 -c "import os; print('os.getuid()')"

```

```python
import os
os.getlogin()
os.getuid()
os.geteuid()

os.seteuid(0)  # Set the current process's effective user id
os.setuid(0)  # Set the current process's user id
os.setreuid(0, 0)  # Set the current process's real and effective user ids

```

```
sudo su
ipython

os.getuid()
0
os.geteuid()
0

os.seteuid(501)
touch /tmp/0
ls -la /tmp/0
-rw-r--r--  1 root  wheel  0 Jul 31 18:17 /tmp/0

os.setuid(501)
touch /tmp/501
ls -la /tmp/501
-rw-r--r--  1 j5pu  wheel  0 Jul 31 18:23 /tmp/501
```

```python

import os

file = ""

# noinspection SpawnShellInjection,PyUnresolvedReferences
os.execl(file, *args)  # Execute the executable file with argument list args, replacing the current process.

# noinspection SpawnShellInjection,PyUnresolvedReferences
os.execlp(file, *args)  # Execute the executable file (which is searched for 
                        # along $PATH) with argument list args, replacing the current process

```
## user + s (pecial)
Commonly noted as SUID, the special permission for the user access level has a single function: A file with SUID always 
executes as the user who owns the file, regardless of the user passing the command. 
If the file owner doesn't have execute permissions, then use an uppercase S here.

Now, to see this in a practical light, let's look at the /usr/bin/passwd command. 
This command, by default, has the SUID permission set:
```
[tcarrigan@server ~]$ ls -l /usr/bin/passwd 
-rwsr-xr-x. 1 root root 33544 Dec 13  2019 /usr/bin/passwd
Note the s where x would usually indicate execute permissions for the user.
```
**This "s" tells us the setuid bit is set**

When we run the passwd command **it is automatically executed as the owner of the file**


## other + t (sticky)

The last special permission has been dubbed the "sticky bit." This permission does not affect individual files. However,
at the directory level, it restricts file deletion. 
Only the owner (and root) of a file can remove the file within that directory. 
A common example of this is the /tmp directory:

```
[tcarrigan@server article_submissions]$ ls -ld /tmp/
drwxrwxrwt. 15 root root 4096 Sep 22 15:28 /tmp/
The permission set is noted by the lowercase t, where the x would normally indicate the execute privilege.
```

## Setting special permissions
To set special permissions on a file or directory, 
you can utilize either of the two methods outlined for standard permissions above: Symbolic or numerical.

Let's assume that we want to set SGID on the directory community_content.

To do this using the symbolic method, we do the following:

[tcarrigan@server article_submissions]$ chmod g+s community_content/
Using the numerical method, we need to pass a fourth, preceding digit in our chmod command. 
The digit used is calculated similarly to the standard permission digits:

* Start at 0
* SUID = 4
* SGID = 2
* Sticky = 1
* 
The syntax is:

```
[tcarrigan@server ~]$ chmod X### file | directory
```

Where X is the special permissions' digit.

Here is the command to set SGID on community_content using the numerical method:

```
[tcarrigan@server article_submissions]$ chmod 2770 community_content/
[tcarrigan@server article_submissions]$ ls -ld community_content/
drwxrws---. 2 tcarrigan tcarrigan 113 Apr  7 11:32 community_content/
```



```
ln -s /usr/local/bin/python3 /usr/local/bin/spython  ## Does not work os.seteuid with symlink
sudo chown -R root /usr/local/bin/spython
sudo chmod -R u+s,g+s /usr/local/bin/spython

sudo cp /usr/local/bin/python3 /usr/local/bin/spython
sudo chmod -R u+s,g+s /usr/local/bin/spython
spython
>>> import os
>>> os.getuid()
501
>>> os.geteuid()
0
>>> import stat
>>> os.stat("/usr/local/bin/spython").st_mode & stat.S_ISUID == stat.S_ISUID
True
>>> from pathlib import Path
>>> Path("/tmp/0").touch()
>>> Path("/tmp/0").owner()
'root'
>>> 
>>> Path("/etc/0").touch()
>>> Path("/etc/0").owner()
'root'
>>> 
>>> os.seteuid(501)
>>> Path("/tmp/501").touch()
>>> Path("/tmp/501").owner()
'j5pu'
>>> >>> Path("/tmp/501").stat().st_uid
501
>>> Path("/etc/501").touch()
>>> Path("/etc/501").owner()
PermissionError: [Errno 13] Permission denied: '/etc/501'
>>> 
>>>
>>> if os.stat("/usr/local/bin/spython").st_mode & stat.S_ISUID == stat.S_ISUID: os.seteuid(os.getuid())
```

## pth

https://docs.python.org/3/library/site.html

/usr/local/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/matplotlib-3.7.1-py3.11-nspkg.pth

 /usr/local/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/distutils-precedence.pth
