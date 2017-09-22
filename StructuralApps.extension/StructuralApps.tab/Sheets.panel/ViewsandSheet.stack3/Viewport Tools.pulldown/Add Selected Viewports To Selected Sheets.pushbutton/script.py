"""Copies schedules or legends from one sheet to another. How to use:
          1. Open the source sheet
          2. Select the destination sheet(s) in the Project Browser 
          3. Start this tool
          4. Select the legend(s) or schedule(s) to copy 
          5. Click Finish"""


"""
Copyright (c) 2014-2017 Ehsan Iran-Nejad
Python scripts for Autodesk Revit

This file is part of pyRevit repository at https://github.com/eirannejad/pyRevit

pyRevit is a free set of scripts for Autodesk Revit: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3, as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See this link for a copy of the GNU General Public License protecting this package.
https://github.com/eirannejad/pyRevit/blob/master/LICENSE
"""

__window__.Close()

from Autodesk.Revit.DB import Transaction, Viewport, ViewSheet, ScheduleSheetInstance, ViewType
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.UI.Selection import ObjectType

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

selSheets = []
selViewports = []

curview = uidoc.ActiveView
for elId in uidoc.Selection.GetElementIds():
    el = doc.GetElement(elId)
    if isinstance(el, ViewSheet):
        selSheets.append(el)

if len(selSheets) > 0:
    if int(__revit__.Application.VersionNumber) > 2014:
        cursheet = uidoc.ActiveGraphicalView
        for v in selSheets:
            if cursheet.Id == v.Id:
                selSheets.remove(v)
    else:
        cursheet = selSheets[0]
        selSheets.remove(cursheet)

    uidoc.ActiveView = cursheet
    sel = uidoc.Selection.PickObjects(ObjectType.Element)
    for el in sel:
        selViewports.append(doc.GetElement(el))

    if len(selViewports) > 0:
        with Transaction(doc, 'Add Viewports to Sheets') as t:
            t.Start()
            for sht in selSheets:
                for vp in selViewports:
                    if isinstance(vp, Viewport):
                        nvp = Viewport.Create(doc, sht.Id, vp.ViewId, vp.GetBoxCenter())
                        nvp.ChangeTypeId(vp.GetTypeId())
                    elif isinstance(vp, ScheduleSheetInstance):
                        ScheduleSheetInstance.Create(doc, sht.Id, vp.ScheduleId, vp.Point)
            t.Commit()
    else:
        TaskDialog.Show('pyrevit', 'At least one viewport must be selected.')
else:
    TaskDialog.Show('pyrevit', 'At least one sheet must be selected.')
