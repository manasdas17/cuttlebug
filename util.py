import wx

def menu_item(window, menu, label, func, icon=None, kind=wx.ITEM_NORMAL, toolbar=None, tracker=None):
    item = wx.MenuItem(menu, -1, label, kind=kind)
    if func:
        window.Bind(wx.EVT_MENU, func, id=item.GetId())
    if icon:
        item.SetBitmap(get_icon(icon))
    menu.AppendItem(item)
    if toolbar and icon:
        tool_item = toolbar.AddSimpleTool(-1, get_icon(icon), label)
        if func:
            window.Bind(wx.EVT_TOOL, func, id=tool_item.GetId())
    if tracker != None:
        tracker.append(item)
    return item
    
def tool_item(window, toolbar, label, func, icon):
    item = toolbar.AddSimpleTool(-1, get_icon(icon), label)
    if func:
        window.Bind(wx.EVT_TOOL, func, id=item.GetId())
    return item

def get_icon(file):
    file = 'icons/%s' % file
    return wx.Bitmap(file)


