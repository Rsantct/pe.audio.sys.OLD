#!/usr/bin/env python3

""" Simply prints the BT address of the
    1st BT loudspeaker as listed in Pulseaudio
"""

import sys
import subprocess as sp

def BTdescription(address):
    """ Gets the device.description from the PA card of given address xx:xx:...
    """
    address = address.replace(':', '_')
    BTdescription = ''

    tmp = sp.check_output( 'pactl list cards'.split() ).decode()

    found = False
    for line in tmp.split('\n'):
        if address in line:
            found = True
        if ('device.description' in line) and found:
            BTdescription = line.split('=')[-1].replace('"', '').strip()
    return BTdescription

def find_1st_BT_device():
    """ Finds the 1st BT loudspeaker as listed in Pulseaudio.
        Returns it as a card dictionary
    """
    cards = []
    tmp = sp.check_output( 'pactl list cards short'.split() ).decode()
    for line in tmp.split('\n'):
        if not line:
            break
        #print (line)
        cards.append( {'num': line.split()[0], 'name': line.split()[1]} )
    for card in cards:
        if 'bluez_card' in card['name']:
            card['string'] = card['name'].split('.')[-1].replace('_',':')
            card['description'] = BTdescription( card['string'] )
            return card
    return {'string': ''}

print( find_1st_BT_device()['string'] )


