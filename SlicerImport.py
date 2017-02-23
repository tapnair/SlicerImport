# Author-Patrick Rainsberry
# Description-Imports a directory of Fusion Slicer output files

from .SlicerImportCommand import SlicerImportCommand


commands = []
cmd_definitions = []


# Define parameters for 1st command #####
cmd = {
    'cmd_name': 'Fusion Slicer Import',
    'cmd_description': 'Import a directory of outputs from Fusion Make',
    'cmd_resources': './resources',
    'cmd_id': 'cmdID_Demo_1',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'SolidScriptsAddinsPanel',
    'class': SlicerImportCommand
}

cmd_definitions.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False


# Don't change anything below here:
for cmd_def in cmd_definitions:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)


def run(context):
    for run_command in commands:
        run_command.on_run()


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()
