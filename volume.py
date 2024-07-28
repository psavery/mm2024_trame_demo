import pyvista as pv
from scipy.ndimage import gaussian_filter
from trame.app import get_server
from trame.widgets import vuetify3 as vuetify, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout
from vtk.util import numpy_support as np_s
import sys

from data_loader import fetch_dataset

# Data loading
dataset = 'star_nanoparticle'
if len(sys.argv) > 1:
    dataset = sys.argv[1]

selected_dataset_path = fetch_dataset(dataset)

input_data = pv.read(selected_dataset_path)

pl = pv.Plotter()
volume = pl.add_volume(input_data, cmap='plasma', opacity='sigmoid_5')
data = volume.GetMapper().GetInput()
vtk_array = data.GetPointData().GetScalars()
np_data = np_s.vtk_to_numpy(vtk_array).reshape(data.GetDimensions())
original_data = np_data.copy()

render_window = pl.ren_win
render_window.OffScreenRenderingOn()

prop = volume.GetProperty()
prop.SetInterpolationTypeToLinear()

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
    # Reset to original data
    np_data[:] = original_data
    # Now apply the gaussian
    np_data[:] = gaussian_filter(np_data.transpose(2, 1, 0), sigma).transpose(2, 1, 0)

    # Update the view
    data.Modified()
    render_window.Render()
    ctrl.view_update()


with SinglePageLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VLabel('Sigma')
        vuetify.VSlider(
            v_model=('sigma', 0),
            min=0,
            max=2,
            step=0.01,
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
