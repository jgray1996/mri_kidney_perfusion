import panel as pn
import numpy as np
import nrrd
from matplotlib.figure import Figure
import pandas as pd
from io import StringIO

LOGO = "https://pre-image.eu/wp-content/uploads/2019/12/PRE-IMAGE-logo-1-white-background-scaled.png"

pn.extension(sizing_mode="stretch_width")
pn.extension('filedropper')

# Create plot placeholder
q_, g_ = None, None
seq = np.zeros((24, 128, 128, 1))
seg = np.zeros((128, 128, 24, 1))

n_scans = 0
batch = None

def load_seq(file):
    global seq, q_
    seq, q_ = nrrd.read(file)

def load_seg(file):
    global seg, g_
    seg, g_ = nrrd.read(file)

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
# image controls
probability_slider = pn.widgets.FloatSlider(value=.75, start=0, step=.01, end=1, name="Probability cut-off")
volume_slice = pn.widgets.IntSlider(value=seq.shape[0]//3, start=0, end=seq.shape[0]-1, name="Slice volume")
flip_left = pn.widgets.Button(name="Flip left", button_type="primary")
flip_right = pn.widgets.Button(name="Flip right", button_type="primary")
mirror = pn.widgets.Button(name="Mirror", button_type="primary")
int_range_slider = pn.widgets.IntRangeSlider(name='Volume slice scope',
    start=0, end=seq.shape[0], value=(0, seq.shape[0]), step=1)

# reading next and previous scans in buffer
load_prev = pn.widgets.Button(name="Previous scan", button_type="primary")
load_next = pn.widgets.Button(name="Next scan", button_type="primary")
file_dropper = pn.widgets.FileDropper(sizing_mode='stretch_both')
scan_number = pn.widgets.IntSlider(name="Index loaded scans", value=0, start=0, end=1)

# export files
output_dir_masks = pn.widgets.FileInput(name="Segmentation masks output", directory=True)
toggle_batch = pn.widgets.Toggle(name='Generate new batch file', button_type='success')
export = pn.widgets.Button(name="Render masks with current settings", button_type="primary")

# updater functions
def update_all(slice_index, cutoff):
    """Update all three images based on the current slice and cutoff."""
    try:
        # Ensure slice_index is within bounds
        slice_index = max(0, min(slice_index, seq.shape[0]-1))
        
        # Update MRI scan image
        img1.set_data(seq[slice_index])
        img1.set_clim(vmin=seq.min(), vmax=seq.max())
        
        # Update segmentation prediction image
        img2.set_data(seg[:, :, slice_index])
        img2.set_clim(vmin=seg.min(), vmax=seg.max())
        
        # Update mask image
        threshold = seg.max() * cutoff
        mask = np.zeros_like(seg[:, :, slice_index])
        mask[seg[:, :, slice_index] > threshold] = 1
        img0.set_data(mask)
        img0.set_clim(vmin=0, vmax=1)
        
        # Force matplotlib to redraw
        component.param.trigger('object')
        
    except Exception as e:
        print(f"Error updating plots: {e}")

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

def load_images(seq_file, seg_file):
    global seq, seg, rotations_flips
    try:
        # Load the files
        seq, q_ = nrrd.read(seq_file)
        seg, g_ = nrrd.read(seg_file)
        
        # Store current slice position as ratio to preserve relative position
        current_slice_ratio = volume_slice.value / max(1, volume_slice.end) if volume_slice.end > 0 else 0.5
        
        # Apply current rotations and flips (don't reset them)
        seg = np.rot90(seg, k=rotations_flips["rot"])
        if rotations_flips["flip"]:
            seg = np.fliplr(seg)
        
        # Update volume slice widget limits and preserve relative position
        new_slice_value = int(current_slice_ratio * (seq.shape[0] - 1))
        volume_slice.param.update(start=0, end=seq.shape[0]-1, value=new_slice_value)
        # int_range_slider.param.update(start=0, end=seq.shape[0], value=(0, seq.shape[0]))
        
        # Update the plot
        update_all(volume_slice.value, probability_slider.value)
        
        print(f"Loaded images: seq shape {seq.shape}, seg shape {seg.shape}")
        print(f"Applied rotations: {rotations_flips['rot']}, flipped: {rotations_flips['flip']}")
        
    except Exception as e:
        print(f"Error loading images {seq_file}, {seg_file}: {e}")

def batch_read(event):
    global batch, n_scans, scan_number
    if file_dropper.value and "batch.csv" in file_dropper.value:
        try:
            batch = pd.read_csv(StringIO(file_dropper.value["batch.csv"]))
            n_scans = len(batch)
            
            # Update scan_number widget - ensure end is always > start
            if n_scans > 0:
                scan_number.param.update(start=0, end=n_scans-1, value=0)
                # Load the first scan
                load_images(batch.Image[0], batch.Mask[0])
            else:
                # No scans in batch - keep end > start to avoid error
                scan_number.param.update(start=0, end=1, value=0)
            
            print(f"Loaded batch with {n_scans} scans")
        except Exception as e:
            print(f"Error loading batch file: {e}")
    else:
        batch = None
        n_scans = 0
        # Keep end > start to avoid slider error
        scan_number.param.update(start=0, end=1, value=0)

def on_scan_number_change(event):
    """Load scan when scan_number changes"""
    global batch, n_scans
    if batch is not None and 0 <= event.new < n_scans:
        load_images(batch.Image[event.new], batch.Mask[event.new])

def prev_scan(event):
    global scan_number
    if scan_number.value > 0:
        scan_number.value -= 1

def next_scan(event):
    global scan_number, n_scans
    if scan_number.value < n_scans - 1:
        scan_number.value += 1

# Watch for parameter changes
volume_slice.param.watch(on_slice_change, 'value')
probability_slider.param.watch(on_cutoff_change, 'value')
flip_right.param.watch(on_right_press, 'clicks')
flip_left.param.watch(on_left_press, 'clicks')
mirror.param.watch(on_mirror_press, 'clicks')

file_dropper.param.watch(batch_read, 'value')
scan_number.param.watch(on_scan_number_change, 'value')
load_prev.param.watch(prev_scan, 'clicks')
load_next.param.watch(next_scan, 'clicks')

# Layout
pn.template.FastListTemplate(
    title="Probability cut-off utility",
    sidebar=[LOGO, probability_slider, pn.Row(flip_left, flip_right), mirror, volume_slice, int_range_slider],
    main=pn.Tabs(pn.Column(pn.panel("# Import Batch file"), file_dropper, name="Batch file"),
                 pn.Column(pn.panel("# Preview of current settings"), 
                           pn.Row(load_prev, load_next), scan_number, component, name="Preview"),
                 pn.Column(pn.panel("""# Export Settings  
                                    Select an output directory for exported masks"""),
                           pn.Row(pn.Column(output_dir_masks, toggle_batch, export)
                                  ), name="Export"))
).servable()