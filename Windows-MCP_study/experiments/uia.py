import uiautomation as uia
from dataclasses import dataclass
from enum import Enum
from windows_mcp.desktop.views import Size, Status

@dataclass
class App:
    name:str
    depth:int
    status:Status
    size:'Size'
    handle: int
    process_id:int
    
    def to_row(self):
        return [self.name, self.depth, self.status.value, self.size.width, self.size.height, self.handle]

desktop = uia.GetRootControl()  # Get the desktop control
children = desktop.GetChildren()
apps = []
for depth, child in enumerate(children):
    if isinstance(child, (uia.WindowControl, uia.PaneControl)):
        window_pattern = child.GetPattern(uia.PatternId.WindowPattern)
        if window_pattern is None:
            continue
        if window_pattern.CanMinimize and window_pattern.CanMaximize:
            apps.append(
                App(
                    **{
                        "name": child.Name,
                        "depth": depth,
                        "status": Status.NORMAL,
                        "size": Size(child.BoundingRectangle.width(), child.BoundingRectangle.height()),
                        "handle": child.NativeWindowHandle,
                        "process_id": child.ProcessId,
                    }
                )
            )

for app in apps:
    print(app.to_row())