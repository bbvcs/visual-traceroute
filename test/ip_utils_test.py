import pytest
import socket
from ip_utils import format_hostname

def test_format_hostname_on_valid_input(): # not valid hostnames, but valid inputs to function (can be formatted)
    # google used as likely servers will be up, and able to take a lot of traffic

    assert format_hostname("www.google.com") == "www.google.com"
    assert format_hostname("https://www.google.com") == "www.google.com"
    assert format_hostname("www.google.com/page1/page2") == "www.google.com"
    assert format_hostname("https://www.google.com/page1/page2") == "www.google.com"

    google_details = socket.gethostbyaddr("www.google.com")
    """ google_details will look something like: 
        ('lhr48s09-in-f4.1e100.net', [], ['172.217.169.68']) 
        here we have a google server hostname and IP """
    assert format_hostname(google_details[2][0]) == google_details[0]

    # add more here ! like actual google/x/y/z sites


#def test_format_hostname_on_invalid_input():


