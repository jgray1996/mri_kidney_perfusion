import panel as pn
import nrrd 
import os 
import numpy as np
import holoviews as hv
import hvplot.pandas
from holoviews import opts
from pathlib import Path
from os import mkdir

# extension loading
pn.extension(sizing_mode="stretch_width")
pn.extension('bokeh')
hv.extension('bokeh')

# global params
sequences=[]
proba=[]

# remote resources
LOGO = "https://pre-image.eu/wp-content/uploads/2019/12/PRE-IMAGE-logo-1-white-background-scaled.png"

#############################################
# 1.1 Select sequences
#############################################
sequences_directory = pn.widgets.FileSelector(
    "~/Documents/Code/mri_kidney_perfusion/unet_unlabeled/",
    file_pattern="*.nrrd",
    name="Select sequence directory"
)

# 1.2 Select probabilities
proba_directory = pn.widgets.FileSelector(
    "~/Documents/Code/mri_kidney_perfusion/unet_unlabeled/",
    file_pattern="*.nrrd",
    name="Select probability directory"
)

# 1.3 Formate file selectors in a Column
def create_file_selectors():
    # 1.2 place in two columns
    directory_selector_cols = pn.Column(
        pn.pane.Markdown("## Select sequence files..."),
        pn.layout.Divider(),
        sequences_directory,
        pn.layout.Divider(),
        pn.pane.Markdown("## Select probability files..."),
        pn.layout.Divider(),
        proba_directory,
        pn.layout.Divider()
    )
    return directory_selector_cols

# 1.4 Create display panes to show the selected paths
sequences_display = pn.pane.Markdown("No sequences selected yet.")
proba_display = pn.pane.Markdown("No probabilities selected yet.")

# 1.5 Define functions that update based on each FileSelector's value
@pn.depends(sequences_directory.param.value, watch=True)
def update_sequences_display(selected_paths):
    global sequences
    sequences = []
    if selected_paths:
        sequences_display.object = f"Selected sequences: **{len(selected_paths)}**"
        for path in selected_paths:
            sequences.append(nrrd.read(path)[0])
        slider_z_axis.end = sequences[0].shape[2] - 1
        file_slider.end = len(sequences) - 1
        
    else:
        sequences_display.object = "No sequences selected yet."

@pn.depends(proba_directory.param.value, watch=True)
def update_proba_display(selected_paths):
    global proba
    proba = []
    if selected_paths:
        proba_display.object = f"Selected probabilities: **{len(selected_paths)}**"
        for path in selected_paths:
            proba.append(nrrd.read(path)[0])
    else:
        proba_display.object = "No probability selected yet."

#############################################
# 2.1 preview the sequences
#############################################
plot1 = pn.pane.HoloViews(hv.Image(np.random.rand(100, 150)), width=600, height=600)

# 2.2 cut-off control
slider_z_axis = pn.widgets.IntSlider(value=0, start=0, end=0, step=1, name="z axis slider")
file_slider = pn.widgets.IntSlider(value=0, start=0, end=0, step=1, name="File loaded")
probability_slider = pn.widgets.FloatSlider(value=0.9, start=0, end=1, step=0.01, name="Probability cut-off slider")

# 2.3 plot updating
@pn.depends(slider_z_axis.param.value,
            file_slider.param.value,
            probability_slider.param.value,
            proba_directory.param.value,
            watch=True)
def update_visualization(slider_z_axis, file_slider, probability_slider, files):
    if sequences and proba:
        loaded_proba = proba[file_slider][slider_z_axis]
        mask = np.zeros_like(loaded_proba)
        mask[loaded_proba > probability_slider] = 1
        mask = hv.Image(mask).opts(title="Generated Mask")
        plot1.object = hv.Image(sequences[file_slider][...,slider_z_axis]).opts(title="MRI Sequence") + mask
    else:
        plot1.object = hv.Image(np.random.rand(100, 100)).opts(title="changed parameter")

update_visualization(slider_z_axis.value, file_slider.value, probability_slider.value, None)

#############################################
# 3.1 export
#############################################
export_button = pn.widgets.Button(name="Export")

# 3.2 monitor function
@pn.depends(export_button.param.value, watch=True)
def export_masks(par):
    if proba_directory.value:
        for file in proba_directory.value:
            data, _ = nrrd.read(file)
            mask = np.zeros_like(data)
            mask[data > probability_slider.value] = 1
            mask = mask.squeeze(axis=-1).transpose(1, 2, 0)
            print(mask.shape)

            base_folder = Path(file).parent.parent
            name = Path(file).name
            output_folder = base_folder/Path("mask")
            output_folder.mkdir(exist_ok=True)
            nrrd.write(str(output_folder/name), mask)

#############################################
# Build tabs for eacht widget
# serving of widgets and items
pn.template.FastListTemplate(
    title="Probability cut-off utility",
    sidebar=[
        LOGO,
        sequences_display,
        proba_display,
        slider_z_axis,
        file_slider,
        probability_slider
        ],
    main=[
        pn.Tabs(
            ("files", create_file_selectors()),
            ("preview", plot1),
            ("export", export_button)
            )
    ]
).servable()