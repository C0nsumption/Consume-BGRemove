# bg_remover.py

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import cv2
import logging

def convert_image_simple(img, red_threshold, green_threshold, blue_threshold, tolerance=30, blur_radius=2):
    logging.info('Starting simple background removal process...')
    try:
        img = img.convert("RGBA")
        data = np.array(img)

        logging.debug(f"Image shape: {data.shape}")
        logging.debug(f"Thresholds: R={red_threshold}, G={green_threshold}, B={blue_threshold}")
        logging.debug(f"Tolerance: {tolerance}, Blur radius: {blur_radius}")

        # Create a mask for background pixels
        r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        
        # Adjust mask creation for dark colors
        if max(red_threshold, green_threshold, blue_threshold) < tolerance:
            # For very dark colors, we invert the logic
            mask = ((r <= red_threshold + tolerance) & 
                    (g <= green_threshold + tolerance) & 
                    (b <= blue_threshold + tolerance))
        else:
            mask = ((r >= max(red_threshold - tolerance, 0)) & 
                    (g >= max(green_threshold - tolerance, 0)) & 
                    (b >= max(blue_threshold - tolerance, 0)))

        logging.debug(f"Mask shape: {mask.shape}, Dtype: {mask.dtype}")

        # Apply Gaussian blur to smooth the edges
        mask = gaussian_filter(mask.astype(float), sigma=blur_radius)

        logging.debug(f"Blurred mask shape: {mask.shape}, Dtype: {mask.dtype}")

        # Update alpha channel
        data[:,:,3] = (1 - mask) * 255

        # Create new image
        new_img = Image.fromarray(data)
        logging.info('Simple background removal completed successfully.')
        return new_img

    except Exception as e:
        logging.error(f"Error in convert_image_simple: {str(e)}")
        raise

def convert_image_advanced(img, red_threshold, green_threshold, blue_threshold, tolerance=30, blur_radius=2):
    logging.info('Starting advanced background removal process...')
    try:
        img = img.convert("RGBA")
        data = np.array(img)

        logging.debug(f"Image shape: {data.shape}")
        logging.debug(f"Thresholds: R={red_threshold}, G={green_threshold}, B={blue_threshold}")
        logging.debug(f"Tolerance: {tolerance}, Blur radius: {blur_radius}")

        # Convert to LAB color space
        lab_image = cv2.cvtColor(data[:,:,:3], cv2.COLOR_RGB2LAB)

        # Create a mask for background pixels using LAB color space
        l, a, b = cv2.split(lab_image)
        
        # Adjust mask creation for dark colors
        if max(red_threshold, green_threshold, blue_threshold) < tolerance:
            # For very dark colors, we invert the logic
            mask = (
                (l <= red_threshold + tolerance) & 
                (a <= green_threshold + tolerance) & 
                (b <= blue_threshold + tolerance)
            )
        else:
            mask = (
                (l >= max(red_threshold - tolerance, 0)) & 
                (a >= max(green_threshold - tolerance, 0)) & 
                (b >= max(blue_threshold - tolerance, 0))
            )

        # Apply edge detection
        edges = cv2.Canny(data[:,:,:3], 100, 200)
        mask = mask & (edges == 0)

        logging.debug(f"Mask shape: {mask.shape}, Dtype: {mask.dtype}")

        # Apply Gaussian blur to smooth the edges
        mask = gaussian_filter(mask.astype(float), sigma=blur_radius)

        # Adaptive thresholding
        mask = cv2.adaptiveThreshold(
            (mask * 255).astype(np.uint8),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        mask = mask.astype(float) / 255.0

        logging.debug(f"Final mask shape: {mask.shape}, Dtype: {mask.dtype}")

        # Update alpha channel
        data[:,:,3] = (1 - mask) * 255

        # Create new image
        new_img = Image.fromarray(data)
        logging.info('Advanced background removal completed successfully.')
        return new_img

    except Exception as e:
        logging.error(f"Error in convert_image_advanced: {str(e)}")
        raise

def refine_edges(img, iterations=3):
    """Refine the edges of the image using morphological operations."""
    alpha = np.array(img)[:,:,3]
    kernel = np.ones((3,3), np.uint8)
    refined_alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel, iterations=iterations)
    refined_alpha = cv2.morphologyEx(refined_alpha, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    img_array = np.array(img)
    img_array[:,:,3] = refined_alpha
    return Image.fromarray(img_array)

def remove_background(img, red_threshold, green_threshold, blue_threshold, tolerance=30, blur_radius=2, mode='simple', refine=False):
    if mode == 'simple':
        result = convert_image_simple(img, red_threshold, green_threshold, blue_threshold, tolerance, blur_radius)
    elif mode == 'advanced':
        result = convert_image_advanced(img, red_threshold, green_threshold, blue_threshold, tolerance, blur_radius)
    else:
        raise ValueError("Invalid mode. Choose 'simple' or 'advanced'.")
    
    if refine:
        result = refine_edges(result)
    
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        test_image = Image.open("test_image.png")
        
        # Simple mode
        result_simple = remove_background(test_image, 250, 250, 250, mode='simple')
        result_simple.save("result_simple.png")
        
        # Advanced mode
        result_advanced = remove_background(test_image, 250, 250, 250, mode='advanced', refine=True)
        result_advanced.save("result_advanced.png")
        
        logging.info("Test images processed and saved successfully.")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")