#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
Dynamic workspace names for Sway
THIS VERSION DOES NOT WORK ON SWAY WITH NOT-YET-FIXED i3ipc v1.7.1 MODULE

The script should also work on i3, but for some reason it works well for me on 2 machines, and loops on the 3rd one.
Use on i3 at your own risk.

Author: Piotr Miller
e-mail: nwg.piotr@gmail.com
Project: https://github.com/nwg-piotr/swayinfo
License: GPL3

Depends on: i3ipc-python (python-i3ipc) >1.7.1
"""

from i3ipc import Connection, Event

# truncate workspace name to this value
max_width = 30

# Create the Connection object that can be used to send commands and subscribe to events.
i3 = Connection()


# A glyph will substitute the WS name if no window active, otherwise it'll be prepended to the window name
# Add more if you use more than 8 workspaces
def glyph(ws_number):
    # glyphs = ["", "", "", "", "", ""]
    glyphs = ["", "", "", "", "", "", "", ""]
    # 
    # Or you may use words instead of glyphs:
    # glyphs = ["HOME", "WWW", "FILE", "GAME", "TERM", "PIC", "TXT", "CODE"]
    try:
        return glyphs[ws_number - 1]
    except IndexError:
        return "?"


# Name the workspace after the focused window name
def assign_generic_name(i3, e):
    try:
        con = i3.get_tree().find_focused()
        if not con.type == 'workspace':         # avoid renaming new empty workspaces on 'binding' event
            # con.type == 'floating_con'        - indicates floating enabled in Sway
            # con.floating                      - may be equal 'auto_on' or 'user_on' in i3
            is_floating = con.type == 'floating_con' or con.floating and '_on' in con.floating

            # Tiling mode or floating indication
            layout = con.parent.layout
            if layout == 'splith':
                split_text = '⇢' if not is_floating else ''
            elif layout == 'splitv':
                split_text = '⇣' if not is_floating else ''
            else:
                split_text = ''

            ws_old_name = con.workspace().name
            ws_name = "%s: %s\u00a0%s %s " % (con.workspace().num, glyph(con.workspace().num), split_text, con.name)
            name = ws_name if len(ws_name) <= max_width else ws_name[:max_width - 1] + "…"

            i3.command('rename workspace "%s" to %s' % (ws_old_name, name))

        else:
            # Give the workspace a generic name: "number: glyph" (like "1: ")
            ws_num = con.workspace().num
            ws_new_name = "%s: %s" % (ws_num, glyph(ws_num))

            i3.command('rename workspace to "{}"'.format(ws_new_name))

        print('{} focused'.format(con.type))

    except Exception as ex:
        exit(ex)


# In sway it's possible to open a new window w/o moving focus; let's give the workspace a name anyway.
def on_window_new(i3, e):
    print('on_window_new OK')
    try:
        con = i3.get_tree().find_by_id(e.container.id)
        ws_num = con.workspace().num
        w_name = con.name if con.name else ''
        print('ws_num {}, w_name {}'.format(ws_num, w_name))

        if w_name and ws_num:
            name = "%s: %s\u00a0%s" % (ws_num, glyph(ws_num), w_name)
            i3.command('rename workspace "%s" to %s' % (ws_num, name))
    except:
        pass


def main():
    # Subscribe to events
    i3.on(Event.WORKSPACE_FOCUS, assign_generic_name)
    i3.on(Event.WINDOW_FOCUS, assign_generic_name)
    i3.on(Event.WINDOW_TITLE, assign_generic_name)
    i3.on(Event.WINDOW_CLOSE, assign_generic_name)
    i3.on(Event.WINDOW_NEW, on_window_new)
    i3.on("binding", assign_generic_name)

    i3.main()


if __name__ == "__main__":
    main()