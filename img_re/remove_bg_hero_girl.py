
from rembg import remove
from PIL import Image

PURPLE_BG = (123, 44, 191)  # same purple as #7B2CBF

# Load image
img = Image.open("img_re/hero_girl.png").convert("RGBA")

# Remove background
no_bg = remove(img)

# Create purple background
purple_bg = Image.new("RGBA", no_bg.size, PURPLE_BG + (255,))

# Combine
final_img = Image.alpha_composite(purple_bg, no_bg)

# Save
final_img.save("img_re/hero_girl_purple.png")

print("✅ Hero girl background replaced with purple")
