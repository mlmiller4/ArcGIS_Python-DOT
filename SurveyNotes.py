#-------------------------------------------------------------------------------
# Name:        SurveyNotes.py
# Purpose:     To generate a table from CCE Project data.
#-------------------------------------------------------------------------------

import arcpy, os, time
from arcpy import env

# Truncate Table before processing to clear table
def truncateTable(table_path):

    rowCount = int(arcpy.GetCount_management(table_path).getOutput(0))
    arcpy.AddMessage ("Existing Rows..." + str(rowCount))
    print ("Existing Rows..." + str(rowCount))
	
    if rowCount > 0:
        arcpy.AddMessage("Truncate Populated Table... ")
        print "Truncate Populated Table..."        
        arcpy.DeleteRows_management(table_path)
    else:
        arcpy.AddMessage("Count Is Good, Proceed...")
        print "Count Is Good, Proceed..."
        pass

# Label Feature Class and OID To Table
def mainRun(cce, blockNo, output_path, mapBook, mapPrefix):

    # Setup Data Driven MXD
    mxd = arcpy.mapping.MapDocument(mapBook)

    # Check if MXD supports Data Driven Pages
    if mxd.isDDPEnabled:
        arcpy.AddMessage("Data Driven Pages Is Enabled...")
        pass
    else:
        arcpy.AddMessage("Data Driven Pages Is Disabled...")
        sys.exit
		
    # Concatenate cce and blockNo to make pageNo
    pageNo = str(cce + "_" + blockNo)
    arcpy.AddMessage("Processing Project " + cce)

    # Where Clause to update the Project Calculations layer. Needed to improve MXD opening speed
    whereclause = "PageNo = " + "\'" + cce + "_" + str(blockNo) + "\'"
    print whereclause

    #Loop through data frame and update the definition query in the Project Calculations layer
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    for lyr in arcpy.mapping.ListLayers(mxd, data_frame=df):
            if lyr.name == "Project Calculations":
               lyr.definitionQuery = whereclause
            else:
                if lyr.supports("serviceProperties"):

                    if "-RS-" in cce:
                        cce = cce.replace("-RS-", "-ASlRS-")
                    if "-RA-" in cce:
                        cce = cce.replace("-RA-", "-AAlRA-")
                    if "-AS-" in cce:
                        cce = cce.replace("-AS-", "-ASlRS-")
                    if "-AA-" in cce:
                        cce = cce.replace("-AA-", "-AAlRA-")

                    lyr.definitionQuery = "PageNo = " + "\'" + cce + "_" + str(blockNo) + "\'"

    """Added Combo Project Text"""
    for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
            if elm.name == "projectElm":
                elm.text = cce

    # Search PageNo Field within Calculation Layer Table for User PageNo
    mxd.dataDrivenPages.refresh()
    page_Count = mxd.dataDrivenPages.pageCount
    print "Total Number Of Pages... " + str(page_Count)
    pageNum = mxd.dataDrivenPages.getPageIDFromName(pageNo)
    arcpy.AddMessage("Locating Specified Page...")
    mxd.dataDrivenPages.currentPageID = pageNum
    arcpy.AddMessage("Located " + str(pageNum))

    """Added to change save file name"""
    pageNo = str(cce + "_" + blockNo)

    # Save Page from Mapbook
    mxd.saveACopy(output_path +"\\" + str(mapPrefix) + "_" + str(pageNo) + '.mxd')    
    arcpy.mapping.ExportToPDF(mxd, output_path +"\\" + str(mapPrefix) + "_" + str(pageNo) + "_DRAFT.pdf")
    arcpy.AddMessage("The output has been saved to the following location: " + output_path)
    print ("New mxd Is Located... " + output_path)
    del mxd, cce, blockNo, output_path, mapPrefix



cce = arcpy.GetParameterAsText(0)
if cce == "#" or not cce:
    cce = "05-ASlRS-703"
blockNo = arcpy.GetParameterAsText(1)
if blockNo == "#" or not blockNo:
    blockNo = '1'
mapPrefix = arcpy.GetParameterAsText(2)
if mapPrefix == "#" or not mapPrefix:
    mapPrefix = "SurveyNotes"

# Assign variables to both path and name of Template Table #
mapBook = arcpy.GetParameterAsText(3)
if mapBook == "#" or not mapBook:
    mapBook == r"\\lex-srv02\gis\projects\IL\Chicago\v4\Map_Docs\2013\Final\SurveyNotes\CDOT_SurveyNotes.mxd"
table_path = arcpy.GetParameterAsText(4)
if table_path == "#" or not table_path:
    table_path = r"\\lex-srv02\gis\projects\IL\Chicago\v4\Tables\Template\Template_GDB.gdb\CIC"

truncateTable(table_path)
dbfTable = table_path

SDE_Base = arcpy.GetParameterAsText(5)
if SDE_Base == "#" or not SDE_Base:
    SDE_Base = r"\\lex-srv02\gis\projects\IL\Chicago\v4\Spatial\gdb\Lex_CDOT_Menu_MobileSync.sde\Lex_CDOT_Menu_MobileSync.DBO.Ops"
output_path = arcpy.GetParameterAsText(6)
if output_path == "#" or not output_path:
    output_path = r"\\lex-srv02\gis\projects\IL\Chicago\v4\Tables\Template"

# List Feature Classes
env.workspace = SDE_Base

descSDE = arcpy.Describe(SDE_Base)
sdeName = descSDE.baseName[:-3]
print sdeName

fc_List = arcpy.ListFeatureClasses("*")
print fc_List

# Where Clause for CCE Number
whereClause = '"StrCCEProjectNumber"' + " = '" + str(cce) + "' AND" + '"BlockNo"' + " = " + str(blockNo)

skip1 = sdeName + "AGM_FieldCrewLog"
skip2 = sdeName + "AGM_FieldCrewMembers"
prjCL = sdeName + "ProjectCenterline"

for fc in fc_List:
    print fc
    if fc == skip1:
        pass
    elif fc == skip2:
        pass

    elif fc == prjCL:
        whereClause2 = "\"strCCEProjectNumber\"" + " = '" + cce + "'"
        s_cur = arcpy.SearchCursor(fc, whereClause2, "", "", ""); print "Search cursor set..."
        desc = arcpy.Describe(fc)
        fieldlist = []
        for field in desc.fields:
            fieldlist.append(field.name)

        #Create Insert Cursor (It is more efficient if the Insert Cursor is created outside the loop)
        i_cursSDE = arcpy.InsertCursor(dbfTable)

        for s_row in s_cur:
            row = i_cursSDE.newRow()
            z0 = ""
            z1 = ""
            z2 = ""
            z3 = ""
            z4 = ""
            if "MeasureType" in fieldlist:
                z0 = s_row.getValue("MeasureType")
                row.MeasureType = z0
            if "OBJECTID" in fieldlist:
                x = s_row.getValue("OBJECTID")
                row.SDE_ID = str(x)
            if "AlleyType" in fieldlist:
                z1 = s_row.getValue("AlleyType")
                row.AlleyType = z1
            if "UtilityType" in fieldlist:
                z2 = s_row.getValue("UtilityType")
                row.UtilityType = z2
            if "SurveyNote" in fieldlist:
                z3 = s_row.getValue("SurveyNote")
                row.SurveyNote = z3
            if "Comments" in fieldlist:
                z4 = s_row.getValue("Comments")
                row.Comments = z4
            z5 = fc
            row.FeatureClass = fc

            i_cursSDE.insertRow(row); print "Row Inserted..."
    
        del s_cur, i_cursSDE

    else:
        s_cur = arcpy.SearchCursor(fc, whereClause, "", "", ""); print "Search cursor set..."
        desc = arcpy.Describe(fc)
        fieldlist = []
        for field in desc.fields:
            fieldlist.append(field.name)

        #Create Insert Cursor (It is more efficient if the Insert Cursor is created outside the loop)
        i_cursSDE = arcpy.InsertCursor(dbfTable)

        for s_row in s_cur:
            row = i_cursSDE.newRow()
            z0 = ""
            x = ""
            z1 = ""
            z2 = ""
            z3 = ""
            z4 = ""
            if "MeasureType" in fieldlist:
                z0 = s_row.getValue("MeasureType")
                row.MeasureType = z0
            if "OBJECTID" in fieldlist:
                x = s_row.getValue("OBJECTID")
                row.SDE_ID = x
            if "AlleyType" in fieldlist:
                z1 = s_row.getValue("AlleyType")
                row.AlleyType = z1
            if "UtilityType" in fieldlist:
                z2 = s_row.getValue("UtilityType")
                row.UtilityType = z2
            if "SurveyNote" in fieldlist:
                z3 = s_row.getValue("SurveyNote")
                row.SurveyNote = z3
            if "Comments" in fieldlist:
                z4 = s_row.getValue("Comments")
                row.Comments = z4
            z5 = fc
            row.FeatureClass = fc

            i_cursSDE.insertRow(row); print "Row Inserted..."
    
        del s_cur, i_cursSDE

# Execute TableToDBASE
"""Added to change file name"""
if "-RS-" in cce:
    cce = cce.replace("-RS-", "-ASlRS-")
if "-RA-" in cce:
    cce = cce.replace("-RA-", "-AAlRA-")
if "-AS-" in cce:
    cce = cce.replace("-AS-", "-ASlRS-")
if "-AA-" in cce:
    cce = cce.replace("-AA-", "-AAlRA-")

# Concatenate cce and blockNo to make pageNo
new_cce = cce.replace('-', '_')
pageNo = str(new_cce + "_" + blockNo)
arcpy.AddMessage("Exporting Table to DBF...")

arcpy.TableToTable_conversion(dbfTable, output_path, mapPrefix + "_" + pageNo + ".dbf", '"SurveyNote"' + "Is Not Null OR" + '"Comments"' + "Is Not Null")



arcpy.AddMessage("Successful Completion...")
del table_path
print "DONE"

mainRun(cce, blockNo, output_path, mapBook, mapPrefix)
