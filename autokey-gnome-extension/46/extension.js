/* extension.js
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

/* exported init */

import Gio from 'gi://Gio';
import * as Keyboard from 'resource:///org/gnome/shell/ui/status/keyboard.js';

const MR_DBUS_IFACE = `
<node>
   <interface name="org.gnome.Shell.Extensions.AutoKey">
      <method name="GetActiveWorkspaceIndex">
         <arg type="i" direction="out" name="wksid" />
      </method>
      <method name="GetActiveWorkstationIndex">
         <arg type="i" direction="out" name="wksid" />
      </method>
      <method name="List">
         <arg type="s" direction="out" name="win" />
      </method>
      <method name="Details">
         <arg type="u" direction="in" name="winid" />
         <arg type="s" direction="out" name="win" />
      </method>
      <method name="Properties">
         <arg type="u" direction="in" name="winid" />
         <arg type="s" direction="out" name="win" />
      </method>
      <method name="Stick">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="UnStick">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="Maximize">
         <arg type="u" direction="in" name="winid" />
         <arg type="i" direction="in" name="directions" />
      </method>
      <method name="UnMaximize">
         <arg type="u" direction="in" name="winid" />
         <arg type="i" direction="in" name="directions" />
      </method>
      <method name="Shade">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="UnShade">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="MakeFullscreen">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="UnMakeFullscreen">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="MakeAbove">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="UnMakeAbove">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="GetTitle">
         <arg type="u" direction="in" name="winid" />
         <arg type="s" direction="out" name="win" />
      </method>
      <method name="MoveToWorkspace">
         <arg type="u" direction="in" name="winid" />
         <arg type="i" direction="in" name="workspaceNum" />
      </method>
      <method name="MoveResize">
         <arg type="u" direction="in" name="winid" />
         <arg type="i" direction="in" name="x" />
         <arg type="i" direction="in" name="y" />
         <arg type="u" direction="in" name="width" />
         <arg type="u" direction="in" name="height" />
      </method>
      <method name="Resize">
         <arg type="u" direction="in" name="winid" />
         <arg type="u" direction="in" name="width" />
         <arg type="u" direction="in" name="height" />
      </method>
      <method name="Move">
         <arg type="u" direction="in" name="winid" />
         <arg type="i" direction="in" name="x" />
         <arg type="i" direction="in" name="y" />
      </method>
      <method name="Minimize">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="UnMinimize">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="Activate">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="Focus">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="Raise">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="SwitchWorkspace">
         <arg type="u" direction="in" name="wksid" />
      </method>
      <method name="Close">
         <arg type="u" direction="in" name="winid" />
      </method>
      <method name="GetMouseLocation">
            <arg type="i" direction="out" name="x" />
            <arg type="i" direction="out" name="y" />
      </method>
      <method name="ScreenSize">
            <arg type="i" direction="out" name="width" />
            <arg type="i" direction="out" name="height" />
      </method>
      <method name="GetKeymap">
            <arg type="s" direction="out" name="keymap" />
      </method>
      <method name="CheckVersion">
            <arg type="s" direction="out" name="version" />
      </method>
   </interface>
</node>`;

/*  meta_window API doc: https://gjs-docs.gnome.org/meta10~10/meta.window  */

export default class Extension {
    enable() {
        this._dbus = Gio.DBusExportedObject.wrapJSObject(MR_DBUS_IFACE, this);
        this._dbus.export(Gio.DBus.session, '/org/gnome/Shell/Extensions/AutoKey');
    }

    disable() {
        this._dbus.flush();
        this._dbus.unexport();
        delete this._dbus;
    }

    _get_window_by_wid(winid) {
        return global.get_window_actors().find(w => w.meta_window.get_id() == winid);
    }

    _get_workspace_by_wks(wksid) {
        let mgr = global.workspace_manager;
        if (mgr) {
            return mgr.get_workspace_by_index(wksid);
        }
        return;
    }

    GetActiveWorkspaceIndex() {
        let workspaceManager = global.workspace_manager;
        if (workspaceManager) {
            return workspaceManager.get_active_workspace_index()
        }
        return;
    }

    List() {
        let win = global.get_window_actors();
        let workspaceManager = global.workspace_manager;
        var winJsonArr = [];
        win.forEach(function (w) {
            winJsonArr.push({
                wm_class: w.meta_window.get_wm_class(),
                wm_class_instance: w.meta_window.get_wm_class_instance(),
                wm_title: w.meta_window.get_title(),
                workspace: w.meta_window.get_workspace().index(),
                desktop: w.meta_window.get_monitor(),
                pid: w.meta_window.get_pid(),
                id: w.meta_window.get_id(),
                frame_type: w.meta_window.get_frame_type(),
                window_type: w.meta_window.get_window_type(),
                width: w.get_width(),
                height: w.get_height(),
                x: w.get_x(),
                y: w.get_y(),
                focus: w.meta_window.has_focus(),
                in_current_workspace: w.meta_window.located_on_workspace(workspaceManager.get_active_workspace()),
            });
        });
        return JSON.stringify(winJsonArr);
    }

    Details(winid) {
        let w = this._get_window_by_wid(winid);
        let workspaceManager = global.workspace_manager;
        let currentmonitor = global.display.get_current_monitor();
        // let monitor = global.display.get_monitor_geometry(currentmonitor);
        if (w) {
            return JSON.stringify({
                wm_class: w.meta_window.get_wm_class(),
                wm_class_instance: w.meta_window.get_wm_class_instance(),
                pid: w.meta_window.get_pid(),
                id: w.meta_window.get_id(),
                width: w.get_width(),
                height: w.get_height(),
                x: w.get_x(),
                y: w.get_y(),
                focus: w.meta_window.has_focus(),
                in_current_workspace: w.meta_window.located_on_workspace(workspaceManager.get_active_workspace()),
                moveable: w.meta_window.allows_move(),
                resizeable: w.meta_window.allows_resize(),
                canclose: w.meta_window.can_close(),
                canmaximize: w.meta_window.can_maximize(),
                maximized: w.meta_window.get_maximized(),
                canminimize: w.meta_window.can_minimize(),
                /*  canshade: w.meta_window.can_shade(), */
                display: w.meta_window.get_display(),
                /*  frame_bounds: w.meta_window.get_frame_bounds(),  */
                frame_type: w.meta_window.get_frame_type(),
                window_type: w.meta_window.get_window_type(),
                layer: w.meta_window.get_layer(),
                monitor: w.meta_window.get_monitor(),
                role: w.meta_window.get_role(),
                area: w.meta_window.get_work_area_current_monitor(),
                area_all: w.meta_window.get_work_area_all_monitors(),
                area_cust: w.meta_window.get_work_area_for_monitor(currentmonitor),
            });
        } else {
            throw new Error('Not found');
        }
    }

    Properties(winid) {
        /*  Can't find a function that works to change modal or shaded.  */
        /*  There are functions that change shaded but no way to get current state.  */
        /*  Window properties are not writeable.  */
        let w = this._get_window_by_wid(winid);
        if (w) {
            return JSON.stringify({
                is_modal: (w.meta_window['window-type'] == 4),
                /*  is_sticky - not available  */
                is_maximized_vert: w.meta_window['maximized-vertically'],
                is_maximized_horz: w.meta_window['maximized-horizontally'],
                /*  is_shaded - not available  */
                is_skip_taskbar: w.meta_window['skip_taskbar'],
                is_hidden: w.meta_window.is_hidden(),
                is_fullscreen: w.meta_window['fullscreen'],
                is_above: w.meta_window['above']
            });
        } else {
            throw new Error('Not found');
        }
    }

    Stick(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.stick();
        else
            throw new Error('Not found');
    }

    UnStick(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.unstick();
        else
            throw new Error('Not found');
    }

    Maximize(winid, directions) {
        /*  Directions:
         *  1 - horizontal
         *  2 - vertical
         *  3 - both
         */
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.maximize(directions);
        else
            throw new Error('Not found');
    }

    UnMaximize(winid, directions) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.unmaximize(directions);
        else
            throw new Error('Not found');
    }

    /*  Doesn't work  */
    Shade(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.shade(global.get_current_time());
        else
            throw new Error('Not found');
    }

    /*  Doesn't work  */
    UnShade(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.unshade(global.get_current_time());
        else
            throw new Error('Not found');
    }

    MakeFullscreen(winid, fullscreen) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.make_fullscreen();
        else
            throw new Error('Not found');
    }

    UnMakeFullscreen(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.unmake_fullscreen();
        else
            throw new Error('Not found');
    }

    MakeAbove(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.make_above();
        else
            throw new Error('Not found');
    }

    UnMakeAbove(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            w.meta_window.unmake_above();
        else
            throw new Error('Not found');
    }

    GetTitle(winid) {
        let w = this._get_window_by_wid(winid);
        if (w)
            return w.meta_window.get_title();
        else
            throw new Error('Not found');
    }

    MoveToWorkspace(winid, workspaceNum) {
        let win = this._get_window_by_wid(winid).meta_window;
        if (win)
            win.change_workspace_by_index(workspaceNum, false);
        else
            throw new Error('Not found');
    }

    MoveResize(winid, x, y, width, height) {
        let win = this._get_window_by_wid(winid);

        if (win) {
            if (win.meta_window.maximized_horizontally || win.meta_window.maximized_vertically)
                win.meta_window.unmaximize(3);
            win.meta_window.move_resize_frame(1, x, y, width, height);
        } else {
            throw new Error('Not found');
        }
    }

    Resize(winid, width, height) {
        let win = this._get_window_by_wid(winid);
        if (win) {
            if (win.meta_window.maximized_horizontally || win.meta_window.maximized_vertically)
                win.meta_window.unmaximize(3);
            win.meta_window.move_xCoordresize_frame(1, win.get_x(), win.get_y(), width, height);
        } else {
            throw new Error('Not found');
        }
    }

    Move(winid, x, y) {
        let win = this._get_window_by_wid(winid);
        if (win) {
            if (win.meta_window.maximized_horizontally || win.meta_window.maximized_vertically)
                win.meta_window.unmaximize(3);
            win.meta_window.move_frame(1, x, y);
        } else {
            throw new Error('Not found');
        }
    }

    Minimize(winid) {
        let win = this._get_window_by_wid(winid).meta_window;
        if (win)
            win.minimize();
        else
            throw new Error('Not found');
    }

    UnMinimize(winid) {
        let win = this._get_window_by_wid(winid).meta_window;
        if (win)
            win.unminimize();
        else
            throw new Error('Not found');
    }

    Raise(winid) {
        let win = this._get_window_by_wid(winid).meta_window;
        if (win)
            win.raise();
        else
            throw new Error('Not found');
    }

    /*  Doesn't work in Wayland, use Raise instead */
    Activate(winid) {
        let win = this._get_window_by_wid(winid).meta_window;
        if (win)
            win.activate(global.get_current_time());
        else
            throw new Error('Not found');
    }

    /*  Doesn't work in Wayland, use Raise instead */
    Focus(winid) {
        let win = this._get_window_by_wid(winid).meta_window;
        if (win)
            win.focus(global.get_current_time());
        else
            throw new Error('Not found');
    }

    SwitchWorkspace(wksid) {
        let wks = this._get_workspace_by_wks(wksid);
        if (wks)
            wks.activate(global.get_current_time());
        else
            throw new Error('Not found');
    }

    Close(winid) {
        let win = this._get_window_by_wid(winid).meta_window;
        if (win)
            win.kill();
            // win.delete(Math.floor(Date.now() / 1000));
        else
            throw new Error('Not found');
    }

    GetMouseLocation() {
        let [x, y, mask] = global.get_pointer();
        return [x, y];
    }

    ScreenSize() {
        return [global.screen_width, global.screen_height];
    }

    GetKeymap() {
        return Keyboard.getInputSourceManager().currentSource.id;
    }

    CheckVersion() {
        return '0.3';
    }
}

/**
 *
 */
function init() {
    // called by gnome shell when extension is loaded
    return new Extension();
}
