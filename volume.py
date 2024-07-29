import pyvista as pv
from scipy.ndimage import gaussian_filter
from trame.app import get_server
from trame.widgets import html, vuetify3 as vuetify, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout
from vtk.util import numpy_support as np_s
import sys

from data_loader import fetch_dataset

# Data loading
dataset = 'star_nanoparticle'
if len(sys.argv) > 1:
    dataset = sys.argv[1]

selected_dataset_path = fetch_dataset(dataset)

if dataset == 'star_nanoparticle':
    opacity = 'sigmoid_5'
else:
    opacity = [0, 0.06, 0.3, 0.5, 1]

# Read the file
input_data = pv.read(selected_dataset_path)

# Set up the VTK volume rendering
pl = pv.Plotter()
volume = pl.add_volume(input_data, cmap='plasma', opacity=opacity)
data = volume.GetMapper().GetInput()
vtk_array = data.GetPointData().GetScalars()
np_data = np_s.vtk_to_numpy(vtk_array).reshape(data.GetDimensions())
original_data = np_data.copy()

# Turn on offscreen rendering
render_window = pl.ren_win
render_window.OffScreenRenderingOn()

# Set linear interpolation
prop = volume.GetProperty()
prop.SetInterpolationTypeToLinear()

# Enable jittering
mapper = volume.GetMapper()
mapper.UseJitteringOn()

# Trame initialization
server = get_server()
state = server.state
ctrl = server.controller
state.trame__title == 'Example Volume Rendering'


# UI Callbacks
@state.change('sigma')
def sigma_changed(sigma, **kwargs):
    # Now apply the gaussian to the original data
    # Reshape to C ordering, since scipy expects that
    shape = np_data.shape
    np_data[:] = gaussian_filter(
        original_data.reshape(shape[::-1]),
        sigma,
    ).reshape(shape)

    # Update the view
    data.Modified()
    ctrl.view_update()


# Set up the UI layout
with SinglePageLayout(server) as layout:
    with layout.toolbar:
        html.Div("Sigma: {{ sigma }}")
        vuetify.VSpacer()
        vuetify.VSlider(
            v_model=('sigma', 0),
            min=0,
            max=10,
            step=0.05,
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
