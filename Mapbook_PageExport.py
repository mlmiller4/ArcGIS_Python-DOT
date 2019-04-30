#-------------------------------------------------------------------------------
# Name:        Mapbook_PageExport.py
# Purpose:     To export a single page from mxd that matches user input of CCE and Block number.
#-------------------------------------------------------------------------------

import arcpy, os, sys,  textwrap

def mainRun(cce, blockNo, output_path, mapBook, mapPrefix):
    # Setup Data Driven MXD
    mxd = arcpy.mapping.MapDocument(mapBook)
    cceInput = cce

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

            if "-AS-" in cce:
                if lyr.name == "RS - Display Data - Turn off in AS":
                    lyr.visible = False
            if "-RS-" in cce and lyr.name == "AS - Display Data - Turn off in RS":
                lyr.visible = False
            if "-CS-" in cce and lyr.name == "AS - Display Data - Turn off in RS":
                lyr.visible = False
            if "-CC-" in cce and lyr.name == "AS - Display Data - Turn off in RS":
                lyr.visible = False
            if "-CO-" in cce and lyr.name == "AS - Display Data - Turn off in RS":
                lyr.visible = False
            if "-RA-" in cce and lyr.name == "AS - Display Data - Turn off in RS":
                lyr.visible = False

            if "-RS-" in cce and lyr.isGroupLayer:
                for sublyr in lyr:
                    if sublyr.name == "Speed Hump":
                        sublyr.visible = False
            if "-RS-" in cce and lyr.isGroupLayer:
                for sublyr in lyr:
                    if sublyr.name == "Pavement Markings":
                        sublyr.visible = False
            if "-RS-" in cce and lyr.isGroupLayer:
                for sublyr in lyr:
                    if sublyr.name == "Utilities":
                        sublyr.visible = False
            if "-RS-" in cce and lyr.isGroupLayer:
                for sublyr in lyr:
                    if sublyr.name == "Other Pavement":
                        sublyr.visible = False


    projType = ""

    for lyr in arcpy.mapping.ListLayers(mxd, data_frame=df):

            if lyr.name == "Project Calculations":
               lyr.definitionQuery = whereclause
               projCalc = lyr.dataSource
            else:
                if lyr.supports("serviceProperties"):

                    if "-RS-" in cce:
                        cce = cce.replace("-RS-", "-ASlRS-")
                        projType = "RS"
                    if "-RA-" in cce:
                        cce = cce.replace("-RA-", "-AAlRA-")
                        projType = "RA"
                    if "-AS-" in cce:
                        cce = cce.replace("-AS-", "-ASlRS-")
                        projType = "AS"
                    if "-AA-" in cce:
                        cce = cce.replace("-AA-", "-AAlRA-")
                        projType = "AA"

                    existDefQuery = lyr.definitionQuery
                    if len(existDefQuery) == 0:
                        if lyr.name == "Dimension":
                            lyr.definitionQuery = "PageNo = " + "\'" + cce + "_" + str(blockNo) + "\'" + " AND projectType = " + "\'" + projType + "\'"
                        else:
                            lyr.definitionQuery = "PageNo = " + "\'" + cce + "_" + str(blockNo) + "\'"
                    else:
                        if lyr.name == "Dimension":
                            lyr.definitionQuery = existDefQuery + " AND PageNo = " + "\'" + cce + "_" + str(blockNo) + "\'" + " AND projectType = " + "\'" + projType + "\'"
                        else:
                            lyr.definitionQuery = existDefQuery + " AND PageNo = " + "\'" + cce + "_" + str(blockNo) + "\'"



    # Search PageNo Field within Calculation Layer Table for User PageNo
    mxd.dataDrivenPages.refresh()
    page_Count = mxd.dataDrivenPages.pageCount
    print "Total Number Of Pages... " + str(page_Count)
    pageNum = mxd.dataDrivenPages.getPageIDFromName(pageNo)
    arcpy.AddMessage("Locating Specified Page...")
    mxd.dataDrivenPages.currentPageID = pageNum
    arcpy.AddMessage("Located " + str(pageNum))
    mxd.dataDrivenPages.refresh()

    extent = mxd.dataDrivenPages.indexLayer.getExtent()
    df.extent = extent
    scaleFoot = int(round(((df.scale * 1.02) /12.0), 2)) #Fix to zoom and scale problem
    df.scale = round((scaleFoot * 12), -1)
    arcpy.RefreshActiveView()


     #IHC Pavement Markings - Toggle for RS
    for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
        if "-RS-" in cceInput and elm.name == "pm_4":
            elm.text = " "
        if "-RS-" in cceInput and elm.name == "pm_6":
            elm.text = " "
        if "-RS-" in cceInput and elm.name == "pm_24":
            elm.text = " "

    #-RS- Calc Toggle
        if "-AS-" in cceInput and elm.name == "T3LF_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "T3LFRamp_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "T4_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "T4Ramp_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "PCC5SF_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "PCC5SFRamp_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "PCC8SF_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "PCC8SFRamp_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "PCC7BCSY_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "PCC7ATOTon_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "PCC5RampNum_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "TopSCY_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "HydSSY_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "SawCLF_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "DriveAlleyATOTon_elm":
            elm.text = " "
        if "-AS-" in cceInput and elm.name == "DriveAlleyCSY_elm":
            elm.text = " "

    """Added Combo Project Text"""
    if mapPrefix == "PhotoLines":
        pageNo = str(cce + "_" + blockNo)
        for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
                if elm.name == "projectElm":
                    elm.text = cce
    if mapPrefix != "PhotoLines":
        pageNo = str(cceInput + "_" + blockNo)
        for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
                if elm.name == "projectElm":
                    elm.text = cceInput

    # Save Page from Mapbook
    mxd.saveACopy(output_path +"\\" + str(mapPrefix) + "_" + str(pageNo) + '.mxd')    
    arcpy.mapping.ExportToPDF(mxd, output_path +"\\" + str(mapPrefix) + "_" + str(pageNo) + "_DRAFT.pdf")
    arcpy.AddMessage("The output has been saved to the following location: " + output_path)
    print ("New mxd Is Located... " + output_path)
    del mxd, cce, blockNo, output_path, mapPrefix

# Assign Parameters
cce = arcpy.GetParameterAsText(0)
if cce == "#" or not cce:
    cce = "11-AS-810"    
blockNo = arcpy.GetParameterAsText(1)

if blockNo == "#" or not blockNo:
    blockNo = "1"    
mapPrefix = arcpy.GetParameterAsText(2)

if mapPrefix == "#" or not mapPrefix:
    mapPrefix = "IHC"
mapBook = arcpy.GetParameterAsText(3)

if mapBook == "#" or not mapBook:
    mapBook = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Map_Docs\Draft\2014\CDOT_MenuProgram_8_5x14_2014.mxd"    
output_path = arcpy.GetParameterAsText(4)

if output_path == "#" or not output_path:
    output_path = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Map_Docs\Final\Menu_Mapbook_PageExport"

arcpy.AddMessage("Assigning " + mapPrefix + " parameters for project " + cce)

mainRun(cce, blockNo, output_path, mapBook, mapPrefix)



