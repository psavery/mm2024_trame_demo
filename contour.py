#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyvista",
#     "scipy",
#     "trame",
#     "trame-vtk",
#     "trame-vuetify",
#     "vtk",
# ]
# ///

from pathlib import Path
import sys

import pyvista as pv

from trame.app import get_server
from trame.assets.remote import download_file_from_google_drive
from trame.widgets import html, vuetify3 as vuetify, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout

from vtk import vtkFlyingEdges3D

data_dir = Path(__file__).parent / 'data'

star_nanoparticle_path = data_dir / 'Recon_NanoParticle_doi_10.1021-nl103400a.tiff'  # noqa
star_nanoparticle_google_drive_id = '1S821zdERFfJ-TlnMeyE0aTdBdV642OL4'

nanotube_path = data_dir / 'reconstructed_tiltser_180_subsampled_10.6084-m9.figshare.c.2185342.v2.tiff'  # noqa
nanotube_google_drive_id = '1bJi4yYis8yCh2A7yIpAzYjGUrqSV1us2'


def fetch_dataset(name: str) -> Path:
    if name == 'star_nanoparticle':
        path = star_nanoparticle_path
        drive_id = star_nanoparticle_google_drive_id
    else:
        path = nanotube_path
        drive_id = nanotube_google_drive_id

    # Make sure the data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        print('Downloading dataset from Google Drive...')
        download_file_from_google_drive(drive_id, path)
    return path

# Data loading
dataset = 'star_nanoparticle'
if len(sys.argv) > 1:
    dataset = sys.argv[1]

min_contour = 1 if dataset == 'star_nanoparticle' else 80
default_contour = 10 if dataset == 'star_nanoparticle' else 127

selected_dataset_path = fetch_dataset(dataset)

# Read in the dataset from the path
input_data = pv.read(selected_dataset_path)

# Set up the contouring algorithm: Flying Edges
flying_edges = vtkFlyingEdges3D()
flying_edges.SetInputData(input_data)
flying_edges.SetValue(0, default_contour)
flying_edges.Update()

# Create the mesh
pl = pv.Plotter()
mesh = pl.add_mesh(flying_edges.GetOutputDataObject(0))

# Set up camera position
renderer = pl.renderer
renderer.camera_position = renderer.get_default_cam_pos()
renderer.ResetCamera()

# Turn on offscreen rendering and set the color range
render_window = pl.render_window
render_window.OffScreenRenderingOn()
mesh.GetMapper().SetScalarRange(0, 255)

# Trame initialization
server = get_server()
state = server.state
ctrl = server.controller
state.trame__title == 'Example Contour Rendering'


# UI Callbacks
@state.change('contour_value')
def contour_changed(contour_value, **kwargs):
    flying_edges.SetValue(0, contour_value)
    flying_edges.Update()
    mesh.GetMapper().SetInputDataObject(flying_edges.GetOutputDataObject(0))

    # Update the view
    mesh.Modified()
    # render_window.Render()
    ctrl.view_update()


# UI setup
with SinglePageLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSpacer()
        html.Div("Contour: {{ contour_value }}")
        vuetify.VSpacer()
        vuetify.VSlider(
            v_model=('contour_value', default_contour),
            min=min_contour,
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
