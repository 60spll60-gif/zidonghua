"""
处理水晶图标：
1. 裁掉 Hunyuan 模型右下角的默认水印
2. 重新填充背景色恢复为 1024x1024
3. 生成多尺寸 favicon 套件
"""
from PIL import Image
import os

ICONS_DIR = r"D:\知识库\新建文件夹\知识库\部署站点\icons"
SRC = os.path.join(ICONS_DIR, "A_modern_minimalist_app_icon_d_2026-08-05T11-31-49.png")

img = Image.open(SRC).convert("RGBA")
w, h = img.size
print(f"原图尺寸: {w}x{h}")

# 策略：右下角水印大约在 (810..1024, 950..1024) 区域
# 整个底部最后 10% 是水印带，从 y = int(h*0.92) 开始是水印
# 更稳妥：直接裁掉底部 8% (从 y=920 开始)，然后用背景渐变色填充

# 1) 采样底部非水印区的颜色（在水晶下方，手部两侧的纯背景区）
# 从原图判断：底部 880-920 这一行，从 x=50..200 的区域是纯背景
bg_sample = img.crop((50, 880, 200, 920)).resize((1, 1)).getpixel((0, 0))
print(f"采样背景色: {bg_sample}")

# 2) 裁掉底部 8% 水印区域
crop_h = int(h * 0.92)  # 保留顶部 92%
cropped = img.crop((0, 0, w, crop_h))

# 3) 用背景色创建填充条
# 实际底部是渐变，我们用线性渐变从 bg_sample 渐变到 (更深的版本)
deep_bg = tuple(max(0, c - 8) for c in bg_sample[:3]) + (255,)
fill = Image.new("RGBA", (w, h - crop_h), deep_bg)

# 在填充条顶部做渐变过渡，让它和上面图片融合
# 简单做法：在填充条顶部 20 像素做线性 alpha 混合
from PIL import ImageDraw
overlay = Image.new("RGBA", (w, h - crop_h), (0, 0, 0, 0))
for y in range(h - crop_h):
    # alpha 从 0 (顶) 到 255 (底)
    if y < 20:
        a = int(255 * (y / 20))
    else:
        a = 255
    # 颜色从 bg_sample (顶) 渐变到 deep_bg (底)
    t = y / max(1, (h - crop_h - 1))
    r = int(bg_sample[0] * (1 - t) + deep_bg[0] * t)
    g = int(bg_sample[1] * (1 - t) + deep_bg[1] * t)
    b = int(bg_sample[2] * (1 - t) + deep_bg[2] * t)
    ImageDraw.Draw(overlay).line([(0, y), (w, y)], fill=(r, g, b, a))

# 4) 拼接
clean = Image.new("RGBA", (w, h), (0, 0, 0, 0))
clean.paste(cropped, (0, 0))
clean.paste(overlay, (0, crop_h), overlay)

# 5) 转换回 RGB（无透明通道，更通用）
clean_rgb = Image.new("RGB", (w, h), (10, 14, 30))
clean_rgb.paste(clean, mask=clean.split()[3])

# 6) 主图：保持 1024x1024 高清版
main_path = os.path.join(ICONS_DIR, "crystal-icon-1024.png")
clean_rgb.save(main_path, "PNG", optimize=True)
print(f"主图已保存: {main_path}")

# 7) 生成 favicon 套件
favicon_sizes = {
    "favicon-16.png": 16,
    "favicon-32.png": 32,
    "favicon-48.png": 48,
    "favicon-64.png": 64,
    "favicon-128.png": 128,
    "favicon-256.png": 256,
    "favicon-512.png": 512,
    "apple-touch-icon.png": 180,
}
for name, size in favicon_sizes.items():
    out = clean_rgb.resize((size, size), Image.LANCZOS)
    out.save(os.path.join(ICONS_DIR, name), "PNG", optimize=True)
    print(f"  - {name} ({size}x{size})")

# 8) 生成 .ico（多尺寸合一）
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
ico_path = os.path.join(ICONS_DIR, "favicon.ico")
clean_rgb.save(ico_path, format="ICO", sizes=ico_sizes)
print(f"favicon.ico 已保存: {ico_path}")

print("\n全部完成。")
