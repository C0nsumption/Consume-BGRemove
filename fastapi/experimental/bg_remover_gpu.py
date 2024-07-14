import torch
from torchvision import transforms
from torchvision.transforms import functional as F
from PIL import Image

def remove_background_gpu(img, red_threshold, green_threshold, blue_threshold, tolerance=30, blur_radius=2, mode='simple'):
    # Convert PIL Image to PyTorch tensor
    to_tensor = transforms.ToTensor()
    img_tensor = to_tensor(img.convert("RGB")).unsqueeze(0).cuda()  # Move to GPU and convert to RGB

    # Create color threshold tensor
    color_threshold = torch.tensor([red_threshold, green_threshold, blue_threshold]).cuda() / 255.0

    # Create mask
    if mode == 'simple':
        mask = torch.all(torch.abs(img_tensor - color_threshold.view(1, 3, 1, 1)) <= (tolerance / 255.0), dim=1)
    else:  # advanced mode
        # Convert to LAB color space (approximation)
        rgb_to_lab = torch.tensor([
            [0.4124, 0.3576, 0.1805],
            [0.2126, 0.7152, 0.0722],
            [0.0193, 0.1192, 0.9505]
        ]).cuda()
        lab_tensor = torch.matmul(img_tensor.squeeze(0).permute(1, 2, 0), rgb_to_lab.t()).unsqueeze(0)
        
        # Create mask in LAB space
        lab_threshold = torch.matmul(color_threshold, rgb_to_lab.t())
        mask = torch.all(torch.abs(lab_tensor - lab_threshold.view(1, 3, 1, 1)) <= (tolerance / 255.0), dim=1)

    # Apply Gaussian blur
    mask = mask.float().unsqueeze(1)
    kernel_size = int(blur_radius * 2)
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure kernel_size is odd
    blurred_mask = F.gaussian_blur(mask, kernel_size=[kernel_size, kernel_size])

    # Apply mask to image
    result = img_tensor * (1 - blurred_mask) + blurred_mask

    # Convert back to PIL Image
    to_pil = transforms.ToPILImage()
    return to_pil(result.squeeze(0).cpu())

# Usage
if __name__ == "__main__":
    img = Image.open("test_image.png").convert("RGBA")
    result = remove_background_gpu(img, 250, 250, 250, mode='simple')
    result.save("result_gpu.png")
