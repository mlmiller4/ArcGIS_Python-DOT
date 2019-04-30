#-------------------------------------------------------------------------------
# Name:        LoadSDE
# Purpose:     This script loads data from a pre-processing Geodatabase into a
#              target SDE.  Any new features are inserted into the SDE, while
#              the attributes of any existing features are updated.
#
# Author:      MMiller
#-------------------------------------------------------------------------------

import arcpy, arcinfo, sys, os
from arcpy import env

def main():

    env.overwriteOutput = True
    arcpy.ClearWorkspaceCache_management()

    # Staging SDE:
    folderName = r"E:\gis\projects\Staging\Admin\prod_build"
    fileName = ["Lex_CDOT_Survey_Admin - Staging.sde", "Lex_CDOT_MapOutput_Admin - Staging(DEFAULT).sde"]

    t_v = ["DBO.Survey", "dbo.DEFAULT"]

    #Use connection files with SDE version for editing only    
    editSDE = r"E:\gis\projects\Staging\Admin\prod_build\Lex_CDOT_Preproc_Admin - Staging.sde"
    editMapbookSDE = r"E:\gis\projects\Staging\Admin\prod_build\Lex_CDOT_MapOutput_Admin - Staging(PreProc).sde"

    # Setup workspaces
    preGDB = arcpy.GetParameterAsText(0) 
    if preGDB == "#" or not preGDB:
        preGDB = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\working\PreProcessing\Lex_CDOT_Menu_PreProcessing_01072015_125937.gdb"

    preProjLines = preGDB + "\ProjectCenterline_draft"

    preBlockLines = preGDB + "\BlockCenterline_draft"

    desc = arcpy.Describe(preProjLines)
    preGDB = desc.path
    print "Path:      " + desc.path
    arcpy.AddMessage("Path:      " + desc.path)
    print "Base Name: " + desc.baseName
    arcpy.AddMessage("Base Name: " + desc.baseName)

    desc = arcpy.Describe(preBlockLines)
    print "Base Name: " + desc.baseName
    arcpy.AddMessage("Base Name: " + desc.baseName)

    # Call for connection
    f = fileName[0]
    checkConn(f, folderName)
    SDE_DEFAULT = folderName + '\\' + f
    targetSDE = SDE_DEFAULT
    descSDE = arcpy.Describe(targetSDE)
    sdeName = descSDE.connectionProperties.database
    print "sdeName = " + sdeName

    try:
        versionList = arcpy.ListVersions(targetMapbookSDE)
        if 'DBO.PreProc' in versionList:
            arcpy.DeleteVersion_management(targetMapbookSDE, 'DBO.PreProc')#Cannot remove version and recreate since its used by the connection file.
            arcpy.CreateVersion_management(targetMapbookSDE, t_v[1], "PreProc", "PUBLIC")
        else:
            arcpy.CreateVersion_management(targetSDE, t_v[1], "PreProc", "PUBLIC")
    except Exception as e:
        print "Problem creating version"

    # Call for connection
    f = fileName[1]
    checkConn(f, folderName)
    SDE_DEFAULT = folderName + '\\' + f
    targetMapbookSDE = SDE_DEFAULT
    descMB = arcpy.Describe(targetMapbookSDE)
    mbSDEName = descMB.connectionProperties.database
    print mbSDEName

    preProjLinesCombo = preProjLines.replace("\ProjectCenterline", "\ProjectCenterlineCombo")
    preBlockLinesCombo = preBlockLines.replace("\BlockCenterline", "\BlockCenterlineCombo")

    env.workspace = preGDB


    """ ************************************  Project Centerline Updates  ****************************** """
    print ""
    print "***************************************"
    print "Beginning Project Centerline Updates..."
    print "***************************************"

    # Create lists of needed field names 
    fieldsProject = ["strCCEProjectNumber", "strCDOTProjectNumber", "memAldermanComment", "memProjectComments", "memWardComment", "SHAPE@", "strReportLocation", "strReportFrom", "strReportTo", "lngMenuID", "lngWardID", "lngBlocks", "lngProjectID"] #These are the needed fields for the ProjectCenterline
    fieldsBlock = ["PageNo", "strCDOTProjectNumber", "strBlockLocation", "strBlockFrom", "strBlockTo", "SHAPE@", "strCCEProjectNumber", "BlockNo", "lngProjectID"]                            
    allFields = "*"                                                                                                                        

    #Add query to ignore RW and RC Project types
    whereClause = """"strCCEProjectNumber" NOT LIKE '%RW%' AND "strCCEProjectNumber" NOT LIKE '%RC%'"""

    #Start an editing session    
    edit = arcpy.da.Editor(editSDE)
    edit.startEditing(False, True)
    edit.startOperation()

    #Create new SearchCursor and InsertCursor for ProjectCenterline_v3
    s_curGDB =  arcpy.da.SearchCursor(preProjLinesCombo, fieldsProject, whereClause); print "Search cursor set... ProjectCenterline.  Evaluating Records..."
    i_cursSDE = arcpy.da.InsertCursor(editSDE + os.sep + sdeName + ".DBO.Ops\\" + sdeName + ".DBO.ProjectCenterline", fieldsProject); print "Insert Cursor set... ProjectCenterline" 

    #Create a list to hold the records that do not have any geometry.  This list will notify the user at the end of any records that have no geometry.
    noGeometryProject = []

    # Create a list to hold project numbers that have had blocks deleted from them.
    projectsWithDeletedBlocks = []

    # Start the for loop to cycle through all the rows
    for s_row in s_curGDB:

        shape = s_row[5]    #This variable points to the Shape token, "SHAPE@"

        match = False       # A boolean value that is changed to True if the record matches a record already in the Target SDE.

        # Setup update cursor for the Target SDE - This will cycle through the existing records in the SDE.
        u_cursSDE = arcpy.da.UpdateCursor(editSDE + os.sep + sdeName + ".DBO.Ops\\" + sdeName + ".DBO.ProjectCenterline",fieldsProject, fieldsProject[0] + " = '" + s_row[0] + "'") 

        #If the feature has no geometry, it's PageNo is added to the noGeometryArray and reported to the user at the end of the script.
        if shape == None:
            noGeometryProject.append(str(s_row[0]))

        #Cycle through the records in the Target SDE and compare the PageNo value with that in the GDB.
        for u_row in u_cursSDE:
            counter = 0
            if u_row[0] == s_row[0]: 

                if u_row[1] == s_row[1]:
                    pass
                else:
                    counter = counter + 1
                    u_row[1] = s_row[1]
                if u_row[2] == s_row[2]:
                    pass
                else:
                    counter = counter + 1
                    u_row[2] = s_row[2]
                if u_row[3] == s_row[3]:
                    pass
                else:
                    counter = counter + 1
                    u_row[3] = s_row[3]
                if u_row[4] == s_row[4]:
                    pass
                else:
                    counter = counter + 1
                    u_row[4] = s_row[4]
                if u_row[6] == s_row[6]:
                    pass
                else:
                    counter = counter + 1
                    u_row[6] = s_row[6]
                if u_row[7] == s_row[7]:
                    pass
                else:
                    counter = counter + 1
                    u_row[7] = s_row[7]
                if u_row[8] == s_row[8]:
                    pass
                else:
                    counter = counter + 1
                    u_row[8] = s_row[8]
                if u_row[9] == s_row[9]:
                    pass
                else:
                    counter = counter + 1
                    u_row[9] = s_row[9]
                if u_row[10] == s_row[10]:
                    pass
                else:
                    counter = counter + 1
                    u_row[10] = s_row[10]
                if u_row[11] == s_row[11]:
                    pass
                else:
                    # if value for lngBlocks is different, then a block has been deleted.
                    # Add project number to a list of projects with deleted blocks
                    if u_row[11] > s_row[11]:
                        projectsWithDeletedBlocks.append(s_row[0])

                    counter = counter + 1
                    u_row[11] = s_row[11]

                if u_row[12] == s_row[12]:
                    pass
                else:
                    counter = counter + 1
                    u_row[12] = s_row[12]

                if counter > 0:
                    u_cursSDE.updateRow(u_row)
                    print "Update " + str(counter) + " objects to row."
                    print str(s_row[0]) + " was updated."
                else:
                    print str(s_row[0]) + ": All attributes match. Skipping Record."
                    pass                  #If a matching record is found, update the record

                match = True #Boolean to determine if its a new project or not

        if match == False:                                  #If no matching record is found in the SDE, the Insert Cursor will insert the new record.
            i_cursSDE.insertRow(s_row)
            print str(s_row[0]) + " was inserted."


        del u_cursSDE       #Delete the Update Cursor before re-creating it in the next iteration of the loop.


    del i_cursSDE, s_curGDB           #Delete the InsertCursor pointing to the Target SDE and the Search Cursor pointing to the GDB.

    print "Number of projects with deleted blocks = " + str(len(projectsWithDeletedBlocks))
    for proj in projectsWithDeletedBlocks:
        print proj + "has a deleted block."

    print "*************************************"
    print "ProjectCenterline updating is complete."
    print "*************************************"
    arcpy.AddMessage("*************************************")
    arcpy.AddMessage("ProjectCenterline updating is complete.")
    arcpy.AddMessage("*************************************")




    """*********************************  Block Centerline Updates  **********************************"""
    print ""
    print "***************************************"
    print "Beginning Block Centerline Updates..."
    print "***************************************"

    #Create Search Cursor - Cusor is initially set to the BlockCenterline_v3 dataset.
    s_curGDB = arcpy.da.SearchCursor(preBlockLinesCombo, fieldsBlock, whereClause); print "Search cursor set... BlockCenterline. Evaluating Records..."

    #Create Insert Cursor (It is more efficient if the Insert Cursor is created outside the loop)
    i_cursSDE = arcpy.da.InsertCursor(editSDE + os.sep + sdeName + ".DBO.Ops\\" + sdeName + ".DBO.BlockCenterline", fieldsBlock) #Change for final once final SDE in place <SAH>

    #Create a list to hold the records that do not have any geometry.  This list will notify the user at the end of any records that have no geometry.
    noGeometryBlock = []

    # Set Update Cursor to point to the BlockCenterline layer in the SDE
    u_cursSDE = arcpy.da.UpdateCursor(editSDE + os.sep + sdeName + ".DBO.Ops\\" + sdeName + ".DBO.BlockCenterline",fieldsBlock)


    # Cycle through the SDE's Block Centerline layer.  All blocks with a project number found in the projectsWithDeletedBlocks list will be renamed to have an "XX" in place of their letters.
    numBlocksDeleted = 0

    for u_row in u_cursSDE:
        if u_row[6] in projectsWithDeletedBlocks:
            newRow = u_row          # Create a copy of the current row

            oldProjNum = u_row[6]
            if len(oldProjNum) > 9:             # Create new project number with XX in place of letters.
                newProjNum = oldProjNum[0:3] + "YY" + oldProjNum[5] + "YY" + oldProjNum[8:]
            else:
                newProjNum = oldProjNum[0:3] + "YY" + oldProjNum[5:]

            newRow[6] = newProjNum                              # Give new row the modified project number.
            newRow[0] = newProjNum + "_" + str(u_row[7])        # Update PageNo with changed project number.
            u_cursSDE.deleteRow()                               # Delete the old row.
            i_cursSDE.insertRow(newRow)                         # Insert the copy with the modified project number.
            numBlocksDeleted = numBlocksDeleted + 1

    print "Number of blocks deleted = " + str(numBlocksDeleted)
    del u_cursSDE

    # Start the for loop to cycle through all the rows
    for s_row in s_curGDB:

        shape = s_row[5]    #This variable points to the Shape token, "SHAPE@"

        match = False       # A boolean value that is changed to True if the record matches a record already in the Target SDE.

        # Setup update cursor for the Target SDE - This will cycle through the existing records in the SDE.
        u_cursSDE = arcpy.da.UpdateCursor(editSDE + os.sep + sdeName + ".DBO.Ops\\" + sdeName + ".DBO.BlockCenterline",fieldsBlock, fieldsBlock[0] + " = '" + s_row[0] + "'") 

        #If the feature has no geometry, it's PageNo is added to the noGeometryArray and reported to the user at the end of the script.
        if shape == None:
            noGeometryBlock.append(str(s_row[0]))


        #Cycle through the records in the Target SDE and compare the PageNo value with that in the GDB.
        for u_row in u_cursSDE:
            counter = 0

            if u_row[0] == s_row[0]:        # If PageNo in preBlockLinesCombo == PageNo in the SDE

                if u_row[1] == s_row[1]:    #strCDOTProjectNumber
                    pass
                else:
                    counter = counter + 1
                    u_row[1] = s_row[1]
                if u_row[2] == s_row[2]:    #strBlockLocation
                    pass
                else:
                    counter = counter + 1
                    u_row[2] = s_row[2]
                if u_row[3] == s_row[3]:    #strBlockFrom
                    pass
                else:
                    counter = counter + 1
                    u_row[3] = s_row[3]
                if u_row[4] == s_row[4]:    #strBlockTo
                    pass
                else:
                    counter = counter + 1
                    u_row[4] = s_row[4]
                if u_row[7] == s_row[7]:    #BlockNo
                    pass
                else:
                    counter = counter + 1
                    u_row[7] = s_row[7]
                if u_row[8] == s_row[8]:    #lngProjectID
                    pass
                else:
                    counter = counter + 1
                    u_row[8] = s_row[8]

                if counter > 0:
                    u_cursSDE.updateRow(u_row)
                    print "Update " + str(counter) + " objects to row."
                    print str(s_row[0]) + " was updated."
                else:
                    print str(s_row[0]) + ": All attributes match. Skipping Record."
                    pass                  #If a matching record is found, update the record

                match = True


        if match == False:                                  #If no matching record is found in the SDE, the Insert Cursor will insert the new record.
            i_cursSDE.insertRow(s_row)
            print str(s_row[0]) + " was inserted."


        del u_cursSDE       #Delete the Update Cursor before re-creating it in the next iteration of the loop.
    # ========================================================================================================================

    
    del i_cursSDE, s_curGDB           #Delete the InsertCursor pointing to the Target SDE and the Search Cursor pointing to the GDB.


    #Stop the editing session.
    edit.stopOperation()
    edit.stopEditing(True)
    del edit

    # Posting to SDE
    SDE_DEFAULT = targetSDE
    version = "PreProc"
    p = t_v[0]
    Post(SDE_DEFAULT, version, p)

    print "*************************************"
    print "BlockCenterline updating is complete."
    print "*************************************"
    arcpy.AddMessage("*************************************")
    arcpy.AddMessage("BlockCenterline updating is complete.")
    arcpy.AddMessage("*************************************")
    #-----------------------------------------------------------------------------------------------------------------------------------------------------




    #-----------------------------------------------------------------------------------------------------------------------------------------------------

    """Added Rotation to fieldsBlock List"""
    fieldsBlock.append("Rotation")
    arcpy.AddMessage(fieldsBlock)

    #Start an editing session   
    edit1 = arcpy.da.Editor(editMapbookSDE)
    edit1.startEditing(False, True)
    edit1.startOperation()

    #Create Search Cursor - Cusor is initially set to the BlockCenterline_v3 dataset.
    s_curGDB = arcpy.da.SearchCursor(preBlockLines, fieldsBlock, whereClause); print "Search cursor set... BlockCenterline. Evaluating Records..."

    #Create Insert Cursor (It is more efficient if the Insert Cursor is created outside the loop)
    i_cursSDE = arcpy.da.InsertCursor(editMapbookSDE + os.sep + mbSDEName + ".DBO.Calcs\\" + mbSDEName + ".DBO.Blocks_FinalCalcs", fieldsBlock) 

    #Create a list to hold the records that do not have any geometry.  This list will notify the user at the end of any records that have no geometry.
    noGeometryBlock = []

    # Start the for loop to cycle through all the rows
    for s_row in s_curGDB:

        shape = s_row[5]    #This variable points to the Shape token, "SHAPE@"

        match = False       # A boolean value that is changed to True if the record matches a record already in the Target SDE.

        # Setup update cursor for the Target SDE - This will cycle through the existing records in the SDE.
        u_cursSDE = arcpy.da.UpdateCursor(editMapbookSDE + os.sep + mbSDEName + ".DBO.Calcs\\" + mbSDEName + ".DBO.Blocks_FinalCalcs", fieldsBlock, fieldsBlock[0] + " = '" + s_row[0] + "'") 

        #If the feature has no geometry, it's PageNo is added to the noGeometryArray and reported to the user at the end of the script.
        if shape == None:
            noGeometryBlock.append(str(s_row[0]))

        #Cycle through the records in the Target SDE and compare the PageNo value with that in the GDB.
        for u_row in u_cursSDE:
            counter = 0

            if u_row[0] == s_row[0]:
                if u_row[1] == s_row[1]:
                    pass
                else:
                    counter = counter + 1
                    u_row[1] =  s_row[1]
                if u_row[2] == s_row[2]:
                    pass
                else:
                    counter = counter + 1
                    u_row[2] = s_row[2]
                if u_row[3] == s_row[3]:
                    pass
                else:
                    counter = counter +1
                    u_row[3] = s_row[3]
                if u_row[4] == s_row[4]:
                    pass
                else:
                    counter = counter + 1
                    u_row[4] = s_row[4]
                if u_row[7] == s_row[7]:
                    pass
                else:
                    counter = counter + 1
                    u_row[7] = s_row[7]
                if u_row[8] == s_row[8]:
                    pass
                else:
                    counter = counter + 1
                    u_row[8] == s_row[8]

                if counter > 0:
                    u_cursSDE.updateRow(u_row)                 #If a matching record is found, update the record
                    print "Update " + str(counter) + " objects to row."
                    print str(s_row[0]) + " was updated."
                else:
                    print str(s_row[0]) + ": All attributes match. Skipping Record."
                    pass

                match = True #Boolean to determine if its a new project or not

        if match == False:                                  #If no matching record is found in the SDE, the Insert Cursor will insert the new record.
            i_cursSDE.insertRow(s_row)
            print str(s_row[0]) + " was inserted."

        del u_cursSDE       #Delete the Update Cursor before re-creating it in the next iteration of the loop.

    del i_cursSDE, s_curGDB           #Delete the InsertCursor pointing to the Target SDE and the Search Cursor pointing to the GDB.

    print "*************************************"
    print "MapBook BlockCenterline updating is complete."
    print "*************************************"
    arcpy.AddMessage("*************************************")
    arcpy.AddMessage("MapBook BlockCenterline updating is complete.")
    arcpy.AddMessage("*************************************")

    #Stop the editing session.
    edit1.stopOperation()
    edit1.stopEditing(True)
    del edit1

    ## Posting to SDE
    SDE_DEFAULT = targetMapbookSDE
    version = "PreProc"
    p = t_v[1]
    Post(SDE_DEFAULT, version, p)

    #------------------------------------------------------------------------
    #Notify the user of any features that do not have geometry.
    if len(noGeometryBlock) > 0:
        print ""
        print "********************************************************** "
        print "WARNING! The following Block Centerlines have no geometry and were skipped: "
        arcpy.AddMessage("WARNING! The following Block Centerlines have no geometry and were skipped: ")
        for i in range(len(noGeometryBlock)):
            print noGeometryBlock[i]
            arcpy.AddMessage(noGeometryBlock[i])

        print "********************************************************** "

    elif len(noGeometryProject) > 0:
        print ""
        print "********************************************************** "
        print "WARNING! The following Project Centerlines have no geometry and were skipped: "
        arcpy.AddMessage("WARNING! The following Project Centerlines have no geometry and were skipped: ")
        for i in range(len(noGeometryProject)):
            print noGeometryProject[i]
            arcpy.AddMessage(noGeometryProject[i])

        print "********************************************************** "

    else:
        print ""
        print "*********************** "
        print "The script is finished. "
        print "*********************** "
        arcpy.AddMessage("The script is finished. ")

    arcpy.ClearWorkspaceCache_management()


## check if connection to SDE exists
def checkConn(f, folderName):
    con_check = os.path.isfile(folderName + '\\' + f)
    try:
        if con_check is True:
            print "Connection is made."

    except Exception as e:
        ## show error
        print "Cannot connect to SDE for the following Reason(s):"
        print e.message  ## error code
        exit()

    ## Set workspace
    SDE_DEFAULT = folderName + '\\' + f
    print SDE_DEFAULT

    try:
        versionList = arcpy.ListVersions(SDE_DEFAULT)
        print versionList
    except Exception as e:
        print"Error: " + e.message
        print "Unable to list versions."
        exit()
    return SDE_DEFAULT, versionList, f, folderName

## Exit operation
def exit():
    try:
        raise SystemExit()
    except:
        print "Cannot continue connection to SDE."


## Reconcile-Post operation
def Post(SDE_DEFAULT, version, p):
    arcpy.env.workspace = SDE_DEFAULT
    parent = p
    
    arcpy.ReconcileVersion_management(SDE_DEFAULT, version, parent, "BY_ATTRIBUTE", "FAVOR_TARGET_VERSION", "LOCK_ACQUIRED", "NO_ABORT") 
    
    arcpy.AddMessage("Post to SDE complete.")
    print "Post to SDE complete."


if __name__ == '__main__':
    main()





