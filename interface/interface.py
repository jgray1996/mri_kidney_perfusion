import panel as pn
import numpy as np
import nrrd
from matplotlib.figure import Figure

LOGO = "https://pre-image.eu/wp-content/uploads/2019/12/PRE-IMAGE-logo-1-white-background-scaled.png"

pn.extension(sizing_mode="stretch_width")

# Load data
seq, _ = nrrd.read("/home/jgray/Documents/mri_kidney_perfusion/data/processed/nrrds/T1_30_140_exvivo_both.nrrd")
seg, _ = nrrd.read("/home/jgray/Documents/mri_kidney_perfusion/data/raw/segmentations/T1_30_140_exvivo_both.seg.nrrd")

# Saving parameters
rotations_flips = {"rot":-1,
                   "flip":True}

seg = np.rot90(seg, k=rotations_flips["rot"])
if rotations_flips["flip"]:
    seg = np.fliplr(seg)

# Initial figure and axes setup
fig = Figure(figsize=(8, 4))
axs = fig.subplots(1, 3)

threshold = seg.max() * .75
mask = np.zeros_like(seg[:, :, seq.shape[0]//3])
mask[seg[:, :, seq.shape[0]//3] > threshold] = 1

img0 = axs[0].imshow(mask)
axs[0].set_title("Segmentation mask")

img1 = axs[1].imshow(seq[seq.shape[0]//3], cmap='gray')
axs[1].set_title("MRI-scan")

img2 = axs[2].imshow(seg[:, :, seq.shape[0]//3], cmap='viridis', vmin=seg.min(), vmax=seg.max())
axs[2].set_title("Segmentation prediction")

# Wrap in panel pane
component = pn.pane.Matplotlib(fig, format='svg', sizing_mode='scale_both')

# Widgets
probability_slider = pn.widgets.FloatSlider(value=.75, start=0, step=.01, end=1, name="Probability cut-off")
volume_slice = pn.widgets.IntSlider(value=seq.shape[0]//3, start=0, end=seq.shape[0]-1, name="Slice volume")
flip_left = pn.widgets.Button(name="Flip left", button_type="primary")
flip_right = pn.widgets.Button(name="Flip right", button_type="primary")
mirror = pn.widgets.Button(name="Mirror", button_type="primary")
files = pn.widgets.FileSelector('../data', name="Select files...")
segfiles = pn.widgets.FileSelector('../data', name="Select files...")

# updater functions
def update_all(slice_index, cutoff):
    """Update all three images based on the current slice and cutoff."""
    img1.set_data(seq[slice_index])
    img2.set_data(seg[:, :, slice_index])
    
    threshold = seg.max() * cutoff
    mask = np.zeros_like(seg[:, :, slice_index])
    mask[seg[:, :, slice_index] > threshold] = 1
    img0.set_data(mask)
    component.param.trigger('object')
    print(rotations_flips)

def on_slice_change(event):
    update_all(event.new, probability_slider.value)

def on_cutoff_change(event):
    update_all(volume_slice.value, event.new)

def on_right_press(event):
    global seg, rotations_flips
    seg = np.rot90(seg, k=1)
    rotations_flips["rot"] += 1
    update_all(volume_slice.value, probability_slider.value)

def on_left_press(event):
    global seg, rotations_flips
    seg = np.rot90(seg, k=-1)
    rotations_flips["rot"] -= 1
    update_all(volume_slice.value, probability_slider.value)

def on_mirror_press(event):
    global seg, rotations_flips
    seg = np.fliplr(seg)
    if rotations_flips["flip"] == True:
        rotations_flips["flip"] = False
    else:
        rotations_flips["flip"] = True
    update_all(volume_slice.value, probability_slider.value)

def on_ud(value):
    global loaded_files
    loaded_files = files.value
    print(files.value)

loaded_files = []
# updates
volume_slice.param.watch(on_slice_change, 'value')
probability_slider.param.watch(on_cutoff_change, 'value')
flip_right.param.watch(on_right_press, 'value')
flip_left.param.watch(on_left_press, 'value')
mirror.param.watch(on_mirror_press, 'value')

files.param.watch(on_ud, 'value')


# Layout
pn.template.FastListTemplate(
    title="Probability cut-off utility",
    sidebar=[LOGO, probability_slider, pn.Row(flip_left, flip_right), mirror, volume_slice],
    main=pn.Tabs(pn.Column(pn.panel("# Select Sequences"),files, name="Sequences"),
                 pn.Column(pn.panel("# Select Segmentation"),files, name="Segmentations"), 
                 pn.Column(component, name="Edit"))
).servable()