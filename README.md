## Visual Traceroute

Python program extending traceroute to display visually the locations of servers present along a packet's route.

This program doesn't re-implement the traceroute command line utility in Python, but calls it using the os module.


## PLEASE READ
Traceroute operates by sending packets over the internet to a specified host. 
Traceroute has a variety of methods (i.e type of packets sent, e.g TCP, ICMP), as some firewalls
block certain packet types, producing uninteresting output. On the command line, these methods would
be activated by using 'traceroute -T www.website.com' or 'traceroute -M TCP www.website.com', rather than the
default 'traceroute www.website.com'

Some traceroute methods don't require superuser privileges, such as the default,
but *some do*. Results vary, but personally I find that the TCP method works the best (i.e produces the least
firewalled output), and this does require sudo provileges. However, default (or even better, ICMP) works quite well too. 

Storing your sudo password in this application posed some security flaws.
Therefore, the best way to allow the use of such methods in this application is 
via editing of the sudoers file, to allow the use of traceroute without entering a password (see below).


## Enabling superuser privileges for Traceroute
To use the DCCP or TCP methods, we have to edit the sudoers file. This is a very quick and easy process.
*be careful: do only as these instructions say*

1: Open a terminal, and run 'which traceroute'. This should give you something like '/usr/sbin/traceroute'. 
If nothing appears, install traceroute using your package manager.
1: Now (on another terminal if you wish) run 'sudo visudo'.
2: Look for the line '%sudo   ALL=(ALL:ALL) ALL'
3: Below this line, (fill in the <>'s with applicable info) write:

<your username> ALL=(ALL) NOPASSWD: <output of 'which traceroute'>

Note, even though we've stopped traceroute from asking for the sudo password, 
you will still have to run it as 'sudo traceroute' on the command line if you wish
to run it outside of this application.





TODO:
- check for if user attempts to use sudo method without setting up visudo
- error handling
- write tests
- write code to account for if dont have curl etc OS level commands installed