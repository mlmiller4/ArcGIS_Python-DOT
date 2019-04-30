import arcpy, sys, os, datetime
from arcpy import env

""" Identical Function """
# This sets up Search Cursors to loop through both the feature class to be updated and the SDE Final Display Feature Class#
# Creates two lists for Global ID's on both search cursors. These are then compared to track whether the Global ID needs  #
# Needs to be placed into an update list for later or an insert list.                                                     #
def identical(SDE_FC_test, target_Display, sql, GID_bool):
    
	# Setup search cursors to create 2 lists for global ID values
    # Establish empty lists
    sql = "\"strCCEProjectNumber\"" + " = '" + cceNo + "'"
    fields = ["GlobalID","PageNo", "SDEID"]
    GID_List1 = []#; print GID_List1
    GID_List2 = []#; print GID_List2
    u_List = []#; print u_List
    i_List = []#; print i_List
    u_bool = False
    i_bool = False
    SDE_Value = "GlobalID"
    if GID_bool == True:
        SDE_Value = "SDEID"

    # Start the for loop to cycle through all the rows and populate Global ID lists to compare
    s_GID_List1 = arcpy.SearchCursor(SDE_FC_test,"","","",""); print "Search cursor set... for Global ID 1"
    s_row1 = s_GID_List1.next()
	
    while s_row1:
        r = s_row1.getValue(SDE_Value)
        GID_List1.append(r)
        s_row1 = s_GID_List1.next()
    print "This is  Global ID list for Base Data... "; print GID_List1
    del s_GID_List1

    # Second Search Loop
    s_GID_List2 = arcpy.SearchCursor(target_Display, sql,"","",""); print "Search cursor set... for Global ID 2"
    s_row2 = s_GID_List2.next()
	
    while s_row2:
        s = s_row2.getValue("SDEID")
        GID_List2.append(s)
        s_row2 = s_GID_List2.next()

    print "This is  Global ID list for Target... "; print GID_List2
    del s_GID_List2

    # Start loop to compare the Global ID lists and append to appropriate list for either update or insert
    ln = len(GID_List2);  print ln
    for x in GID_List1:
        if x in GID_List2:
            u_List.append(x)
            u_bool = True
        else:
            i_List.append(x)
            i_bool = True


    print "This is the Insert List... "; print i_List
    print "This is the Update List... "; print u_List


    mainFunction(SDE_FC_test, target_Display, u_bool, i_bool, u_List, i_List, sql, GID_bool)

""" Function for both insert and update cursors """
# This function will check which boolean value is True i.e. the update or insert method.      #
# If insert is true then an insert cursor is looped and records are inserted to Final Display #
# If update is true then an update cursor is looped and records are updated to Final Display  #
def mainFunction(SDE_FC_test, target_Display, u_bool,i_bool, u_List, i_List, sql, GID_bool):

    SDE_Value = "GlobalID"
    if GID_bool == True:
        SDE_Value = "SDEID"
    else:
        pass

    desc1 = arcpy.Describe(SDE_FC_test)

    fieldlist1 = []
    for field1 in desc1.fields:
        fieldlist1.append(field1.name)

    desc2 = arcpy.Describe(target_Display)

    fieldlist2 = []
    for field2 in desc2.fields:
        fieldlist2.append(field2.name)

    s_GID = arcpy.SearchCursor(SDE_FC_test, sql, "", "", ""); print "Search cursor set... for Insert row"
    if i_bool == True:
        print "Insert True..."

        #Create Insert Cursor (It is more efficient if the Insert Cursor is created outside the loop)
        i_cursSDE = arcpy.InsertCursor(target_Display)

        for s_row in s_GID:
              x = s_row.getValue(SDE_Value); print x
              z1 = s_row.getValue("MeasureType")
              z2 = s_row.getValue("MeasureLength")
              if "MeasureWidth" in fieldlist1:
                   z2a = s_row.getValue("MeasureWidth")
              z3 = s_row.getValue("SurveyBy")
              z4 = s_row.getValue("SurveyByDate")
              z5 = s_row.getValue("BlockNo")
              z6 = s_row.getValue("PageNo")
              z7 = s_row.getValue("OmitYN")
              z8 = s_row.getValue("SHAPE")
              z9 = s_row.getValue(SDE_Value)
              z10 = s_row.getValue("strCCEProjectNumber")
              z11 = s_row.getValue("lngProjectID")
              z12 = s_row.getValue("SurveyNote")
              z13 = userInit
              today = datetime.datetime.now()
              z14 = today.strftime("%y/%m/%d")

              if x in i_List:
                    row = i_cursSDE.newRow()
                    row.MeasureType = z1
                    row.MeasureLengthFt = z2
                    if "MeasureWidthFt" in fieldlist2:
                        row.MeasureWidthFt = z2a
                    row.SURVEYBY = z3
                    row.BlockNo = z5
                    row.SurveyByDate = z4
                    row.PageNo = z6
                    row.OmitYN = z7
                    row.SHAPE = z8
                    row.SDEID = z9
                    row.strCCEProjectNumber = z10
                    row.lngProjectID = z11
                    row.SurveyNote = z12
                    row.CalcBy = z13
                    row.CalcByDate = z14

                    i_cursSDE.insertRow(row); print "Row Inserted..."
                    del row
        del i_cursSDE, x
    del s_GID, i_List          

    arcpy.AddMessage("Display Geometries have been added to the Final Display Feature Class")


    s_GID = arcpy.SearchCursor(SDE_FC_test, sql, "", "", ""); print "Search cursor set... for Insert row"
	
    if u_bool == True:
        print "Update True..."
        # Create Search cursor that will use update cursor
        # Setup update cursor for the Target SDE - This will cycle through the existing records in the SDE.


        for s_row in s_GID:
            # Get Values
            x = s_row.getValue(SDE_Value); print x
            if x in u_List:
                z1 = s_row.getValue("MeasureType")
                z2 = s_row.getValue("MeasureLength")
                if "MeasureWidth" in fieldlist1:
                    z2a = s_row.getValue("MeasureWidth")
                z3 = s_row.getValue("SurveyBy")
                z4 = s_row.getValue("SurveyByDate")
                z5 = s_row.getValue("BlockNo")
                z6 = s_row.getValue("PageNo")
                z7 = s_row.getValue("OmitYN")
                z8 = s_row.getValue("SHAPE")
                z9 = s_row.getValue(SDE_Value)
                z10 = s_row.getValue("strCCEProjectNumber")
                z11 = s_row.getValue("lngProjectID")
                z12 = s_row.getValue("SurveyNote")
                z13 = userInit
                today = datetime.datetime.now()
                z14 = today.strftime("%y/%m/%d")

                # Compare value from Feature Class to value list u_list
                u_cursSDE = arcpy.UpdateCursor(target_Display,"\"SDEID\"" + " = '" + x + "'","","","")
                for row in u_cursSDE:
                    if row.getValue("SDEID") == x:

                        # Set Values
                        row.setValue("MeasureType",z1)
                        row.setValue("MeasureLengthFt" ,z2)
                        if "MeasureWidthFt" in fieldlist2:
                            row.setValue("MeasureWidthFt", z2a)
                        row.setValue("SURVEYBY" ,z3)
                        row.setValue("BlockNo" ,z5)
                        row.setValue("SurveyByDate" ,z4)
                        row.setValue("PageNo" ,z6)
                        row.setValue("OmitYN" ,z7)                        
                        row.setValue("SDEID" ,z9)
                        row.setValue("strCCEProjectNumber", z10)
                        row.setValue("lngProjectID", z11)
                        row.setValue("SurveyNote", z12)
                        row.setValue("CalcBy", z13)
                        row.setValue("CalcByDate", z14)
                        # Update row
                        u_cursSDE.updateRow(row)
                        print x + " was updated in SDE..."
                        del row
                del u_cursSDE
        del s_GID, x, u_List  
        
    arcpy.AddMessage("Display Geometries have been updated to the Final Display Feature Class")


def GlobalID_Function(fc, fcMem, GID_bool, sql_N):
    s_GID = arcpy.SearchCursor(fc, sql_N, "", "", ""); print "Search cursor set..."
    print "Insert True..."

    desc = arcpy.Describe(fc)

    fieldlist = []
    for field in desc.fields:
        fieldlist.append(field.name)

    #Create Insert Cursor (It is more efficient if the Insert Cursor is created outside the loop)
    i_cursSDE = arcpy.InsertCursor(fcMem)

    for s_row in s_GID:
        z0 = ""
        if "MeasureType" in fieldlist:
            z0 = s_row.getValue("MeasureType")

        x = s_row.getValue("GlobalID"); print x
        z1 = s_row.getValue("MeasureLength")
        z2 = s_row.getValue("MeasureWidth")
        z3 = s_row.getValue("SurveyBy")
        z4 = s_row.getValue("SurveyByDate")
        z5 = s_row.getValue("BlockNo")
        z6 = s_row.getValue("PageNo")
        z7 = s_row.getValue("OmitYN")
        z8 = s_row.getValue("SHAPE")
        z9 = s_row.getValue("GlobalID")
        z10 = s_row.getValue("strCCEProjectNumber")
        z11 = s_row.getValue("lngProjectID")
        z12 = s_row.getValue("SurveyNote")

        if GID_bool == True:
            row = i_cursSDE.newRow()
            row.MeasureType = z0
            row.MeasureLength = z1
            row.MeasureWidth = z2
            row.SURVEYBY = z3
            row.SurveyByDate = z4
            row.BlockNo = z5
            row.PageNo = z6
            row.OmitYN = z7
            row.SHAPE = z8
            row.SDEID = z9
            row.strCCEProjectNumber = z10
            row.lngProjectID = z11
            row.SurveyNote = z12

            i_cursSDE.insertRow(row); print "Row Inserted into Scratch..."

    del s_GID, i_cursSDE

""" Beginning of Script """

env.overwriteOutput = True

# Establish Project Number from user and create SQL Clause
cceNo = arcpy.GetParameterAsText(0)
if cceNo == "#" or not cceNo:
    cceNo = "20-AS-801"
print cceNo

# Establish Multivalue string from user Input
multiValue = arcpy.GetParameterAsText(1)
if multiValue == "#" or not multiValue:
    multiValue = "Street"
print multiValue

"""Make this a param"""
userInit = arcpy.GetParameterAsText(2)
if userInit == "#" or not userInit:
    userInit = "TEST"
scratch_path = arcpy.GetParameterAsText(3)
if scratch_path == "#" or not scratch_path:
    scratch_path = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\working\Templates\Lex_CDOT_Menu_v4_Display.gdb"

today = datetime.datetime.now()
ts = today.strftime('%y%m%d_%H%M%S')

scratch_pathDIR = os.path.dirname(scratch_path)
scratch_pathNEW = scratch_pathDIR.replace('Templates', 'scratch')

scratch_copy = arcpy.Copy_management(scratch_path, scratch_pathNEW + "\\" + cceNo + "_" + userInit + "_" + ts + ".gdb")
scratch = str(scratch_copy)

# Connect to data SDE workspace *Test location
SDE_Base = arcpy.GetParameterAsText(4)
if SDE_Base == "#" or not SDE_Base:
    SDE_Base = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\Lex_CDOT_Survey.sde\Lex_CDOT_Menu.DBO.Ops"

# Connect to Target Final Display workspace *Test location
target = arcpy.GetParameterAsText(5)
if target == "#" or not target:
    target = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\Lex_CDOT_MapOutput.sde\Lex_CDOT_MapOutput.DBO.Display"

if "-AS-" in cceNo:
    cceNo = cceNo.replace("-AS-", "-ASlRS-")
if "-AA-" in cceNo:
    cceNo = cceNo.replace("-AA-", "-AAlRA-")
if "-RS-" in cceNo:
    cceNo = cceNo.replace("-RS-", "-ASlRS-")
if "-RA-" in cceNo:
    cceNo = cceNo.replace("-RA-", "-AAlRA-")


arcpy.AddMessage("Assigning parameters for project " + cceNo)
sql = "\"strCCEProjectNumber\"" + " = '" + cceNo + "'"

descSDE = arcpy.Describe(SDE_Base)
sdeName = descSDE.baseName[:-3]
print sdeName

sdePath = os.path.dirname(os.path.dirname(target))

descTarget = arcpy.Describe(target)
targetName = descTarget.name[:-7]
print targetName

""" Input Values gathered from windows form """
# mxd_Path = # Value from Windows Form Input
# cceNo = # Add Value from Windows Form Input for CCE
# block_Value = # Add Value from Windows Form Input for Block
# # Or both CCE and BLOCK can be PageNo # Look into
# output_Path = # Add Path to output folder
# global output_Path

""" Append to List for Function """
##multiValue = "CurbSidewalkStreet"
display_List = []
sub_curb = False
sub_sidewalk = False
sub_street = False
sub_other = False

if 'Curb' in multiValue:
    sub_curb = True

if 'Sidewalk' in multiValue:
    sub_sidewalk = True

if 'Street' in multiValue:
    sub_street = True

if sub_curb == True:
    value = 'Curb'
    display_List.append(value)
    del value
	
if sub_sidewalk == True:
    value = 'Sidewalk'
    display_List.append(value)
    del value
	
if sub_street == True:
    value = 'Street'
    display_List.append(value)
    del value

print display_List

def main():
    """ Create Selection """

    while 'Curb' in display_List:
        env.overwriteOutput = True
        arcpy.AddMessage("Processing Curb data")
        GID_bool = False
        display_List.remove("Curb")
        SDE_FC = SDE_Base + '\\' + sdeName + "CurbGutter"
        SDE_memory = r"\in_memory"
        SDE_FC_test = arcpy.MakeFeatureLayer_management(SDE_FC, SDE_memory , sql)
    
        print "Created Feature Layer..."
        print "Now loading identical function..."

        # Establish target_Display variable to hit the Final Displays for curbs (Polyline)
        target_Display = target + '\\' + targetName + 'CurbMeasure_DisplayFinal'

        identical(SDE_FC_test, target_Display, sql, GID_bool)
        print display_List
        print "Return..."


    while 'Sidewalk' in display_List:
    
        arcpy.AddMessage("Processing Sidewalk data")
        display_List.remove("Sidewalk")
		
        # Create list for feature class buffer analysis and Create Merge Feature Class
        fc_BuffList = []
        """Update to allow Omit = Yes - 2/3/14"""
        sql_N = "\"strCCEProjectNumber\" = '" + cceNo + "'"    
        sql_Y = "\"strCCEProjectNumber\" = '" + cceNo + "' AND \"OmitYN\" = 'Yes'"   

    
		# Establish a list of Polyline Feature Classes for Buffer
        env.workspace = SDE_Base
        fc_List = arcpy.ListFeatureClasses("*", "POLYLINE")
        print fc_List

        for fc in fc_List:
            print fc
            if fc == sdeName +'Sidewalk':
                GID_bool = True
                fcTemp = scratch + '\\' + 'Sidewalk'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "sidewalkTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                fc_BuffList.append(fcMem)
    
            if fc == sdeName + 'SidewalkOmit':
                GID_bool = True
                fcTemp = scratch + '\\' + 'SidewalkOmit'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "sidewalkOmitTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "SidewalkOmit")
                    cursor.updateRow(row); #print "SidewalkOmit row updated..."
                del cursor

                fc_BuffList.append(fcMem)

            if fc == sdeName + 'SidewalkRamp':
                GID_bool = True
                fcTemp = scratch + '\\' + 'SidewalkRamp'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "sidewalkRampTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                fc_BuffList.append(fcMem)

            if fc == sdeName + 'SidewalkRampOmit':
                GID_bool = True
                fcTemp = scratch + '\\' + 'SidewalkRampOmit'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "sidewalkRampOmitTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "SidewalkRampOmit")
                    cursor.updateRow(row); #print "SidewalkRampOmit row updated..."
                del cursor

                fc_BuffList.append(fcMem)

            if fc == sdeName + 'SidewalkRampRemove':
                GID_bool = True
                fcTemp = scratch + '\\' + 'SidewalkRampRemove'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "sidewalkRampRemoveTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "SidewalkRampRemove")
                    cursor.updateRow(row); #print "SidewalkRampRemove row updated..."
                del cursor

                fc_BuffList.append(fcMem)

            if fc == sdeName + 'AlleyDriveway':
                GID_bool = True
                fcTemp = scratch + '\\' + 'AlleyDriveway'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "alleyDrivewayTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                fc_BuffList.append(fcMem)

            if fc == sdeName + 'AlleyPavement':
                GID_bool = True
                fcTemp = scratch + '\\' + 'AlleyPavement'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "alleyPavementTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                fc_BuffList.append(fcMem)

            if fc == sdeName + 'ConcreteBusPad':
                GID_bool = True
                fcTemp = scratch + '\\' + 'ConcreteBusPad'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "concreteBusPadTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "ConcreteBusPad")
                    cursor.updateRow(row); #print "ConcreteBusPad row updated..."
                del cursor

                fc_BuffList.append(fcMem)

            if fc == sdeName + 'ConcretePavement':
                GID_bool = True
                fcTemp = scratch + '\\' + 'ConcretePavement'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "concretePavementTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "ConcretePavement")
                    cursor.updateRow(row); #print "ConcretePavement row updated..."
                del cursor

                fc_BuffList.append(fcMem)

            if fc == sdeName + 'DrivewayRemove':
                GID_bool = True
                fcTemp = scratch + '\\' + 'DrivewayRemove'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "drivewayRemoveTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "DrivewayRemove")
                    cursor.updateRow(row); #print "DrivewayRemove row updated..."
                del cursor

                fc_BuffList.append(fcMem)

        print fc_BuffList

        # Merge tool is run on fc_BuffList to create one Feature Class to apply a buff distance field using an update cursor.
        # Buffer tool is then run to create polygon feature class
        FC_merge = arcpy.Merge_management(fc_BuffList, scratch + '\\' + "MERGE_TEST")
        print "Features have been merged..."

        arcpy.AddField_management(FC_merge, "buffdistance", "LONG", "", "", 9, "BuffDistance", "NULLABLE")
        print "Buffer Distance field has been added..."
        cursor = arcpy.UpdateCursor(FC_merge)
        for row in cursor:
            z = row.getValue("MeasureWidth")
            w = z / 2
            row.setValue("buffdistance", w); print "Buffer of '" + str(w) + "' has been updated to row..."
            cursor.updateRow(row)
        del cursor

        # Buffer Analysis
        SDE_FC_test = arcpy.Buffer_analysis(FC_merge, scratch + '\\' + "BUFF_TEST","buffdistance", "FULL", "FLAT", "NONE")

        # Establish target_Display variable to hit the Final Displays for sidewalks (Polygon)
        target_Display = target + '\\' + targetName + 'SidewalkDriveway_DisplayFinal'

        # Run Functions
        identical(SDE_FC_test, target_Display, sql, GID_bool)
        del fc_List

        print display_List
        print "Return..."
    
    while 'Street' in display_List:
    
        arcpy.AddMessage("Processing Street data")
        GID_bool = False
        display_List.remove("Street")
        streetList = []

        """Update to allow Omit = Yes - 2/3/14"""
        sql_N = "\"strCCEProjectNumber\" = '" + cceNo + "'"

        env.workspace = SDE_Base
        fc_List = arcpy.ListFeatureClasses("*", "POLYLINE")
        print fc_List
        for fc in fc_List:
            print fc
            if fc == sdeName + 'StreetPavement':
                GID_bool = True
                fcTemp = scratch + '\\' + 'StreetPavement'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "streetPavementTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "StreetPavement")
                    cursor.updateRow(row);
                del cursor

                streetList.append(fcMem)

            if fc == sdeName + 'AdditionalPavement':
                GID_bool = True
                fcTemp = scratch + '\\' + 'AdditionalPavement'
                fcMem = arcpy.CopyFeatures_management(fcTemp, scratch + '\\' + "additionalPavementTEST")
                GlobalID_Function(fc, fcMem, GID_bool, sql_N)
                arcpy.AddField_management(fcMem, "MeasureType", "TEXT", "", "", 50, "Measure Type", "NULLABLE")
                cursor = arcpy.UpdateCursor(fcMem,"","", "MeasureType")
                for row in cursor:
                    row.setValue("MeasureType", "AdditionalPavement")
                    cursor.updateRow(row); #print "AdditionalPavement row updated..."
                del cursor

                streetList.append(fcMem)

        print "Created Merged Feature Class..."
        SDE_FC_test = arcpy.Merge_management(streetList, scratch + '\\' + "MERGE_TEST")
        print "Features have been merged..."
        print "Now loading identical function..."

        # Establish target_Display variable to hit the Final Displays for Street
        target_Display = target + '\\' + targetName + 'StreetMeasurements_DisplayFinal'

        identical(SDE_FC_test, target_Display, sql, GID_bool)

        print display_List
        print "Return..."
    print "...Completed"



if __name__ == '__main__':
    main()
