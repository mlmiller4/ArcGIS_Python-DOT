#-------------------------------------------------------------------------------
# Name:        streetCalcs.py
# Purpose:
#
# Author:      tulery
#
# Created:     27/06/2013
# Copyright:   (c) HDR inc. 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, sys, os, math, datetime, textwrap
from arcpy import env

env.overwriteOutput = True
"""--------------------Notes----------------------------#
# Establish the workspace Lex_CDOT_Menu_v4_Testing_newSchema.sde
# Target workspace Lex_CDOT_Menu_v4_Calcs.gdb
# Work with Dataset \Ops
# Feature Class \StreetPavement

# Find Field for Measure Length
# If new schema has no width field - need to use intersect tool to find width (intersect layer with layer copy) output to new layer call it width

# Establish Scratch Database that will include all calcs in working folder
# that also contains user information plus timestamp

# May need to set a count with search cursor
# KEEP IN MIND THAT MAY NOT NEED TO MAKE COPIES IF USING DICTIONARIES#
#--------------------Notes----------------------------"""

#Parameters
cceNo = arcpy.GetParameterAsText(0) # Establish Project Number from user?
if cceNo == '#' or not cceNo:
    cceNo = "11-AS-810" # provide a default value if unspecified
userInit = arcpy.GetParameterAsText(1)
if userInit == '#' or not userInit:
    userInit = "TEST" # provide a default value if unspecified
reviewedBy = arcpy.GetParameterAsText(2)
if reviewedBy == '#' or not reviewedBy:
    reviewedBy = "Kristen Hahn" # provide a default value if unspecified
reviewByDate = arcpy.GetParameterAsText(3)
if reviewByDate == '#' or not reviewByDate:
    reviewByDate = "2/21/14" # provide a default value if unspecified
scratch_folder = arcpy.GetParameterAsText(4)
if scratch_folder == '#' or not scratch_folder:
    scratch_folder = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\working\Templates" # provide a default value if unspecified
SDE = arcpy.GetParameterAsText(5)
if SDE == '#' or not SDE:
    SDE = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\Lex_CDOT_Survey.sde\Lex_CDOT_Menu.DBO.Ops" # provide a default value if unspecified
target = arcpy.GetParameterAsText(6)
if target == '#' or not target:
    target = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\Lex_CDOT_MapOutput.sde\Lex_CDOT_MapOutput.DBO.Calcs\Lex_CDOT_MapOutput.DBO.Blocks_FinalCalcs" # provide a default value if unspecified
arcpy.AddMessage("Assigning parameters for project " + cceNo)

projectType = cceNo.split('-')[1]

#Find corresponding combo number
if "-AS-" in cceNo:
    cceNo = cceNo.replace("-AS-", "-ASlRS-")
if "-AA-" in cceNo:
    cceNo = cceNo.replace("-AA-", "-AAlRA-")

scratch_folder = scratch_folder.replace('Templates', 'scratch')

today = datetime.datetime.now()
ts = today.strftime('%y%m%d_%H%M%S')
#Create Scratch GDB
scratchGDB = "CC_" + cceNo + "_" + userInit + "_" + ts + ".gdb"
arcpy.CreateFileGDB_management(scratch_folder, scratchGDB)
scratch = scratch_folder + "\\" + scratchGDB

descSDE = arcpy.Describe(SDE)
sdeName = descSDE.baseName[:-3]
print sdeName

sdePath = os.path.dirname(os.path.dirname(target))

descTarget = arcpy.Describe(target)
targetName = descTarget.name[:-17]
print targetName

where = "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')"
sql = "\"strCCEProjectNumber\"" + " = '" + cceNo + "'"
print where

"""Need to add/fix Block and Project Centerline tables as well.---SAH"""
# Establish Variable for SDE Street Calcs *If the direct connection to Feature class will be different
streetPave = SDE + "\\" + sdeName + "StreetPavement"
AddPave = SDE + "\\" + sdeName + "AdditionalPavement"
CornerR = SDE + "\\" + sdeName + "CornerReturns"
AlleyPave = SDE + "\\" + sdeName + "AlleyPavement"
PaveMarks = SDE + "\\" + sdeName + "PavementMarking"
SpeedHump = SDE + "\\" + sdeName + "SpeedHump"
BikeRack = SDE + "\\" + sdeName + "BikeRack"
blockCL = SDE + "\\" + sdeName + "BlockCenterline"
project_Center = SDE + "\\" + sdeName + "ProjectCenterline"
#tblMenu
tblMenu = sdePath + "\\" + targetName + "tblMenu"

FinalCalcs = target

# Create Table View for Selections # Create Copy rows from queried table views
print "Creating Table Views and Copies..."
streetView = arcpy.MakeTableView_management(streetPave, "streetView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
streetCopy = arcpy.CopyRows_management(streetView, scratch + "\\" + "streetCopy")

addView = arcpy.MakeTableView_management(AddPave, "addView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
addCopy = arcpy.CopyRows_management(addView, scratch + "\\" + "addpaveCopy")

cornerView = arcpy.MakeTableView_management(CornerR, "cornerView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
cornerRCopy = arcpy.CopyRows_management(cornerView, scratch + "\\" + "cornerRCopy")

alleyView = arcpy.MakeTableView_management(AlleyPave, "alleyView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
alleypaveCopy = arcpy.CopyRows_management(alleyView, scratch + "\\" + "alleypaveCopy")

paveMarksView = arcpy.MakeTableView_management(PaveMarks, "paveMarksView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
paveMarksCopy = arcpy.CopyRows_management(paveMarksView, scratch + "\\" + "paveMarksCopy")

speedHumpView = arcpy.MakeTableView_management(SpeedHump, "speedHumpView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
speedHumpCopy = arcpy.CopyRows_management(speedHumpView, scratch + "\\" + "speedHumpCopy")

bikeRackView = arcpy.MakeTableView_management(BikeRack, "bikeRackView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
bikeRackCopy = arcpy.CopyRows_management(bikeRackView, scratch + "\\" + "bikeRackCopy")

blockView = arcpy.MakeTableView_management(blockCL, "blockView", "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
blockCopy = arcpy.CopyRows_management(blockView, scratch + "\\" + "blockCopy")

projectView = arcpy.MakeTableView_management(project_Center, "projectView", "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
projectCopy = arcpy.CopyRows_management(projectView, scratch + "\\" + "projectCopy")

print "..."

#AutoComments Dictionary Population Function
def updateAutoCommentsDict(pref, fieldName, includeFieldYN):

    if includeFieldYN:
        fieldValue = row.getValue(fieldName)
        if fieldValue == None:
            fieldValue = ""

        if len(AutoComments_Dict[pageNo]) == 0:
            AutoComments_Dict.update({pageNo : pref +": " + fieldValue})
        else:
            AutoComments_Dict.update({pageNo : AutoComments_Dict[pageNo] + "; " + pref + ": " + fieldValue})
    else:
        if len(AutoComments_Dict[pageNo]) == 0:
            AutoComments_Dict.update({pageNo : pref})
        else:
            AutoComments_Dict.update({pageNo : AutoComments_Dict[pageNo] + "; " + pref})

#AutoComments Dictionary Population Function
def checkStrForNull(fieldName):
    fieldValue = row.getValue(fieldName)
    if fieldValue == None:
        fieldValue = ""
    return fieldValue

#High Crown Calculation function to be called when Average slope is > 4%
def high_Crown_Calc(length, width, listSlope):

    #vars for high crown calc
    minSlope = min(listSlope)
    dMax = 0.0
    numPass = 0.0
    widthPass1 = 6.5
    widthPass2 = 6.5
    widthPass3 = 6.5
    widthPass4 = 6.5
    widthPass5 = 0.0
    widthPass6 = 0.0
    widthPass7 = 0.0
    depthCurbPass1 = 1.25
    depthCurbPass2 = 1.25
    depthCurbPass3 = 0.0
    depthCurbPass4 = 0.0
    depthCurbPass5 = 0.0
    depthCurbPass6 = 0.0
    depthCurbPass7 = 0.0
    depthCLPass1 = 0.0
    depthCLPass2 = 0.0
    depthCLPass3 = 0.0
    depthCLPass4 = 0.0
    depthCLPass5 = 0.0
    depthCLPass6 = 0.0
    depthCLPass7 = 0.0
    tonsPass1 = 0.0
    tonsPass2 = 0.0
    tonsPass3 = 0.0
    tonsPass4 = 0.0
    tonsPass5 = 0.0
    tonsPass6 = 0.0
    tonsPass7 = 0.0
    tonsTransitions = 0.0
    totalGrindings = 0.0

    #dMax calc
    if 2.75 <  (minSlope - (.015 * width * 6.0) + 1.25):
        dMax = 2.75
    else:
        dMax = minSlope - (.015 * width * 6.0) + 1.25

    #numPass and widthPass calcs
    if width <= 26.0:
        numPass = 4.0
        widthPass3 = (width - 13)/2.0
        widthPass4 = (width - 13)/2.0
    elif 26.0 < width <= 32.5:
        numPass = 5.0
        widthPass3 = 6.5
        widthPass4 = 6.5
        widthPass5 = width - 26.0
    elif 32.5 < width <= 39.0:
        numPass = 6.0
        widthPass3 = 6.5
        widthPass4 = 6.5
        widthPass5 = (width - 26)/2.0
        widthPass6 = (width - 26)/2.0
    elif 39.0 < width <= 45:
        numPass = 7.0
        widthPass3 = 6.5
        widthPass4 = 6.5
        widthPass5 = (width - 26)/2.0
        widthPass6 = (width - 26)/2.0
        widthPass7 = width - 39.0
    else:
        numPass = 8.0
        widthPass3 = 6.5
        widthPass4 = 6.5
        widthPass5 = (width - 26)/2.0
        widthPass6 = (width - 26)/2.0
        widthPass7 = width - 39.0

    #depth curb pass and depth CL pass calcs
    depthCLPass1 = (((dMax - 1.25) * widthPass1)/(width/2.0)) + 1.25
    depthCLPass2 = (((dMax - 1.25) * widthPass1)/(width/2.0)) + 1.25
    depthCurbPass3 = (((dMax - 1.25) * widthPass1)/(width/2.0)) + 1.25
    depthCLPass3 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25
    depthCurbPass4 = (((dMax - 1.25) * widthPass1)/(width/2.0)) + 1.25
    depthCLPass4 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25

    if numPass == 5:
        depthCurbPass5 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25
        depthCLPass5 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25
    elif numPass == 6:
        depthCurbPass5 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25
        depthCurbPass6 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25
        depthCLPass5 = dMax
        depthCLPass6 = dMax
    elif numPass >= 7:
        depthCurbPass5 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25
        depthCurbPass6 = (((dMax - 1.25) * (widthPass1 + widthPass3))/(width/2.0)) + 1.25
        depthCurbPass7 = (((dMax - 1.25) * (widthPass1 + widthPass3 + widthPass5))/(width/2.0)) + 1.25
        depthCLPass5 = (((dMax - 1.25) * (widthPass1 + widthPass3 + widthPass5))/(width/2.0)) + 1.25
        depthCLPass6 = (((dMax - 1.25) * (widthPass1 + widthPass3 + widthPass5))/(width/2.0)) + 1.25
        depthCLPass7 = (((dMax - 1.25) * (widthPass1 + widthPass3 + widthPass5))/(width/2.0)) + 1.25

    #tons pass calcs
    tonsPass1 = (((depthCurbPass1 + depthCLPass1)/2.0) * widthPass1) * (((length - 20.0)/9.0)* (130.0/2000.0))
    tonsPass2 = ((depthCurbPass2 + depthCLPass2)/2.0) * widthPass2 * ((length - 20.0)/9.0)* (130.0/2000.0)
    tonsPass3 = ((depthCurbPass3 + depthCLPass3)/2.0) * widthPass3 * ((length - 20.0)/9.0)* (130.0/2000.0)
    tonsPass4 = ((depthCurbPass4 + depthCLPass4)/2.0) * widthPass4 * ((length - 20.0)/9.0)* (130.0/2000.0)

    if numPass == 5:
        tonsPass5 = ((dMax + depthCurbPass5)/2.0) * widthPass5 * ((length - 20.0)/9.0)* (130.0/2000.0)
    elif numPass == 6:
        tonsPass5 = ((depthCurbPass5 + depthCLPass5)/2.0) * widthPass5 * ((length - 20.0)/9.0)* (130.0/2000.0)
        tonsPass6 = ((depthCurbPass6 + depthCLPass6)/2.0) * widthPass6 * ((length - 20.0)/9.0)* (130.0/2000.0)
    elif numPass >= 7:
        tonsPass5 = ((depthCurbPass5 + depthCLPass5)/2.0) * widthPass5 * ((length - 20.0)/9.0)* (130.0/2000.0)
        tonsPass6 = ((depthCurbPass6 + depthCLPass6)/2.0) * widthPass6 * ((length - 20.0)/9.0)* (130.0/2000.0)
        tonsPass7 = ((depthCurbPass7 + depthCLPass7)/2.0) * widthPass7 * ((length - 20.0)/9.0)* (130.0/2000.0)

    #tons transitions calc
    tonsTransitions = width * (40.0/9.0) *(((numPass + 3.0) * 1.5) + (depthCurbPass3 + depthCurbPass4 + depthCurbPass5 + depthCurbPass6 + depthCurbPass7))/((5.0)+ numPass + 3.0) * (130.0/2000.0)

    #total grindings calc
    totalGrindings = tonsPass1 + tonsPass2 + tonsPass3 + tonsPass4 + tonsPass5 + tonsPass6 + tonsPass7 + tonsTransitions

    return totalGrindings


print "..."
# Setting up Dictionaries
# Feature Class Dictionaries
# ADDING DICTIONARIES FOR ALL FC'S

MainDict_SY = {}
MainDict_TON = {}
AddPaveDict_SY = {}
AddPaveDict_TON = {}
CornerRDict_SY = {}
CornerRDict_TON = {}
AlleyPave_SY = {}
AlleyPave_TON = {}


# Pavement Dictionaries
SDC_Dict = {}
DYC_Dict = {}
SB_Dict = {}
IC_Dict = {}
SC_Dict = {}

# Slope Dictionaries
slope1 = {}
slope2 = {}
slope3 = {}
slope4 = {}

#Misc Block Dictionaries
CornerHouse_Dict = {}
SpeedHump_Dict = {}
SpeedHumpAddr_Dict = {}

#Auto-Comments Dictionary
AutoComments_Dict = {}

#Bike Rack Type Dictionary
BikeRack_Dict = {}

#Alley Composition Dictionaries
AACompDirt = {}
AACompConcrete = {}
AACompCobblestone = {}
AACompAsphault = {}
AACompOther = {}
AACompOtherText = {}

#High Crown TF Dictionary
HighCrownDict_Bool = {}


# Setting Dictionaries to PageNumber and value of 0.0
s_cursor = arcpy.SearchCursor(blockCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:
    pageNo = row.getValue("PageNo"); print pageNo
    """Added SurveyBy for Final Calcs"""#TBU-01/23/2014
    SurveyBy = row.getValue("SurveyBy")
    SurveyByDate = row.getValue("SurveyByDate")
    value = 0.0
    # Fill Pavement Dictionaries
    if pageNo in SDC_Dict:
        SDC_Dict.update({pageNo : SDC_Dict[pageNo] + value})
    elif pageNo not in SDC_Dict:
        SDC_Dict.update({pageNo : value})
    if pageNo in DYC_Dict:
        DYC_Dict.update({pageNo : DYC_Dict[pageNo] + value})
    elif pageNo not in DYC_Dict:
        DYC_Dict.update({pageNo : value})
    if pageNo in SB_Dict:
        SB_Dict.update({pageNo : SB_Dict[pageNo] + value})
    elif pageNo not in SB_Dict:
        SB_Dict.update({pageNo : value})
    if pageNo in IC_Dict:
        IC_Dict.update({pageNo : IC_Dict[pageNo] + value})
    elif pageNo not in IC_Dict:
        IC_Dict.update({pageNo : value})
    if pageNo in SC_Dict:
        SC_Dict.update({pageNo : SC_Dict[pageNo] + value})
    elif pageNo not in SC_Dict:
        SC_Dict.update({pageNo : value})

    # Fill Feature Class Dictionaries # ADDED NEW DICTIONARIES
    if pageNo in MainDict_SY:
        MainDict_SY.update({pageNo : MainDict_SY[pageNo] + value})
    elif pageNo not in MainDict_SY:
        MainDict_SY.update({pageNo : value})
    if pageNo in MainDict_TON:
        MainDict_TON.update({pageNo : MainDict_TON[pageNo] + value})
    elif pageNo not in MainDict_TON:
        MainDict_TON.update({pageNo : value})
    if pageNo in AddPaveDict_SY:
        AddPaveDict_SY.update({pageNo : AddPaveDict_SY[pageNo] + value})
    elif pageNo not in AddPaveDict_SY:
        AddPaveDict_SY.update({pageNo : value})
    if pageNo in AddPaveDict_TON:
        AddPaveDict_TON.update({pageNo : AddPaveDict_TON[pageNo] + value})
    elif pageNo not in AddPaveDict_TON:
        AddPaveDict_TON.update({pageNo : value})
    if pageNo in CornerRDict_SY:
        CornerRDict_SY.update({pageNo : CornerRDict_SY[pageNo] + value})
    elif pageNo not in CornerRDict_SY:
        CornerRDict_SY.update({pageNo : value})
    if pageNo in CornerRDict_TON:
        CornerRDict_TON.update({pageNo : CornerRDict_TON[pageNo] + value})
    elif pageNo not in CornerRDict_TON:
        CornerRDict_TON.update({pageNo : value})
    if pageNo in AlleyPave_SY:
        AlleyPave_SY.update({pageNo : AlleyPave_SY[pageNo] + value})
    elif pageNo not in AlleyPave_SY:
        AlleyPave_SY.update({pageNo : value})
    if pageNo in AlleyPave_TON:
        AlleyPave_TON.update({pageNo : AlleyPave_TON[pageNo] + value})
    elif pageNo not in AlleyPave_TON:
        AlleyPave_TON.update({pageNo : value})

    # ADDED FOR SLOPE DICTIONARIES
    if pageNo in slope1:
        slope1.update({pageNo : slope1[pageNo] + value})
    elif pageNo not in slope1:
        slope1.update({pageNo : value})
    if pageNo in slope2:
        slope2.update({pageNo : slope2[pageNo] + value})
    elif pageNo not in slope2:
        slope2.update({pageNo : value})
    if pageNo in slope3:
        slope3.update({pageNo : slope3[pageNo] + value})
    elif pageNo not in slope3:
        slope3.update({pageNo : value})
    if pageNo in slope4:
        slope4.update({pageNo : slope4[pageNo] + value})
    elif pageNo not in slope4:
        slope4.update({pageNo : value})

    #Misc Block Dictionaries
    CornerHouse_Dict.update({pageNo : ""})
    SpeedHump_Dict.update({pageNo : value})
    SpeedHumpAddr_Dict.update({pageNo : ""})
    AutoComments_Dict.update({pageNo : ""})
    BikeRack_Dict.update({pageNo : ""})

    #AA Comp Dictionaries
    AACompDirt.update({pageNo : ""})
    AACompConcrete.update({pageNo : ""})
    AACompCobblestone.update({pageNo : ""})
    AACompAsphault.update({pageNo : ""})
    AACompOther.update({pageNo : ""})
    AACompOtherText.update({pageNo : ""})

    #High Crown Dict
    HighCrownDict_Bool.update({pageNo : ""})



del s_cursor

print "Mainline:"
print MainDict_SY
print MainDict_TON
print ".."
print "Additional Pavement:"
print AddPaveDict_SY
print AddPaveDict_TON
print ".."
print "Corner Return:"
print CornerRDict_SY
print CornerRDict_TON
print ".."
print "Alley Pavement:"
print AlleyPave_SY
print AlleyPave_TON
print ".."
print "Pavement Markings:"
print SDC_Dict
print DYC_Dict
print SB_Dict
print IC_Dict
print SC_Dict
print "Slope:"
print slope1
print slope2
print slope3
print slope4

print "..."

# Create Update Cursor for Mainline Pavement Area
print "Starting update for Mainline Pavement Area..."
arcpy.AddMessage("Processing Street data from project " + cceNo)
s_cursor = arcpy.SearchCursor(streetCopy) # SWITCHED TO SEARCH CURSOR # DON'T NEED TO UPDATE FIELDS FOR COPIES
count = 0
for row in s_cursor:  #ADDED FOR SEARCH CURSOR
    pageNo = row.getValue("PageNo")
    length = row.getValue("MeasureLength") #ADDED
    width = row.getValue("MeasureWidth") #ADDED
    mainSY = (length * width) / 9.0
    slopeDepth1 = row.getValue("SlopeCalcDepth1") #ADDED
    slopeDepth2 = row.getValue("SlopeCalcDepth2") #ADDED
    slopeDepth3 = row.getValue("SlopeCalcDepth3") #ADDED
    slopeDepth4 = row.getValue("SlopeCalcDepth4") #ADDED
    listSlope = [slopeDepth1, slopeDepth2, slopeDepth3, slopeDepth4]
    depth_average = (slopeDepth1 + slopeDepth2 + slopeDepth3 + slopeDepth4) / 4.0
    if depth_average == 0.0:
        slope_average = depth_average
    else:
        slope_average = depth_average / ((width / 2.0) * 12.0)
    if slope_average < .04:
        mainTON = mainSY * 0.11375
        HighCrownTF = False
    else:
        mainTON = high_Crown_Calc(length, width, listSlope)
        HighCrownTF = True

    #Mainline (Street) Area
    if pageNo in MainDict_SY:
        MainDict_SY.update({pageNo : MainDict_SY[pageNo] + mainSY}); print mainSY; print "...MainDict_SY is updated"
    elif pageNo not in MainDict_SY:
        MainDict_SY.update({pageNo : mainSY}); print mainSY; print "...MainDict_SY is updated"

    #Mainline (Street) Pavement Grinding
    if pageNo in MainDict_TON:
        MainDict_TON.update({pageNo : MainDict_TON[pageNo] + mainTON}); print mainTON; print "...MainDict_TON is updated"
    elif pageNo not in MainDict_TON:
        MainDict_TON.update({pageNo : mainTON}); print mainTON; print "...MainDict_TON is updated"

    #Mainline (Street) Is High Crown?
    if pageNo in HighCrownDict_Bool:
        HighCrownDict_Bool.update({pageNo : HighCrownTF}); print HighCrownTF; print "...HighCrownTF is updated"

del s_cursor

arcpy.AddMessage("Processing Additional Pavement data from project " + cceNo)
s_cursor = arcpy.SearchCursor(addCopy) # SWITCHED TO SEARCH CURSOR # DON'T NEED TO UPDATE FIELDS FOR COPIES
count = 0
for row in s_cursor:  #ADDED FOR SEARCH CURSOR
    pageNo = row.getValue("PageNo")
    length = row.getValue("MeasureLength") #ADDED
    width = row.getValue("MeasureWidth") #ADDED
    addSY = (length * width) / 9.0
    addTON = ((addSY * 1.75) * 130.0) / 2000.0

    #Additional Pavement Area
    if pageNo in AddPaveDict_SY:
        AddPaveDict_SY.update({pageNo : AddPaveDict_SY[pageNo] + addSY}); print addSY; print "...AddPaveDict_SY is updated"
    elif pageNo not in AddPaveDict_SY:
        AddPaveDict_SY.update({pageNo : addSY}); print addSY; print "...AddPaveDict_SY is updated"
    #Additional Pavement Grinding
    if pageNo in AddPaveDict_TON:
        AddPaveDict_TON.update({pageNo : AddPaveDict_TON[pageNo] + addTON}); print addTON; print "...AddPaveDict_TON is updated"
    elif pageNo not in AddPaveDict_TON:
        AddPaveDict_TON.update({paveNo : addTON}); print addTON; print "...AddPaveDict_TON is updated"
del s_cursor

arcpy.AddMessage("Processing Corner Return data from project " + cceNo)
s_cursor = arcpy.SearchCursor(cornerRCopy) # SWITCHED TO SEARCH CURSOR # DON'T NEED TO UPDATE FIELDS FOR COPIES
count = 0
for row in s_cursor:  #ADDED FOR SEARCH CURSOR
    pageNo = row.getValue("PageNo")
    length = row.getValue("MeasureLength") #ADDED
    width = row.getValue("MeasureWidth") #ADDED
    crSY = (length * width) / 18.0
    crTON = ((crSY * 1.75) * 130.0) / 2000.0

    #Corner Return Area
    if pageNo in CornerRDict_SY:
        CornerRDict_SY.update({pageNo : CornerRDict_SY[pageNo] + crSY}); print crSY; print "...CornerRDict_SY is updated"
    elif pageNo not in CornerRDict_SY:
        CornerRDict_SY.update({pageNo : crSY}); print crSY; print "...CornerRDict_SY is updated"
    #Corner Return Grinding
    if pageNo in CornerRDict_TON:
        CornerRDict_TON.update({pageNo : CornerRDict_TON[pageNo] + crTON}); print crTON; print "...CornerRDict_TON is updated"
    elif pageNo not in CornerRDict_TON:
        CornerRDict_TON.update({paveNo : crTON}); print crTON; print "...CornerRDict_TON is updated"
del s_cursor

arcpy.AddMessage("Processing Alley Pavement data from project " + cceNo)
s_cursor = arcpy.SearchCursor(alleypaveCopy) # SWITCHED TO SEARCH CURSOR # DON'T NEED TO UPDATE FIELDS FOR COPIES
count = 0
for row in s_cursor:  #ADDED FOR SEARCH CURSOR
    pageNo = row.getValue("PageNo")
    length = row.getValue("MeasureLength") #ADDED
    width = row.getValue("MeasureWidth") #ADDED
    alleySY = (length * width) / 9.0
    alleyTON = ((alleySY * 2.0) * 130.0) / 2000.0

    #Alley Pavement Area
    if pageNo in AlleyPave_SY:
        AlleyPave_SY.update({pageNo : AlleyPave_SY[pageNo] + alleySY}); print alleySY; print "...AlleyPave_SY is updated"
    elif pageNo not in AlleyPave_SY:
        AlleyPave_SY.update({pageNo : alleySY}); print alleySY; print "...AlleyPave_SY is updated"
    #Alley Pavement Grinding
    if pageNo in AlleyPave_TON:
        AlleyPave_TON.update({pageNo : AlleyPave_TON[pageNo] + alleyTON}); print alleyTON; print "...AlleyPave_TON is updated"
    elif pageNo not in AlleyPave_TON:
        AlleyPave_TON.update({paveNo : alleyTON}); print alleyTON; print "...AlleyPave_TON is updated"

del s_cursor

arcpy.AddMessage("Processing Pavement Markings data from project " + cceNo)
s_cursor = arcpy.SearchCursor(paveMarksCopy) # SWITCHED TO SEARCH CURSOR # DON'T NEED TO UPDATE FIELDS FOR COPIES
count = 0
for row in s_cursor:  #ADDED FOR SEARCH CURSOR
    #Pavement Markings
    markingType = row.getValue("MarkingType"); print markingType
    pageNo = row.getValue("PageNo")
    if markingType == "Skip Dash Centerline":
        if pageNo in SDC_Dict:
            SDC = row.getValue("MeasureLength")
            SDC_Dict.update({pageNo : SDC_Dict[pageNo] + SDC}); print SDC; print "...SDC_Dict is updated"
        else:
            SDC = row.getValue("MeasureLength")
            SDC_Dict.update({pageNo : SDC}); print SDC; print "...SDC_Dict is updated"
    if markingType == "Double Yellow Centerline":
        if pageNo in DYC_Dict:
            DYC = row.getValue("MeasureLength")
            DYC_Dict.update({pageNo : DYC_Dict[pageNo] + DYC}); print DYC; print "...DYC_Dict is updated"
        else:
            DYC = row.getValue("MeasureLength")
            DYC_Dict.update({pageNo : DYC}); print DYC; print "...DYC_Dict is updated"
    if markingType == "Stop Bar":
        if pageNo in SB_Dict:
            SB = row.getValue("MeasureLength")
            SB_Dict.update({pageNo : SB_Dict[pageNo] + SB}); print SB; print "...SB_Dict is updated"
        else:
            SB = row.getValue("MeasureLength")
            SB_Dict.update({pageNo : SB}); print SB; print "...SB_Dict is updated"
    if markingType == "International Crosswalk":
        if pageNo in IC_Dict:
            IC = row.getValue("MeasureLength")
            IC_Dict.update({pageNo : IC_Dict[pageNo] + IC}); print IC; print "...IC_Dict is updated"
        else:
            IC = row.getValue("MeasureLength")
            IC_Dict.update({pageNo : IC}); print IC; print "...IC_Dict is updated"
    if markingType == "Standard Crosswalk":
        if pageNo in SC_Dict:
            SC = row.getValue("MeasureLength")
            SC_Dict.update({pageNo : SC_Dict[pageNo] + SC}); print SC; print "...SC_Dict is updated"
        else:
            SC = row.getValue("MeasureLength")
            SC_Dict.update({pageNo : SC}); print SC; print "...SC_Dict is updated"

del s_cursor

arcpy.AddMessage("Processing Bike Rack data from project " + cceNo)
s_cursor = arcpy.SearchCursor(bikeRackCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:

    pageNo = row.getValue("PageNo")
    measureType = row.getValue("MeasureType")


    if "Shared" in measureType:
        bikeLocType = row.getValue("BikeRackLocationType")
        bikeLoc = row.getValue("BikeRackLocationType")
        if bikeLoc is None:
            bikeLoc = "";
        comString = "Bike Sharing Stations in " + bikeLocType + ": " + bikeLoc

        if len(BikeRack_Dict[pageNo]) == 0:
            BikeRack_Dict.update({pageNo : comString})
        else:
            BikeRack_Dict.update({pageNo : BikeRack_Dict[pageNo] + "; " + comString})


del s_cursor

arcpy.AddMessage("Processing SpeedHump data from project " + cceNo)
s_cursor = arcpy.SearchCursor(speedHumpCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:

    pageNo = row.getValue("PageNo")
    address = row.getValue("AddressDimension")
    intAddress = [int(s) for s in address.split() if s.isdigit()]

    if pageNo in SpeedHump_Dict:
        SpeedHump_Dict.update({pageNo : SpeedHump_Dict[pageNo] + 1})
    else:
        SpeedHump_Dict.update({pageNo : 1})

    if pageNo in SpeedHumpAddr_Dict:
        if SpeedHumpAddr_Dict[pageNo] == "":
            SpeedHumpAddr_Dict.update({pageNo : SpeedHumpAddr_Dict[pageNo] + ", " + str(intAddress[0])})
        else:
            SpeedHump_Dict.update({pageNo : str(intAddress[0])})
    else:
        SpeedHump_Dict.update({pageNo : str(intAddress[0])})

del s_cursor

arcpy.AddMessage("Processing BlockCenterline data from project " + cceNo)
s_cursor = arcpy.SearchCursor(blockCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:

    pageNo = row.getValue("PageNo")
    CornerHouse = row.getValue("strBlockCornerHouse")
    if CornerHouse == None:
           CornerHouse = ""
    CornerHouse_Dict.update({pageNo : CornerHouse}); print CornerHouse

    #AutoComments: Get Field Values

    #Surface Conditon - AA, AS, RA, RS
    SurfaceCondition = checkStrForNull("SurfaceCondition")
    ShowSurfaceCondition = checkStrForNull("AutoComShow2_YN")
    #Alley Drainage Issues- AA
    DrainAlleyPotFloodYN = checkStrForNull("DrainAlleyPotFloodYN")
    ShowDrainAlleyPotFlood = checkStrForNull("AutoComShow12_YN")
    DrainAlleyCSRResurfPotFloodYN = checkStrForNull("DrainAlleyCSRResurfPotFloodYN")
    ShowDrainAlleyPotFlood = checkStrForNull("AutoComShow12_YN")
    #Special Locations - All
    SchoolYN = checkStrForNull("SchoolYN")
    ShowSchoolYN = checkStrForNull("AutoComShow3_YN")
    FireStationYN = checkStrForNull("FireStationYN")
    ShowFireStationYN = checkStrForNull("AutoComShow4_YN")
    PoliceStationYN = checkStrForNull("PoliceStationYN")
    ShowPoliceStationYN = checkStrForNull("AutoComShow5_YN")
    ChurchYN = checkStrForNull("ChurchYN")
    ShowChurchYN = checkStrForNull("AutoComShow6_YN")
    FuneralHomeYN = checkStrForNull("FuneralHomeYN")
    ShowFuneralHomeYN = checkStrForNull("AutoComShow7_YN")
    HospitalYN = checkStrForNull("HospitalYN")
    ShowHospitalYN = checkStrForNull("AutoComShow8_YN")
    OtherSpecialLocYN = checkStrForNull("OtherSpecialLocYN")
    ShowOtherSpecialLocYN = checkStrForNull("AutoComShow9_YN")
    #Street Drainage Issues - AS
    DrainStreetStandWaterYN = checkStrForNull("DrainStreetStandWaterYN")
    ShowDrainStreetStandWaterYN = checkStrForNull("AutoComShow10_YN")
    DrainStreetDebrisYN = checkStrForNull("DrainStreetDebrisYN")
    ShowDrainStreetDebrisYN = checkStrForNull("AutoComShow11_YN")
    #Other Pavement Markings
    OtherPaveMarksYN = checkStrForNull("OtherPaveMarksYN")
    ShowOtherPaveMarksYN = checkStrForNull("AutoComShow13_YN")
    #Special Conditions
    LoopDetectorsYN = checkStrForNull("LoopDetectorsYN")
    ShowLoopDetectorsYN = checkStrForNull("AutoComShow14_YN")
    BusStopYN = checkStrForNull("BusStopYN")
    ShowBusStopYN = checkStrForNull("AutoComShow15_YN")
    ParkPayBoxesYN = checkStrForNull("ParkPayBoxesYN")
    ShowParkPayBoxesYN = checkStrForNull("AutoComShow16_YN")
    HeightRestrictYN = checkStrForNull("HeightRestrictYN")
    ShowHeightRestrictYN = checkStrForNull("AutoComShow17_YN")
    ViaductYN = checkStrForNull("ViaductYN")
    ShowViaductYN = checkStrForNull("AutoComShow18_YN")
    WPABlockYN = checkStrForNull("WPABlockYN")
    ShowWPABlockYN = checkStrForNull("AutoComShow19_YN")
    CurbGutterPoorYN = checkStrForNull("CurbGutterPoorYN")
    ShowCurbGutterPoorYN = checkStrForNull("AutoComShow20_YN")
    GutterPanOverlaidYN = checkStrForNull("GutterPanOverlaidYN")
    ShowGutterPanOverlaidYN = checkStrForNull("AutoComShow21_YN")
    StructureRepairYN = checkStrForNull("StructureRepairYN")
    ShowStructureRepairYN = checkStrForNull("AutoComShow22_YN")
    CuldeSacYN = checkStrForNull("CulDeSacYN")
    ShowCuldeSacYN = checkStrForNull("AutoComShow23_YN")
    DeadEndYN = checkStrForNull("DeadEndYN")
    ShowDeadEndYN = checkStrForNull("AutoComShow24_YN")
    GuardrailYN = checkStrForNull("GuardrailYN")
    ShowGuardrailYN = checkStrForNull("AutoComShow25_YN")
    DecorFenceYN = checkStrForNull("DecorFenceYN")
    ShowDecorFenceYN = checkStrForNull("AutoComShow26_YN")
    #Survey Draw Comments
    SurveyDrawComments = checkStrForNull("SurveyDrawComments")
    ShowSurveyDrawComments = checkStrForNull("AutoComShow28_YN")

    ShowBikeRack = checkStrForNull("AutoComShow27_YN")

    #Apply Comments to Dictionary
    if HighCrownDict_Bool[pageNo] and projectType == "AS":
        updateAutoCommentsDict("High Crown", "None", False)
    if SpeedHumpAddr_Dict[pageNo] != "" and (projectType == "AA" or projectType == "AS"):
        updateAutoCommentsDict("Speed Hump: " + SpeedHumpAddr_Dict[pageNo], "None", False)
    if SchoolYN == "Yes" and ShowSchoolYN != "No":
        updateAutoCommentsDict("School", "SchoolNotes", True)
    if FireStationYN == "Yes" and ShowFireStationYN != "No":
        updateAutoCommentsDict("Fire Station", "FireStationNotes", True)
    if PoliceStationYN == "Yes" and ShowPoliceStationYN != "No":
        updateAutoCommentsDict("Police Station", "PoliceStationNotes", True)
    if ChurchYN == "Yes" and ShowChurchYN != "No":
        updateAutoCommentsDict("Church", "ChurchNotes", True)
    if FuneralHomeYN == "Yes" and ShowFuneralHomeYN != "No":
        updateAutoCommentsDict("Funeral Home", "FuneralHomeNotes", True)
    if HospitalYN == "Yes" and ShowHospitalYN != "No":
        updateAutoCommentsDict("Hosptital", "HosptitalNotes", True)
    if OtherSpecialLocYN == "Yes" and ShowOtherSpecialLocYN != "No":
        updateAutoCommentsDict("Other Special Location", "OtherSpecialLocNotes", True)
    if OtherPaveMarksYN == "Yes" and ShowOtherPaveMarksYN != "No" and (projectType == "AA" or projectType == "AR" or projectType == "AS" or projectType == "CC" or projectType == "CO" or projectType == "CS"):
        updateAutoCommentsDict("Pavement Markings not shown", "OtherPaveMarksNotes", True)
    if LoopDetectorsYN == "Yes" and ShowLoopDetectorsYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Loop Detectors Present", "LoopDetectorNotes", True)
    if BusStopYN == "Yes" and ShowBusStopYN != "No":
        updateAutoCommentsDict("Bus Stop", "BusStopLocation", True)
    if ParkPayBoxesYN == "Yes" and ShowParkPayBoxesYN != "No":
        updateAutoCommentsDict("Parking Pay Boxes Present", "ParkPayBoxesNotes", True)
    if HeightRestrictYN == "Yes" and ShowHeightRestrictYN != "No" and (projectType == "AA" or projectType == "AS"):
        updateAutoCommentsDict("Height Restriction", "None", False)
    if ViaductYN == "Yes" and ShowViaductYN != "No" and (projectType == "AA" or projectType == "AS"):
        updateAutoCommentsDict("Viaduct", "ViaductNotes", True)
    if WPABlockYN == "Yes" and ShowWPABlockYN != "No" and projectType == "AS":
        updateAutoCommentsDict("WPA Block", "None", False)
    if CurbGutterPoorYN == "Yes" and ShowCurbGutterPoorYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Curb and Gutter in poor shape - Suggest Replacement", "None", False)
    if GutterPanOverlaidYN == "Yes" and ShowGutterPanOverlaidYN != "No":
        updateAutoCommentsDict("Gutter Pan Overlaid", "None", False)
    if StructureRepairYN == "Yes" and ShowStructureRepairYN != "No" and (projectType == "AA" or projectType == "AS"):
        updateAutoCommentsDict("Structure Repair", "StructureRepairNotes", True)
    if CuldeSacYN == "Yes" and ShowCuldeSacYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Cul-de-Sac Present", "None", False)
    if DeadEndYN == "Yes" and ShowDeadEndYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Dead End Street", "None", False)
    if GuardrailYN == "Yes" and ShowGuardrailYN != "No":
        updateAutoCommentsDict("Guardrail", "GuardrailNotes", True)
    if DecorFenceYN == "Yes" and ShowDecorFenceYN != "No" and (projectType == "AR" or projectType == "CC" or projectType == "CO" or projectType == "CS" or projectType == "CA" or projectType == "RS"):
        updateAutoCommentsDict("Existing Decorative Fence", "DecorFenceNotes", True)
    if DrainStreetDebrisYN == "Yes" and ShowDrainStreetDebrisYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Drainage issues noted", "DrainStreetDebrisNotes", False)
    if DrainStreetStandWaterYN == "Yes" and ShowDrainStreetStandWaterYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Drainage issues noted", "DrainStreetStandWaterNotes", False)

    if len(BikeRack_Dict[pageNo]) > 0 and ShowBikeRack != "No":
        updateAutoCommentsDict(BikeRack_Dict[pageNo], "None", False)

    #Survey Comments
    if len(SurveyDrawComments) > 0 and ShowSurveyDrawComments != "No":
        updateAutoCommentsDict("General Comments", "SurveyDrawComments", True)

    #Apply Overriding Comments
    if DrainAlleyPotFloodYN == "Yes" and ShowDrainAlleyPotFlood == "Yes" and projectType == "AA":
        AutoComments_Dict.update({pageNo : "Drop - Potential for flooding into private property. Recommend Green Alley Solution."})
    if DrainAlleyCSRResurfPotFloodYN == "Yes" and ShowDrainAlleyPotFlood and projectType == "AA":
        AutoComments_Dict.update({pageNo : "Drop - Potential for flooding into private property. Recommend Green Alley Solution."})
    if "Drop" in SurfaceCondition and ShowSurfaceCondition == "Yes" and (projectType == "AA" or projectType == "AS"):
        AutoComments_Dict.update({pageNo : "Drop - Good Condition"})
    if "Drop" in SurfaceCondition and ShowSurfaceCondition == "Yes" and (projectType == "RA" or projectType == "RS"):
        AutoComments_Dict.update({pageNo : "Drop - Resurfacing Project Dropped"})


del s_cursor

arcpy.AddMessage("Processing ProjectCenterline data from project " + cceNo)
s_cursor = arcpy.SearchCursor(projectCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:


    WardID = row.getValue("lngWardID")
    if WardID == None:
           WardID = 0
    MenuID = row.getValue("lngMenuID")
    if MenuID == None:
           MenuID = 0

    s_cursor2 = arcpy.SearchCursor(tblMenu, "\"LNGMENUID\"" + " = '" + str(MenuID) + "'")

    for s_row in s_cursor2:
        strMenu = s_row.getValue("strMenu")

del s_cursor

arcpy.AddMessage("Processing Alley Composition data from project " + cceNo)
s_cursor = arcpy.SearchCursor(alleypaveCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:
    YES = "Yes"
    NO = "No"
    EMPTY = ""
    AAComp = row.getValue("AlleyCompType")
    pageNo = row.getValue("PageNo")
    AAValue = row.getValue("AlleyCompOther")
    if pageNo in AACompDirt:
        if AAComp == "Gravel/Dirt":
            AACompDirt.update({pageNo : YES})
        else:
            AACompDirt.update({pageNo : NO})
    if pageNo in AACompConcrete:
        if AAComp == "Concrete":
            AACompConcrete.update({pageNo : YES})
        else:
            AACompConcrete.update({pageNo : NO})
    if pageNo in AACompCobblestone:
        if AAComp == "Cobblestone":
            AACompCobblestone.update({pageNo : YES})
        else:
            AACompCobblestone.update({pageNo : NO})
    if pageNo in AACompAsphault:
        if AAComp == "Asphalt":
            AACompAsphault.update({pageNo : YES})
        else:
            AACompAsphault.update({pageNo : NO})
    if pageNo in AACompOther:
        if AAComp == "Other":
            AACompOther.update({pageNo : YES})
            AACompOtherText.update({pageNo : YES})
        else:
            AACompOther.update({pageNo : AAValue})
            AACompOtherText.update({pageNo : EMPTY})
del s_cursor

print "..."

print "Mainline:"
print MainDict_SY; print "... MainDict_SY"
print MainDict_TON; print "... MainDict_TON"
print ".."
print "Additional Pavement:"
print AddPaveDict_SY; print "... AddPaveDict_SY"
print AddPaveDict_TON; print "... AddPaveDict_TON"
print ".."
print "Corner Return:"
print CornerRDict_SY; print "... CornerRDict_SY"
print CornerRDict_TON; print "... CornerRDict_TON"
print ".."
print "Alley Pavement:"
print AlleyPave_SY; print "... AlleyPave_SY"
print AlleyPave_TON; print "... AlleyPave_TON"
print ".."
print "Pavement Markings:"
print SDC_Dict; print "... SDC_Dict"
print DYC_Dict; print "... DYC_Dict"
print SB_Dict; print "... SB_Dict"
print IC_Dict; print "... IC_Dict"
print SC_Dict; print "... SC_Dict"
print "Slope:"
print slope1; print "... slope1"
print slope2; print "... slope2"
print slope3; print "... slope3"
print slope4; print "... slope4"

print "..."

cceNoCalcs = cceNo

#Find corresponding combo number
if "-ASlRS-" in cceNoCalcs:
    cceNoCalcs = cceNo.replace("-ASlRS-", "-AS-")
if "-AAlRA-" in cceNoCalcs:
    cceNoCalcs = cceNo.replace("-AAlRA-", "-AA-")

print cceNoCalcs
arcpy.AddMessage("Updating Final Calculations " + cceNo)
# Update Final Calcs
u_cursor = arcpy.UpdateCursor(FinalCalcs, "\"strCCEProjectNumber\"" + " = '" + cceNoCalcs + "'")
for row in u_cursor:
    pageNo = row.getValue("PageNo"); print pageNo

    #Find corresponding combo number in Dictionaries
    if "-AS-" in pageNo:
        pageNo = pageNo.replace("-AS-", "-ASlRS-")
    if "-AA-" in pageNo:
        pageNo = pageNo.replace("-AA-", "-AAlRA-")


    print "..."

    # Calc for Totals (SY)((AS,Grind)TON)
    Total_AQ_SY = math.ceil(math.ceil(MainDict_SY[pageNo]) + math.ceil(AddPaveDict_SY[pageNo]) + math.ceil(CornerRDict_SY[pageNo]) + math.ceil(AlleyPave_SY[pageNo]))
    Total_AQ_TON = math.ceil(Total_AQ_SY * 0.112)
    Total_GQ_TON = math.ceil((MainDict_TON[pageNo]) + math.ceil(AddPaveDict_TON[pageNo]) + math.ceil(CornerRDict_TON[pageNo]) + math.ceil(AlleyPave_TON[pageNo]))

    row.setValue("ASResurfSY", Total_AQ_SY); print Total_AQ_SY; print "...Total_AQ_SY is updated"
    row.setValue("ASResurfTons", Total_AQ_TON); print Total_AQ_TON; print "...Total_AQ_TON is updated"
    row.setValue("ASGrindingTons", Total_GQ_TON); print Total_GQ_TON; print "...Total_GQ_TON is updated"

    # Calc For Pavement Markings
    pvm_LN4_T = math.ceil(((SDC_Dict[pageNo]) / 4.0) + ((DYC_Dict[pageNo]) * 2.0))
    pvm_LN6_T = math.ceil((SC_Dict[pageNo]) * 2.0)
    pvm_LN24_T = math.ceil(((IC_Dict[pageNo]) * (6.0 / 4.0)) + (SB_Dict[pageNo]))

    row.setValue("ASPvMark4inLF", pvm_LN4_T); print pvm_LN4_T; print "...pvm_LN4_T is updated"
    row.setValue("ASPvMark6inLF", pvm_LN6_T); print pvm_LN6_T; print "...pvm_LN6_T is updated"
    row.setValue("ASPvMark24inLF", pvm_LN24_T); print pvm_LN24_T; print "...pvm_LN24_T is updated"

    today = datetime.datetime.now()
    print today

    #Corner House
    row.setValue("strBlockCornerHouse", CornerHouse_Dict[pageNo])

    #Number of Speed Hump
    row.setValue("AASpeedHumpCnt", SpeedHump_Dict[pageNo])

    #Record Calc Date
    row.setValue("CalcByDate", today.strftime("%m/%d/%Y"))
    row.setValue("CalcBy", userInit)
    row.setValue("ReviewBy", reviewedBy)
    row.setValue("ReviewByDate", reviewByDate.split(" ")[0])

    """Added"""#TBU-01/23/2014
    #Survey By
    print SurveyBy
    arcpy.AddMessage("Surveyed By: " + SurveyBy)
    row.setValue("SurveyBy", SurveyBy)

    #Survey By Date
    row.setValue("SurveyByDate", SurveyByDate.strftime("%m/%d/%Y"))

    #Project Attributes
    row.setValue("lngMenuID", MenuID)
    row.setValue("lngWardID", WardID)
    row.setValue("strMenu", strMenu)

    if "-RS-" in cceNoCalcs:
        row.setValue("strMenu", "Ramp-Street")
        row.setValue("lngMenuID", "23")

    if "-RA-" in cceNoCalcs:
        row.setValue("strMenu", "Ramp-Alley")
        row.setValue("lngMenuID", "22")

    test = len(AutoComments_Dict[pageNo])
    #Auto - Comments

    """Added to wrap comments"""#TBU-01/31/2014
    comments = AutoComments_Dict[pageNo]

    # Wrap the Comments to a list of strings
    newComments = []
    if "-AA-" in cceNo:
        newComments = textwrap.wrap(comments, 60)
    else:
        newComments = textwrap.wrap(comments, 100)

    # Add Escape sequences for newlines and concatenate
    newCommentsString= ""
    for x in newComments:
        if newComments.index(x) != (len(newComments) - 1):
            newCommentsString += x + " \n"
        else:
            newCommentsString += x

    #Set the value
    row.setValue("Comments", newCommentsString)

    #ALLEY COMP
    if AACompDirt[pageNo] == "Yes":
        row.setValue("AACompDirtYN", "X")
    else:
        row.setValue("AACompDirtYN", " ")
    if AACompConcrete[pageNo] == "Yes":
        row.setValue("AACompConcreteYN", "X")
    else:
        row.setValue("AACompConcreteYN", " ")
    if AACompCobblestone[pageNo] == "Yes":
        row.setValue("AACompCobblestoneYN", "X")
    else:
        row.setValue("AACompCobblestoneYN", " ")
    if AACompAsphault[pageNo] == "Yes":
        row.setValue("AACompCasphaultYN", "X")
    else:
        row.setValue("AACompCasphaultYN", " ")

    if AACompAsphault[pageNo] == "Yes":
        row.setValue("AACompOtherYN", "X")
    else:
        row.setValue("AACompOtherYN", " ")

    row.setValue("AACompOther", AACompOtherText[pageNo])


    #Update the row
    u_cursor.updateRow(row); print "..."

del u_cursor

print "Finished FINAL Calcs..."



