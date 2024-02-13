# bscpy setup

1. Get the IP address of your TV. I could only get it through the router, I didn't find it anywhere in the menu.
2. Optional: set the TV's IP to a fixed address in your router's DHCP settings. This will make your life much easier in the future, as the address won't change every week.
3. Install [bscpylgtv](https://github.com/chros73/bscpylgtv)
4. On macOS / linux, I recommend making a bash function like this into your .bash_profile.

   ```
   bscpy() {
    bscpylgtvcommand 192.168.1.12 "$@"
   }
   ```

   On Windows, you can make a bscpy.bat file with the following content:

   ```
   @echo off
   bscpylgtvcommand 192.168.1.12 %*
   ```


4. Test the INFO button:
   ```
   bscpy button INFO
   ```

5. Make sure it appears, click Yes.

6. bscpy setup is done.
