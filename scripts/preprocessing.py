import SimpleITK as sitk
import os

def preprocess_mri_pipeline(input_dir: str, output_dir: str, reference_image_path: str):
    """
    Applies N4 bias field correction and histogram matching to a directory of MRI scans.

    Args:
        input_dir (str): The directory containing the MRI scans to be processed.
        output_dir (str): The directory where the processed scans will be saved.
        reference_image_path (str): The path to the reference MRI scan for histogram matching.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Loading reference image from: {reference_image_path}")
    reference_image = sitk.ReadImage(reference_image_path, sitk.sitkFloat32)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        if os.path.isfile(input_path) and filename.endswith(".nrrd"):
            print(f"\nProcessing: {filename}")

            # Load the Input Image
            input_image = sitk.ReadImage(input_path, sitk.sitkFloat32)

            # N4 Bias Field Correction
            print("Applying N4 bias field correction...")
            mask_image = sitk.OtsuThreshold(input_image, 0, 1, 200)
            corrector = sitk.N4BiasFieldCorrectionImageFilter()
            corrected_image = corrector.Execute(input_image, mask_image)

            # Histogram Matching
            print("Applying histogram matching...")
            matcher = sitk.HistogramMatchingImageFilter()
            matcher.SetNumberOfHistogramLevels(1024)
            matcher.SetNumberOfMatchPoints(7)
            matcher.ThresholdAtMeanIntensityOn()
            
            # The reference_image is now passed directly to Execute
            matched_image = matcher.Execute(corrected_image, reference_image)

            print("Rescaling intensities to [0, 1]...")
            rescaler = sitk.RescaleIntensityImageFilter()
            rescaler.SetOutputMinimum(0.0)
            rescaler.SetOutputMaximum(1.0)
            scaled_image = rescaler.Execute(matched_image)

            # Save the Processed Image
            print(f"Saving processed image to: {output_path}")
            sitk.WriteImage(scaled_image, output_path)

    print("\n--- Preprocessing complete for all images. ---")


preprocess_mri_pipeline("../unet_unlabeled/Dataset001_T1/imagesRd", 
                    "../unet_unlabeled/Dataset001_T1/imagesPr",
                    "../unet_training/Dataset001_T1/imagesTr/T1_000_0000.nrrd")

preprocess_mri_pipeline("../unet_unlabeled/Dataset002_T2/imagesRd", 
                    "../unet_unlabeled/Dataset002_T2/imagesPr",
                    "../unet_training/Dataset002_T2/imagesTr/T2_000_0000.nrrd")

preprocess_mri_pipeline("../unet_unlabeled/Dataset003_T2star/imagesRd", 
                    "../unet_unlabeled/Dataset003_T2star/imagesPr",
                    "../unet_training/Dataset003_T2star/imagesTr/T2star_000_0000.nrrd")

preprocess_mri_pipeline("../unet_unlabeled/Dataset004_ASL/imagesRd", 
                    "../unet_unlabeled/Dataset004_ASL/imagesPr",
                    "../unet_training/Dataset004_ASL/imagesTr/ASL_000_0000.nrrd")

preprocess_mri_pipeline("../unet_unlabeled/Dataset005_DWI/imagesRd", 
                    "../unet_unlabeled/Dataset005_DWI/imagesPr",
                    "../unet_training/Dataset005_DWI/imagesTr/DWI_000_0000.nrrd")
