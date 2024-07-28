from pathlib import Path
import sys

import pyvista as pv
from trame.app import get_server
from trame.assets.remote import download_file_from_google_drive
from trame.widgets import vuetify3 as vuetify, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout

from vtk import vtkFlyingEdges3D
from vtk.util import numpy_support as np_s

from data_loader import fetch_dataset

# Data loading
dataset = 'star_nanoparticle'
if len(sys.argv) > 1:
    dataset = sys.argv[1]

selected_dataset_path = fetch_dataset(dataset)

# Read in the dataset from the path
input_data = pv.read(selected_dataset_path)

flying_edges = vtkFlyingEdges3D()
flying_edges.SetInputData(input_data)
flying_edges.SetValue(0, 5)
flying_edges.Update()

pl = pv.Plotter()
mesh = pl.add_mesh(flying_edges.GetOutputDataObject(0))

# Set up camera position
renderer = pl.renderer
renderer.camera_position = renderer.get_default_cam_pos()
renderer.ResetCamera()

render_window = pl.render_window
# render_window.OffScreenRenderingOn()
mesh.GetMapper().SetScalarRange(0, 255)

# Trame initialization
server = get_server()
state = server.state
ctrl = server.controller
state.trame__title == 'Example Contour Rendering'


# UI Callbacks
@state.change('contour_value')
def contour_changed(contour_value, **kwargs):
    print(f'{contour_value=}')
    flying_edges.SetValue(0, contour_value)
    flying_edges.Update()
    mesh.GetMapper().SetInputDataObject(flying_edges.GetOutputDataObject(0))

    # Update the view
    mesh.Modified()
    render_window.Render()
    ctrl.view_update()


with SinglePageLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VLabel('Contour')
        vuetify.VSpacer()
        vuetify.VSlider(
            v_model=('contour_value', 5),
            min=0.1,
            max=255,
            step=1,
            hide_details=True,
            dense=True,
            style='max-width: 300px',
        )
        vuetify.VDivider(vertical=True, classes='mx-2')

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vtk_widgets.VtkRemoteView(
                render_window,
                interactive_ratio=1,
            ) as html_view:
                ctrl.view_update = html_view.update


if __name__ == '__main__':
    server.start()
