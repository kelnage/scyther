#!/usr/bin/python

#---------------------------------------------------------------------------

""" Import externals """
import wx
import wx.lib.newevent
import os
import sys
import re
import threading
import StringIO

#---------------------------------------------------------------------------

""" Import scyther components """
import XMLReader

""" Import scyther-gui components """
import Tempfile
import Claim
import Preference
import Scyther

#---------------------------------------------------------------------------

""" Global declaration """
(UpdateAttackEvent, EVT_UPDATE_ATTACK) = wx.lib.newevent.NewEvent()
busy = threading.Semaphore()


#---------------------------------------------------------------------------

def ScytherPath():
    """ Retrieve Scyther path, and maybe test whether is is valid? """
    program = Preference.get('scyther','scyther')
    program = "\\\\Roivas\\public\\scyther-gui\\Scyther.exe"
    return program

class ScytherThread(threading.Thread):
    # Override Thread's __init__ method to accept the parameters needed:
    def __init__ ( self, win, spdl, details ):

        self.win = win
        self.spdl = spdl
        self.details = details

        self.claims = []

        threading.Thread.__init__ ( self )

    def run(self):

        global busy

        evt = UpdateAttackEvent(status="Running Scyther...")
        wx.PostEvent(self.win, evt)

        self.claimResults()

        evt = UpdateAttackEvent(status="Done.")
        wx.PostEvent(self.win, evt)

        #self.win.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        busy.release()

    def claimResults(self):
        """ Convert spdl to result (using Scyther) """

        scyther = Scyther.Scyther()
        if sys.platform.startswith('win'):
            scyther.program = "c:\\Scyther.exe"
            if not os.path.isfile(scyther.program):
                print "I can't find the Scyther executable %s" % (scyther.program)

        scyther.setInput(self.spdl)
        self.claims = scyther.verify()
        self.summary = str(scyther)

        self.win.errors.update(self.summary)


def RunScyther(win,mode):

    global busy

    if (busy.acquire(False)):

        # start the thread
        win.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))

        win.settings.mode = mode
        t =  ScytherThread(win,win.control.GetValue(),"")
        t.start()
        win.threads = [ t ]

