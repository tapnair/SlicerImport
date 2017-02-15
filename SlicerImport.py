# Author-Patrick Rainsberry
# Description-Imports a directory of Fusion Slicer output files

from .SlicerImportCommand import SlicerImportCommand


commands = []
command_defs = []


# Define parameters for 1st command #####
cmd = {
    'commandName': 'Fusion Slicer Import',
    'commandDescription': 'Import a directory of outputs from Fusion Make',
    'commandResources': './resources',
    'cmdId': 'cmdID_Demo_1',
    'workspace': 'FusionSolidEnvironment',
    'toolbarPanelID': 'SolidScriptsAddinsPanel',
    'class': SlicerImportCommand
}

command_defs.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False


# Don't change anything below here:
for cmd_def in command_defs:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)


def run(context):
    for command in commands:
        command.on_run()


def stop(context):
    for command in commands:
        command.on_stop()
