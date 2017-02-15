import os

import adsk.core
import adsk.fusion
import traceback

from .Fusion360Utilities import Fusion360Utilities as futil
from .Fusion360Utilities.Fusion360Utilities import get_app_objects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase


def create_component(target_component, filename):
    transform = adsk.core.Matrix3D.create()
    new_occurrence = target_component.occurrences.addNewComponent(transform)
    new_occurrence.component.name = filename

    return new_occurrence


# Extract file names of all dxf files in a directory
def get_dxf_files(directory):
    dxf_files = []

    for filename in os.listdir(directory):

        if filename.endswith(".dxf"):
            dxf_file = {
                'full_path': os.path.join(directory, filename),
                'name': filename[:-4]
            }
            dxf_files.append(dxf_file)

        else:
            continue

    return dxf_files


# Returns the magnitude of the bounding box in the specified direction
def get_bb_in_direction(fusion_object, direction_vector):

    # Get bounding box extents
    max_point = fusion_object.boundingBox.maxPoint
    min_point = fusion_object.boundingBox.minPoint
    delta_vector = adsk.core.Vector3D.create(max_point.x - min_point.x,
                                             max_point.y - min_point.y,
                                             max_point.z - min_point.z)

    # Get bounding box delta in specified direction
    delta = delta_vector.dotProduct(direction_vector)
    return delta


# Transforms an occurrence along a specified vector by a specified amount
def transform_along_vector(occurrence, direction_vector, magnitude):
    
    # Create a vector for the translation
    vector = direction_vector.copy()
    vector.scaleBy(magnitude)

    # Create a transform to do move
    old_transform = adsk.core.Matrix3D.cast(occurrence.transform)
    new_transform = adsk.core.Matrix3D.create()
    new_transform.translation = vector
    old_transform.transformBy(new_transform)

    # Transform Component
    occurrence.transform = old_transform


# Main class for import command
class SlicerImportCommand(Fusion360CommandBase):

    # Executed on user pressing OK button
    def on_execute(self, command, command_inputs, args, input_values):

        # Start a time line group
        start_index = futil.start_group()

        # Gets necessary application objects
        app_objects = get_app_objects()

        # Define spacing and directions
        x_vector = adsk.core.Vector3D.create(1.0, 0.0, 0.0)
        x_magnitude = 0.0
        y_vector = adsk.core.Vector3D.create(0.0, 1.0, 0.0)
        y_magnitude = 0.0
        y_row_max = 0.0
        row_count = 0

        # Read in dxf Files
        dxf_files = get_dxf_files(input_values['directory'])

        # Iterate all dxf files and create components
        for dxf_file in dxf_files:

            # Create new component for this DXF file
            occurrence = create_component(app_objects['root_comp'], dxf_file['name'])

            # Import all layers of DXF to XY plane
            sketches = futil.import_dxf(dxf_file['full_path'], occurrence.component,
                                        occurrence.component.xYConstructionPlane)

            # Get sketches
            boundary_sketch = futil.sketch_by_name(sketches, 'boundary')
            frame_sketch = futil.sketch_by_name(sketches, 'frame')

            # Extrude boundary layer
            futil.extrude_all_profiles(boundary_sketch, input_values['distance'], occurrence.component)

            # todo extrude holes

            # Tight pack vs arrange frames
            if input_values['tight_pack']:
                check_sketch = boundary_sketch
                frame_sketch.deleteMe()
            else:
                check_sketch = frame_sketch

            # Get extents of current component in placement direction
            x_delta = get_bb_in_direction(check_sketch, x_vector)
            y_delta = get_bb_in_direction(check_sketch, y_vector)

            # Move component in specified direction
            transform_along_vector(occurrence, x_vector, x_magnitude)
            transform_along_vector(occurrence, y_vector, y_magnitude)

            # Update document and capture position of new component
            adsk.doEvents()
            if app_objects['design'].snapshots.hasPendingSnapshot:
                app_objects['design'].snapshots.add()

            # Increment magnitude by desired component size and spacing
            x_magnitude += input_values['spacing']
            x_magnitude += x_delta
            row_count += 1

            if y_delta > y_row_max:
                y_row_max = y_delta

            # Move to next row
            if row_count >= input_values['rows']:

                y_magnitude += input_values['spacing']
                y_magnitude += y_row_max
                y_row_max = 0.0
                x_magnitude = 0.0
                row_count = 0

        # Close time line group
        futil.end_group(start_index)

    # Define the user interface for the command
    def on_create(self, command, command_inputs):

        # Gets necessary application objects
        app_objects = get_app_objects()

        import os

        # Create file browser dialog box
        file_dialog = app_objects['ui'].createFileDialog()
        file_dialog.filter = ".DXF files (*.dxf);;All files (*.*)"
        file_dialog.initialDirectory = os.path.expanduser("~/Desktop/")
        file_dialog.isMultiSelectEnabled = False
        file_dialog.title = 'Select any file in the Fusion Slicer Output Directory'

        dialog_results = file_dialog.showOpen()
        if dialog_results == adsk.core.DialogResults.DialogOK:
            default_dir = os.path.dirname(file_dialog.filename)
        else:
            default_dir = ''

        # Gets default units
        default_units = app_objects['units_manager'].defaultLengthUnits

        # Define that the default values for the command in cm
        distance_default = adsk.core.ValueInput.createByReal(5)
        spacing_default = adsk.core.ValueInput.createByReal(1)

        # Directory of files to import
        command_inputs.addStringValueInput('directory', 'Output Directory from Make', default_dir)

        # Thickness of profiles
        command_inputs.addValueInput('distance', 'Thickness of sections: ', default_units, distance_default)

        # Spacing between borders
        command_inputs.addValueInput('spacing', 'Spacing between parts: ', default_units, spacing_default)

        # Number of components per rows
        command_inputs.addIntegerSpinnerCommandInput('rows', 'Number per row: ', 1, 999, 1, 8)

        # Tight pack?
        command_inputs.addBoolValueInput("tight_pack", 'Tightly pack frames?', True)