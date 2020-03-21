VKFollowerCleaner
=================

ABOUT
-----

VKFollowerCleaner is scrypt on Python3

This script is tools for vk.com

This script help you make your followers list more lively and beautiful

This script uses two methods to run API methods:

 - queries in loop (VK.API has limitations for running the same API methods in often)
 - API.Execute (Allows passing up to 25 API methods in one request, but returns less error information)
 
These methods are very different, so I recommend trying them both.

QUICK START
-----------

This script uses VK.API, so to run this script you need to install the package "vk_api" from pip

      pip3 install vk_api

To run the help, just run this script

      python3 VKFollowerCleaner.py

WHAT'S NEXT
-----------

Maybe in the future I will do:

 - Clear all followers without photo
 - Clear all subscribers who do not have the message "Was online..."
