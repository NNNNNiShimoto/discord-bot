from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np
import random

FONT_PATH = "/usr/your/font/path/ver1"
FONT_PATH2 = "/usr/your/font/path/ver2"

COLOR_CONFIG = [
    {
        #basic
        'baseColor': (255, 255, 255),
        'lineColor': 200,
        'fontColor': (0, 0, 0),
        'fontPath': FONT_PATH,
        'colorList': [
            (255, 0, 0),      #red
            (0, 0, 255),      #blue
            (0, 128, 0),      #green
            (255, 215, 0),    #yellow
            (128, 0, 128),    #purple
            (0, 192, 192),    #sky
            (255, 153, 0),    #orange
            (128, 128, 128),  #gray
            (0, 0, 128)       #navy
        ],
    },
    {
        #you can add another color
        'baseColor': (0, 115, 86),
        'lineColor': 255,
        'fontColor': (255, 255, 255),
        'fontPath': FONT_PATH2,
        'colorList': [
            (255, 255, 255)
        ],
    }
]

def bound (i :int):
    if i > 50: return 50
    elif i < 10: return 10
    else: return i

def createAmida(name_list :list, hit_num :int, color_config: int):
    if abs(hit_num) > len(name_list) or hit_num == 0:
        return 1
    
    #if hit_num is minus, print number on picture instead of star.
    is_print_number = hit_num<0
    hit_num = abs(hit_num)
    
    img_height=1200
    img_width=1200

    thickness=5

    horizon_bar_num=4*len(name_list)-2
    vertical_bar_num=len(name_list)
    holizon_bar_width=int((img_height-400)/horizon_bar_num)
    vertical_bar_height=int(img_width/vertical_bar_num)
    
    #holizon bar moves randomly between -holizon_delta_max and +holizon_delta_max
    horizon_delta_max = int((holizon_bar_width-2*thickness)/2)

    base_img=Image.new("RGB",(img_width+vertical_bar_height,img_height), COLOR_CONFIG[color_config]['baseColor'])
    base_img=np.array(base_img)

    #draw lines
    for i in range(vertical_bar_num):
        base_img[
            120:1080,
            (i+1)*vertical_bar_height-thickness:(i+1)*vertical_bar_height+thickness
        ] = COLOR_CONFIG[color_config]['lineColor']

    for i in range(horizon_bar_num):
        pos=np.random.randint(1,vertical_bar_num)
        dt = np.random.randint(-horizon_delta_max, horizon_delta_max)
        base_img[
            200+dt+int((i+1)*holizon_bar_width-thickness):200+dt+int((i+1)*holizon_bar_width+thickness), #width
            pos*vertical_bar_height:(pos+1)*vertical_bar_height #height
        ] = COLOR_CONFIG[color_config]['lineColor']

    base_img=Image.fromarray(base_img)

    #draw letters
    font_size=50
    font_path=COLOR_CONFIG[color_config]['fontPath']
    font_namesize_list = [ ImageFont.truetype(font_path, bound(vertical_bar_height//len(item))) for item in name_list ]
    font_mark = ImageFont.truetype(font_path, font_size) 

    for i in range(vertical_bar_num):
        vfsize = bound(vertical_bar_height//len(name_list[i]))
        ImageDraw.Draw(base_img).text((
            (i+1)*vertical_bar_height - vfsize*len(name_list[i])/2, 100-vfsize), 
            name_list[i], 
            font = font_namesize_list[i], 
            fill = COLOR_CONFIG[color_config]['fontColor'])
    
    winners_list = random.sample(range(len(name_list)),hit_num)
    color_list = COLOR_CONFIG[color_config]['colorList']
    if is_print_number:
        for i in range(hit_num):
            ImageDraw.Draw(base_img).text(
                ((winners_list[i]+1)*vertical_bar_height-17, img_height-100), 
                str(i+1), 
                font = font_mark, 
                fill = color_list[i%len(color_list)]
            )
    else:
        color_list = random.sample(color_list, hit_num)
        for i in range(hit_num):    
            ImageDraw.Draw(base_img).text(
                ((winners_list[i]+1)*vertical_bar_height-25, img_height-90), 
                "★", 
                font = font_mark, 
                fill = color_list[i]
            )
    
    #save image
    base_img.save('./img/dynamic/amida.jpg', quality=85)

    return 0
