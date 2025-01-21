

import os
import numpy as np
import SimpleITK as sitk
from PIL import Image
from mayavi import mlab
from scipy.ndimage import zoom
from skimage import measure

# Function to load images from a folder
def load_images_from_folder(folder, target_shape=None):
    images = []
    print(f"Loading images from: {folder}")
    try:
        for filename in sorted(os.listdir(folder)):  
            if filename.endswith(".png"):
                img = Image.open(os.path.join(folder, filename)).convert('L')
                img_array = np.array(img)
                if target_shape:
                    scale_factors = [t / s for t, s in zip(target_shape, img_array.shape)]
                    img_array = zoom(img_array, scale_factors, order=1)
                images.append(img_array)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    return np.array(images)

# Function to register images
def register_image(fixed_volume, moving_volume):
    fixed_image = sitk.GetImageFromArray(fixed_volume.astype(np.float32))
    moving_image = sitk.GetImageFromArray(moving_volume.astype(np.float32))
    print("Registering volumes...")

    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation()
    initial_transform = sitk.CenteredTransformInitializer(
        fixed_image, moving_image, sitk.AffineTransform(3),
        sitk.CenteredTransformInitializerFilter.GEOMETRY
    )
    registration_method.SetInitialTransform(initial_transform)
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100)
    registration_method.SetInterpolator(sitk.sitkLinear)
    final_transform = registration_method.Execute(fixed_image, moving_image)
    resampled_moving_image = sitk.Resample(moving_image, fixed_image, final_transform,
                                           sitk.sitkLinear, 0.0, moving_image.GetPixelID())
    return sitk.GetArrayFromImage(resampled_moving_image)

# Function to visualize the full 3D volume
def visualize_volume(volume, title):
    mlab.figure(title, size=(800, 800))
    src = mlab.pipeline.scalar_field(volume)
    mlab.pipeline.volume(src)  # Render as a volumetric field
    mlab.show()

# Function to resample volume
def resample_volume(volume, target_shape):
    scale_factors = [t / v for t, v in zip(target_shape, volume.shape)]
    resampled = zoom(volume, scale_factors, order=1)
    print(f"Resampled Volume Shape: {resampled.shape}")
    return resampled

# Function to fuse volumes
def fuse_volumes(axial_volume, sagittal_volume, coronal_volume):
    fused_volume = (axial_volume + sagittal_volume + coronal_volume) / 3.0
    print(f"Fused Volume Shape: {fused_volume.shape}")
    return fused_volume

# Function to extract surface
def extract_surface(volume, threshold=0.5):
    vertices, faces, normals, _ = measure.marching_cubes(volume, level=threshold)
    print(f"Extracted Surface: {len(vertices)} vertices and {len(faces)} faces.")
    return vertices, faces

# Function to visualize the 3D surface
def visualize_3d_surface(vertices, faces):
    mlab.figure(size=(800, 800))
    mlab.triangular_mesh(vertices[:, 0], vertices[:, 1], vertices[:, 2], faces)
    mlab.show()

# Main execution block
if __name__ == "__main__":
    axial_folder = r"D:\3D\MRI\DATASET\AXIAL"
    coronal_folder = r"D:\3D\MRI\DATASET\CORONAL"
    sagittal_folder = r"D:\3D\MRI\DATASET\SAGITTAL"

    target_shape = (256, 256, 256)  # Target shape for downsampling

    # Load and downsample images
    axial_volume = load_images_from_folder(axial_folder, target_shape)
    coronal_volume = load_images_from_folder(coronal_folder, target_shape)
    sagittal_volume = load_images_from_folder(sagittal_folder, target_shape)

    print("Axial volume shape:", axial_volume.shape)
    print("Coronal volume shape:", coronal_volume.shape)
    print("Sagittal volume shape:", sagittal_volume.shape)

    # Check if sagittal_volume is loaded
    if sagittal_volume.shape[0] == 0:
        print("Warning: Sagittal volume is empty. Skipping registration for sagittal images.")
        registered_sagittal = None
    else:
        registered_sagittal = register_image(axial_volume, sagittal_volume)

    registered_coronal = register_image(axial_volume, coronal_volume)

    if registered_sagittal is not None:
        visualize_volume(registered_sagittal, "Registered Sagittal Volume")
    visualize_volume(registered_coronal, "Registered Coronal Volume")

    # Resample each volume
    target_shape_resample = (512, 512, 512)
    axial_resampled = resample_volume(axial_volume, target_shape_resample)
    sagittal_resampled = resample_volume(registered_sagittal, target_shape_resample) if registered_sagittal is not None else np.zeros(target_shape_resample)
    coronal_resampled = resample_volume(registered_coronal, target_shape_resample)

    # Fuse the volumes
    fused_volume = fuse_volumes(axial_resampled, sagittal_resampled, coronal_resampled)

    # Extract and visualize the surface
    vertices, faces = extract_surface(fused_volume, threshold=0.5)
    visualize_3d_surface(vertices, faces)
