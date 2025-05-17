from PIL import Image, ImageDraw
import os

# Create test directory if it doesn't exist
os.makedirs("test_images", exist_ok=True)

# Create a few test images with different sizes and formats
def create_test_image(filename, width, height, format="JPEG"):
    # Create a new image with a solid color
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    
    # Draw some shapes on the image
    draw = ImageDraw.Draw(img)
    draw.rectangle([(width//4, height//4), (width*3//4, height*3//4)], fill=(255, 255, 255))
    draw.ellipse([(width//3, height//3), (width*2//3, height*2//3)], fill=(255, 0, 0))
    
    # Save the image
    img.save(f"test_images/{filename}", format=format)
    print(f"Created {filename} ({width}x{height})")

# Create JPEG images
create_test_image("test_large.jpg", 3000, 2000)
create_test_image("test_medium.jpg", 1500, 1000)
create_test_image("test_small.jpg", 800, 600)

# Create PNG images
create_test_image("test_large.png", 3000, 2000, "PNG")
create_test_image("test_medium.png", 1500, 1000, "PNG")

# Create WebP images
create_test_image("test_large.webp", 3000, 2000, "WEBP")

# Create an image with non-ASCII filename
create_test_image("测试图片.jpg", 1200, 800)
create_test_image("テスト画像.png", 1200, 800, "PNG")

print("Test images created successfully!")
