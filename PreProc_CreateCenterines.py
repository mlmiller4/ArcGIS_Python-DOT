#------------------------------------------------------------------------------------------------
# Name:        createBlockandCenterline
# Purpose:     Creates Block Centerlines from Lat/Long coordinates in the DB_DATA_13 database.
#
# Author:      MMiller
#
# Created:     08/01/2013
# Copyright:   (c) MMiller 2013
# Licence:     <your licence>
#
#Code Review Draft: 9/17/2013 <SAH>
#Code Review Final:
#-------------------------------------------------------------------------------



print "Script has started!"


import arcpy, sys, os, time, datetime, math
from arcpy import env

env.overwriteOutput = True

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%m%d%Y_%H%M%S')

#------------------------------------------------------------------------------------------------------------------------------#
# Function for calculating the North Azimuth of each centerline.

def NorthAzimuth(Pline):
  if (Pline.length > 0):
    #degBearing = math.degrees(math.atan2((Pline.lastPoint.X - Pline.firstPoint.X),(Pline.lastPoint.Y - Pline.firstPoint.Y)))    #<--- This is atan2(x,y)
        #Should atan2 be X,Y or Y,X???  docs.python.org lists math.atan2(y,x)
    """Update to Bearing"""#TBU-01/31/2014
    degBearing = math.degrees(math.atan2((Pline.lastPoint.X - Pline.firstPoint.X),(Pline.lastPoint.Y - Pline.firstPoint.Y)))

    degBearing1 = 0
    if (degBearing < 0):
        degBearing1 =  degBearing+360
    else:
        degBearing1 =  degBearing
    if (degBearing1 < 90.01):
        degBearing1 += 270
    elif (degBearing1 > 90.01 and degBearing1 < 180.01 ):
        degBearing1 -= 90
    elif (degBearing1 > 180.01 and degBearing1 < 270.01 ):
        degBearing1 -= 90
    elif (degBearing1 > 270.01):
        degBearing1 -= 270
    return degBearing1
  else:
    return 0
#---------------------------------------------------------------------------------------------------------------------------------#


# Script arguments

#Input
inputMDB = arcpy.GetParameterAsText(0)

if inputMDB == "#" or not inputMDB:
    inputMDB = r"\\lex-srv02\gis\projects\IL\Chicago\CDOT_Menu_Pro\Tables\mdb\DB_DATA_14.mdb"  #Set default value if unspecified.

targetGDB = arcpy.GetParameterAsText(1)

if targetGDB == "#" or not targetGDB:
    targetGDB = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\working\Templates\Lex_CDOT_Menu_PreProcessing.gdb"  #Set default value if unspecified.

today = datetime.datetime.now()
ts = today.strftime('%m%d%Y_%H%M%S')

targetGDBpath = os.path.dirname(targetGDB)
print targetGDBpath
targetGDBpath = targetGDBpath.replace('Templates', 'PreProcessing')
targetBasename = os.path.basename(targetGDB)
print targetBasename
targetBasename = os.path.splitext(targetBasename)
print targetBasename[0]
targetNewbase = targetBasename[0] + "_" + ts + ".gdb"
print targetNewbase
newTargetGDB = os.path.join(targetGDBpath, targetNewbase)
print newTargetGDB

env.workspace = inputMDB

arcpy.Copy_management(targetGDB, newTargetGDB)
##arcpy.Copy_management(targetGDB, targetGDB[:-4] + "_" + ts + ".gdb")

targetGDB = targetGDB[:-4] + "_" + ts + ".gdb"

gdb_Workspace = newTargetGDB
##gdb_Workspace = targetGDB
print "Workspace set to: " + str(gdb_Workspace)
arcpy.AddMessage("Output Pre-Processing GDB is set to: " + str(gdb_Workspace))

gdb_Folder = os.path.dirname(env.workspace)
print "Folder is: " + str(gdb_Folder)



#Create variables for the 3 tables:
tblBlockGIS = env.workspace + os.sep + "tblBlockGIS"
tblProject = env.workspace + os.sep + "tblProject"
tblPhase = env.workspace + os.sep + "tblPhase"

#Fields that will be used in the join
joinFields = ["lngProjectID", "strCCEProjectNumber", "strCDOTProjectNumber", "lngPhaseID", "lngWardID", "lngMenuID", "memProjectComments", "strReportLocation", "strReportFrom", "strReportTo", "memWardComment", "lngBlocks", "memAldermanComment"]


#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# When a table view of tblBlockGIS is created, its lngBlockID field will become an OBJECTID field and its values will be overwritten with OID numbers.
# Because the lngBlockID values are needed for a later join, they need to be preserved by creating a lngBlockID2 field
# and copying the values from the original lngBlockID.
# This will also occur with lngProjectID in the tblProject table, and therefore an lngProjectID2 field also needs to be added.

arcpy.AddField_management(tblBlockGIS, "lngBlockID2", "LONG", 10, "", "", "", "", "")   #Create lngBlockID2 field in tblBlockGIS

BlockID_Fields = ["lngBlockID", "lngBlockID2"]

u_cursTemp = arcpy.da.UpdateCursor(tblBlockGIS, BlockID_Fields)

for rowTemp in u_cursTemp:
    rowTemp[1] = rowTemp[0]         #Set values of lngBlockID2 to be equal to lngBlockID

    u_cursTemp.updateRow(rowTemp)

del u_cursTemp, BlockID_Fields

# Do the same for tblProject and lngProjectID.
arcpy.AddField_management(tblProject, "lngProjectID2", "LONG", 10)  #Create lngProjectID2 field in tblProject

ProjectID_Fields = ["lngProjectID", "lngProjectID2"]

u_cursTemp = arcpy.da.UpdateCursor(tblProject, ProjectID_Fields)

for rowTemp in u_cursTemp:
    rowTemp[1] = rowTemp[0]     #Set values of lngProjectID2 equal to lngProjectID

    u_cursTemp.updateRow(rowTemp)

del u_cursTemp, ProjectID_Fields
#------------------------------------------------------------------------------------------------------------------------------------------------------#


#Make Table View for the tables - Table Views are IN_MEMORY tables.
tblBlockGIS_View = arcpy.MakeTableView_management(tblBlockGIS, "blockTableView","HumanVerificationStatus = 'Verified' AND ( \"Latitude_From_Snap\" IS NOT NULL AND \"Longitude_From_Snap\" IS NOT NULL AND \"Latitude_To_Snap\" IS NOT NULL AND \"Longitude_To_Snap\" IS NOT NULL)")
print "tblBlockGIS_View created..."

tblProject_View = arcpy.MakeTableView_management(tblProject, "tblProject_View", "lngPhaseID = 38")  #Select only records where lngPhaseID = 38.  This limits the table to the records marked as "Available for Survey".
print "tblProject_View created..."

tblPhase_View = arcpy.MakeTableView_management(tblPhase)
print "tblPhase_View created..."

#Create a Describe object for each table
descBlockGIS = arcpy.Describe(tblBlockGIS_View)
descProject = arcpy.Describe(tblProject_View)
descPhase = arcpy.Describe(tblPhase_View)


#Create Search Cursors
s_cursBlockGIS = arcpy.da.SearchCursor(tblBlockGIS_View, "*")
s_cursProject = arcpy.da.SearchCursor(tblProject_View, joinFields)  #Include only the fields in the joinFields list.
s_cursPhase = arcpy.da.SearchCursor(tblPhase_View, "*")


#Create an in-memory table to hold the joined tblBlockGIS and tblProject tables.
tblJoin = arcpy.management.CreateTable("in_memory", "mytblJoin", tblBlockGIS_View)
#print "Created tblJoin"


#Get a description of all fields in the tblProject table.  Get the field name, type, precision, etc. of the fields listed in the joinFields list and add create identical fields in tblJoin.
for field in descProject.fields:

    for i in joinFields:

        if field.name == i and field.name != "lngProjectID":    #Because tblBlockGIS already has an lngProjectID field, it does not need to be added again.
            arcpy.AddField_management(tblJoin, field.name, field.type, field.precision, field.scale, field.length, field.aliasName, field.isNullable, field.required, field.domain)
            #Make sure to add all of the fields' properties, or else problems copying data may result.  If field.length is not specified, string fields will have a length of 0.



print "tblJoin now has the fields from tblBlockGIS, plus the joined fields from tblProject."

descJoin = arcpy.Describe(tblJoin)

i_curs = arcpy.da.InsertCursor(tblJoin, "*") #Create an Insert Cursor for tblJoin


# tblJoin will now have the same fields as tblBlockGIS and the joinFields list from tblProject.


#-------------------------------------------------------------------------------------------------------------------------------------
# Match the records in tblBlockGIS and tblProject by the lngProjectID field and populate their attributes.
# When finished, tblJoin will have attributes for all fields in tblBlockGIS along with the joinFields list from tblProject.


count = 0       #Counter for the number of records matched between tblBlockGIS and tblProject


for row_BlockGIS in s_cursBlockGIS:     #Loop through the records in tblBlockGIS

    for row_Project in s_cursProject:       #Loop through the records in tblProject

        if row_Project[0] == row_BlockGIS[2]:   #Determine whether lngProjectID in tblBlockGIS matches the lngProjectID in tblProject

            allValues = []                      #Create a list to hold the values to be inserted into tblJoin
            allValues.extend(row_BlockGIS)      #Add the values from the current row in tblBlockGIS

            for i in range(len(row_Project)):           #Add the values from the current row in tblProject to the allValues list, but skip the lngProjectID field.
                if i > 0:
                    allValues.append(row_Project[i])


            #Insert the allValues list as a row into tblJoin.
            #print "allValues has " + str(len(allValues))
            i_curs.insertRow(allValues)
            count += 1

    s_cursProject.reset()   #Reset the tblProject Search Cursor for next iteration of the loop.


print str(count) + " records match."

del i_curs


# At this point, the tblBlockGIS and tblProject fields will be joined in tblJoin.

#---------------------------------------------------------------------------------------------
# Add and populate the 'PageNo' field.

arcpy.AddField_management(tblJoin, "PageNo", "TEXT", "", "", 50, "", "", "", "")        #Create 'PageNo' field as text with length of 50

fields = ["strCCEProjectNumber", "lngBlock", "PageNo"]

u_cursJoin = arcpy.da.UpdateCursor(tblJoin, fields)     #Create an update cursor for tblJoin

for row_Join in u_cursJoin:

    # If the record has an lngBlock number, then the PageNo is the strCCEProjectNumber combined with the lngBlock.
    # If lngBlock is NULL, then the PageNo is just the strCCEProjectNumber.

    if row_Join[1]:
        row_Join[2] = str(row_Join[0]) + "_" + str(row_Join[1])
    else:
        row_Join[2] = str(row_Join[0])

    u_cursJoin.updateRow(row_Join)

del u_cursJoin, fields


#------------------------------------------------------------------------------------------------------------------------------------------------#
# Since we have already limited tblProject_View to the records that are ready for survey, we need to add the strPhase field and populate
# it with 'Available for Survey'

#Add an strPhase field to tblJoin identical to the one in tblPhase
for field in descPhase.fields:
    if field.name == "strPhase":
        arcpy.AddField_management(tblJoin, field.name, field.type, field.precision, field.scale, field.length, field.aliasName, field.isNullable, field.required, field.domain)
        print "Added: " + field.name


#Create an Update Cursor for tblJoin with the fields lngPhaseID and strPhase
u_cursJoin = arcpy.da.UpdateCursor(tblJoin, "strPhase")

for row_Join in u_cursJoin:
    row_Join[0] = "Available for Survey"
    u_cursJoin.updateRow(row_Join)



#--------------------------------------------------------------------------------------------------------------------------------#
# Use the XYToLine_management to create a feature class from tblJoin.


sr_object = arcpy.SpatialReference("Geographic Coordinate Systems/World/WGS 1984")  #Spatial reference for the WGS 1984 coordinate system.

XY_Features = "in_memory" + os.sep + "BlocksGIS_totable_XYToLine"     #Name for the in-memory feature class to be created.

arcpy.XYToLine_management(tblJoin, XY_Features, "Longitude_From_Snap", "Latitude_From_Snap", "Longitude_To_Snap", "Latitude_To_Snap", "GEODESIC", "lngBlockID2", sr_object)

print "XY_Features successfully created."



#---------------------------------------------------------------------------------------------------------------------------------#
# Because the XYToLine_management function does not copy the attributes from its input table, the resulting XY features must
# be joined back to tblJoin so that the features will have the same attributes.

# Fields to be joined from tblJoin
fieldsToJoin = ["lngBlock", "lngProjectID", "CornerHouseAddress", "BlockOn", "BlockFrom", "BlockTo", "HumanVerificationStatus",
"strCCEProjectNumber", "strCDOTProjectNumber", "lngPhaseID", "lngWardID", "lngMenuID", "memProjectComments", "strReportLocation", "strReportFrom", "strReportTo", "memWardComment", "lngBlocks", "memAldermanComment",
"PageNo", "strPhase"]

arcpy.JoinField_management(XY_Features, "lngBlockID2", tblJoin, "lngBlockID2", fieldsToJoin)


# Create a copy of the joined feature class to be used later - This will be joined to the BlockCenterline_draft feature class.
XY_Features_Copy = "in_memory" + os.sep + "BlocksGIS_totable_XYToLine_Copy"
arcpy.CopyFeatures_management(XY_Features, XY_Features_Copy)


#------------------------------------------------------------------------------------------------------------------------------------#
# Dissolve the line features based on the lngProjectID field and then re-join the dissolved features back to tblJoin,
# based on the lngProjectID field, in order to regain the original attributes of the features.
# Also, add field 'PreProcDate' and populate with the current date and time.

XY_Features_Dissolve = "in_memory" + os.sep + "BlocksGIS_totable_XYToLine_Dissolve"
arcpy.Dissolve_management(XY_Features, XY_Features_Dissolve, "lngProjectID")


arcpy.AddField_management(XY_Features_Dissolve, "PreProcDate", "DATE", "", "", "", "", "NULLABLE", "", "")   #Add field called 'PreProcDate' for the date and time.

u_curs_XYDissolve = arcpy.da.UpdateCursor(XY_Features_Dissolve, "PreProcDate")     #Use an update cursor to populate 'PreProcDate' with date and time.

#Populate 'PreProcDate' with the current date and time.
for row_XYDissolve in u_curs_XYDissolve:
    row_XYDissolve[0] = datetime.datetime.now()
    u_curs_XYDissolve.updateRow(row_XYDissolve)

del u_curs_XYDissolve


# Fields to be joined from tblJoin
fieldsToJoin = ["lngBlock", "CornerHouseAddress", "BlockOn", "BlockFrom", "BlockTo", "HumanVerificationStatus",
"strCCEProjectNumber", "strCDOTProjectNumber", "lngPhaseID", "lngWardID", "lngMenuID", "memProjectComments", "strReportLocation", "strReportFrom", "strReportTo", "memWardComment", "lngBlocks", "memAldermanComment",
"PageNo", "lngBlockID2", "lngProjectID2", "strPhase"]

arcpy.JoinField_management(XY_Features_Dissolve, "lngProjectID", tblJoin, "lngProjectID", fieldsToJoin)


#------------------------------------------------------------------------------------------------------------------------------------#
# Format memWardComment, memAldermanComment, and memProjectComment to be no more than 255 characters in length.

fields = ["memWardComment", "memAldermanComment", "memProjectComments"]

u_curs_XYDissolve = arcpy.da.UpdateCursor(XY_Features_Dissolve, fields)

for u_row in u_curs_XYDissolve:     #Check whether the string is NULL first and keep only the first 255 characters of each existing string
    if u_row[0]:
        u_row[0] = (u_row[0])[:255]

    if u_row[1]:
        u_row[1] = (u_row[1])[:255]

    if u_row[2]:
        u_row[2] = (u_row[2])[:255]

    u_curs_XYDissolve.updateRow(u_row)

del u_curs_XYDissolve, fields


#--------------------------------------------------------------------------------------------------------------------------------------#
# Create a feature class called ProjectCenterline_draft from the Lex_CDOT_Menu_PreProcessing.gdb\containers\ProjectCenterline

template_ProjectCenterline = gdb_Workspace + "\\containers\\ProjectCenterline"  #Note: This is current set to Lex_CDOT_Menu_PreProcessing(copy).gdb
print "template_ProjectCenterline set."

descTemplate = arcpy.Describe(template_ProjectCenterline)  #Use a Describe object to access the spatial reference and set sr_object equal to it.
sr_object = descTemplate.spatialReference

ProjectCenterline_draft = arcpy.CreateFeatureclass_management(gdb_Workspace, "ProjectCenterline_draft", "POLYLINE", template_ProjectCenterline, "DISABLED", "DISABLED", sr_object, "", "", "", "")

print "ProjectCenterline_draft sucessfully created."

# Append XY_Features_Dissolve to the new ProjectCenterline_draft feature class
arcpy.Append_management(XY_Features_Dissolve, ProjectCenterline_draft, "NO_TEST")

print "XY_Features_Dissolve successfully appended to ProjectCenterline_draft."

# Copy the values for the 'PreProcDate' in the XY_Features_Dissolve to the 'CreateDate' field in ProjectCenterline_draft.
# Use Search and Update cursors, match the records on the 'lngProjectID' field.
fields_ProjectCenterline = ["lngProjectID", "CreateDate"]
fields_XY_Features_Dissolve = ["lngProjectID", "PreProcDate"]

u_curs_ProjectCenterline = arcpy.da.UpdateCursor(ProjectCenterline_draft, fields_ProjectCenterline)     #Set Update Cursor to ProjectCenterline_draft and a Search Cursor to XY_Features_Dissolve.
s_curs_XY_Features = arcpy.da.SearchCursor(XY_Features_Dissolve, fields_XY_Features_Dissolve)

for s_curs in s_curs_XY_Features:
    for u_curs in u_curs_ProjectCenterline:

        if u_curs[0] == s_curs[0]:
            u_curs[1] = s_curs[1]
            u_curs_ProjectCenterline.updateRow(u_curs)

    u_curs_ProjectCenterline.reset()

print "CreateDate field in ProjectCenterline_draft sucessfully updated."

del u_curs_ProjectCenterline, s_curs_XY_Features


#-------------------------------------------------------------------------------------------------------------------------#
# Create a feature class for BlockCenterline_draft from the Lex_CDOT_Menu_PreProcessing.gdb\containers\BlockCenterline

template_BlockCenterline = gdb_Workspace + "\\containers\\BlockCenterline"  #Note: This is current set to Lex_CDOT_Menu_PreProcessing(copy).gdb
print "template_BlockCenterline set."

descXYFeatures = arcpy.Describe(XY_Features_Copy)

for field in descXYFeatures.fields:
    if field.name == "lngBlockID2":
           tempField = field

arcpy.AddField_management(template_BlockCenterline, tempField.name, tempField.type, tempField.precision, tempField.scale, tempField.length, "", "", "", "")

BlockCenterline_draft = arcpy.CreateFeatureclass_management(gdb_Workspace, "BlockCenterline_draft", "POLYLINE", template_BlockCenterline, "DISABLED", "DISABLED", sr_object, "", "", "", "")

print "BlockCenterline_draft sucessfully created."

# Append XY_Features_Copy to the new BlockCenterline_draft feature class.
arcpy.Append_management(XY_Features_Copy, BlockCenterline_draft, "NO_TEST")
print "XY_Features_Copy successfully appended to BlockCenterline_draft."

# Copy attribute data from XY_Features_Copy into BlockCenterline_draft
fields_BlockCenterline = ["lngBlockID2", "BlockNo", "strBlockLocation", "strBlockFrom", "strBlockTo", "strBlockCornerHouse", "lngBlockID", "CreateDate", "strCDOTProjectNumber"]    #Fields to be used in Search and Update Cursors
fields_XY_Features_Copy = ["lngBlockID2", "lngBlock", "BlockOn", "BlockFrom", "BlockTo", "CornerHouseAddress", "strCDOTProjectNumber"]

u_curs_BlockCenterline = arcpy.da.UpdateCursor(BlockCenterline_draft, fields_BlockCenterline)
s_curs_XY_Features = arcpy.da.SearchCursor(XY_Features_Copy, fields_XY_Features_Copy)

for s_curs in s_curs_XY_Features:
    for u_curs in u_curs_BlockCenterline:

        if u_curs[0] == s_curs[0]:      # If lngBlockID2 in BlockCenterline_draft = lngBlockID2 in XY_Features_Copy, match all corresponding fields
            u_curs[1] = s_curs[1]       # BlockNo = lngBlock
            u_curs[2] = s_curs[2]       # strBlockLocation = BlockOn
            u_curs[3] = s_curs[3]       # strBlockFrom = BlockFrom
            u_curs[4] = s_curs[4]       # strBlockTo = BlockTo
            u_curs[5] = s_curs[5]       # strBlockConerHouse = CornerHouseAddress
            u_curs[6] = s_curs[0]       # Set lngBlockID = lngBlockID2
            u_curs[8] = s_curs[6]       # strCDOTProjectNumber
            u_curs[7] = datetime.datetime.now( )        # Set 'CreateDate' to the current date & time.
            u_curs_BlockCenterline.updateRow(u_curs)

    u_curs_BlockCenterline.reset()

print "BlockCenterline_draft fields successfully updated."

del s_curs_XY_Features, u_curs_BlockCenterline


#----------------------------------------------------------------------------------------------------#
# Populate the 'Rotation' field in BlockCenterline_draft with the azimuth
#----------------------------------------------------------------------------------------------------#

fields = ["Rotation", "SHAPE@", "strCCEProjectNumber"]

u_curs_BlockCenterline = arcpy.da.UpdateCursor(BlockCenterline_draft, fields, "SHAPE_Length > 0")  # <---- Create query for SHAPE_Length > 0

for u_curs in u_curs_BlockCenterline:       #Iterate through each polyline feature in BlockCenterline.
    print u_curs[2]
    feat = u_curs[1]

    point = arcpy.Point()
    array = arcpy.Array()

    for part in feat:           #Create an array of points in each polyline feature.
        for pnt in part:
            point.X = pnt.X
            point.Y = pnt.Y
            array.add(point)

    pline = arcpy.Polyline(array)       #Create a polyline object from the array of points.
    print "pline created."

    u_curs[0] = NorthAzimuth(pline)     #Pass the polyline object to the NorthAzimuth function.

    """Added to account for Alley (AA) rotation set to 0"""#TBU-01/31/2014
    if "-AA-" in u_curs[2]:
        u_curs[0] = int("0")
    if "-RA-" in u_curs[2]:
        u_curs[0] = int("0")

    print "North Azimuth = " + str(u_curs[0])

    u_curs_BlockCenterline.updateRow(u_curs)

    array.removeAll()       #Reset to an empty array for next iteration of the loop.


print "Finished calculating North Azimuth."

print "Creating Combo feature classes...."

out_data = gdb_Workspace + "\BlockCenterlineCombo_draft"
data_type = ""

BlockCenterline_draftCombo = arcpy.Copy_management(BlockCenterline_draft, out_data, data_type)

fields = ["strCCEProjectNumber", "PageNo"]

u_curs_BlockCenterlineCombo = arcpy.da.UpdateCursor(BlockCenterline_draftCombo, fields, "SHAPE_Length > 0")  # <---- Create query for SHAPE_Length > 0

for u_curs in u_curs_BlockCenterlineCombo:       #Iterate through each polyline feature in BlockCenterline.

    cce = u_curs[0]
    pageNo = u_curs[1]

    if "-AS-" in cce:
        u_curs[0] = cce.replace("-AS-", "-ASlRS-")
        u_curs[1] = pageNo.replace("-AS-", "-ASlRS-")
        u_curs_BlockCenterlineCombo.updateRow(u_curs)

    if "-AA-" in cce:
        u_curs[0] = cce.replace("-AA-", "-AAlRA-")
        u_curs[1] = pageNo.replace("-AA-", "-AAlRA-")
        u_curs_BlockCenterlineCombo.updateRow(u_curs)

    if "-RS-" in cce:
        u_curs_BlockCenterlineCombo.deleteRow()

    if "-RA-" in cce:
        u_curs_BlockCenterlineCombo.deleteRow()


del u_curs_BlockCenterlineCombo

print "Finished creating Block Centerline Combo."

out_data = gdb_Workspace + "\ProjectCenterlineCombo_draft"
data_type = ""

ProjectCenterline_draftCombo = arcpy.Copy_management(ProjectCenterline_draft, out_data, data_type)

fields = ["strCCEProjectNumber"]

u_curs_ProjectCenterlineCombo = arcpy.da.UpdateCursor(ProjectCenterline_draftCombo, fields, "SHAPE_Length > 0")  # <---- Create query for SHAPE_Length > 0

for u_curs in u_curs_ProjectCenterlineCombo:       #Iterate through each polyline feature in BlockCenterline.

    cce = u_curs[0]

    if "-AS-" in cce:
        u_curs[0] = cce.replace("-AS-", "-ASlRS-")
        u_curs_ProjectCenterlineCombo.updateRow(u_curs)

    if "-AA-" in cce:
        u_curs[0] = cce.replace("-AA-", "-AAlRA-")
        u_curs_ProjectCenterlineCombo.updateRow(u_curs)

    if "-RS-" in cce:
        u_curs_ProjectCenterlineCombo.deleteRow()

    if "-RA-" in cce:
        u_curs_ProjectCenterlineCombo.deleteRow()


del u_curs_ProjectCenterlineCombo

print "Finished creating Project Centerline Combo."



# TEST OUTPUT - Creates test tables and features classes.
#----------------------------------------------------------------------------------------------------#
#Test Feature - Output a feature class to ensure that it is being created correctly.
##outputFeatures = gdb_Workspace + os.sep + "BlocksGIS_totable_XYToLine"
##myTestFeatures = arcpy.CreateFeatureclass_management(gdb_Workspace, "XY_Features_Copy", "POLYLINE")
##arcpy.CopyFeatures_management(XY_Features_Copy, myTestFeatures)
##
##print "Test Features successfully created."


#Test Table - Output a test table to ensure that everything is joining correctly.
##myTestTable = arcpy.management.CreateTable(r"\\lex-srv02\gis\projects\IL\Chicago\v4\Tables\TEST.mdb", "testTable11", tblSurvey_View)
##
##arcpy.CopyRows_management(tblSurvey_View, myTestTable)
##
##print "testTable created."

del s_cursBlockGIS, s_cursPhase, s_cursProject, tblJoin, u_curs_BlockCenterline
arcpy.Delete_management("in_memory")
arcpy.AddMessage("Output Pre-Processing GDB is complete.")

