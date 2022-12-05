import numpy as np
from PIL import ImageFont, ImageDraw, Image

def key(text, w=1):
    return {'t': text, 'w': w}
'''
keeb = [
    [key('Esc'), key('1'), key('2'), key('3'), key('4'), key('5'), key('6'), key('7'), key('8'), key('9'), key('0'), key('-'), key('='), key('Backspace', 2), key('Home')],
    [key('Tab', 1.5), key('Q'), key('W'), key('E'), key('R'), key('T'), key('Y'), key('U'), key('I'), key('O'), key('P'), key('['), key(']'), key('\\', 1.5), key('PgUp')],
    [key('Caps Lock', 1.75), key('A'), key('S'), key('D'), key('F'), key('G'), key('H'), key('J'), key('K'), key('L'), key(';'), key("'"), key('Enter', 2.25), key('PgDn')],
    [key('Shift', 2.25), key('Z'), key('X'), key('C'), key('V'), key('B'), key('N'), key('M'), key(','), key('.'), key('/'), key('Shift', 1.75), key('↑'), key('End')],
    [key('Ctrl', 1.25), key('Win', 1.25), key('Alt', 1.25), key('Space', 6.25), key('Alt'), key('Fn'), key('Ctrl'), key('←'), key('↓'), key('→')]
]
'''

keeb = [
    [key(''), key('1'), key('2'), key('3'), key('4'), key('5'), key('6'), key('7'), key('8'), key('9'), key('0'), key('-'), key('='), key('', 2), key('')],
    [key('', 1.5), key('Q'), key('W'), key('E'), key('R'), key('T'), key('Y'), key('U'), key('I'), key('O'), key('P'), key('['), key(']'), key('\\', 1.5), key('')],
    [key('', 1.75), key('A'), key('S'), key('D'), key('F'), key('G'), key('H'), key('J'), key('K'), key('L'), key(';'), key("'"), key('', 2.25), key('')],
    [key('', 2.25), key('Z'), key('X'), key('C'), key('V'), key('B'), key('N'), key('M'), key(','), key('.'), key('/'), key('', 1.75), key(''), key('')],
    [key('', 1.25), key('', 1.25), key('', 1.25), key('', 6.25), key(''), key(''), key(''), key(''), key(''), key('')]
] 

def draw_keeb(name, frameColor, keyColor, textColor, specialColor, keeb=keeb, height=580, width=1720, unit=100):

    def draw_key(image, key, x, y, w, h, color):
        x = int(x)
        y = int(y)
        text = key['t']
        color = specialColor if text == '' else color
        image[y:int(y+h), x:int(x+w)] = color
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype('Poppins-Regular.ttf', 20)
        textsize = font.getsize(text)
        textX = (w - textsize[0]) / 2
        textY = (h + textsize[1]) / 2
        draw.text((x+textX, y+textY), text, textColor, font=font, align='center')
        return np.array(img_pil)

    image = np.zeros((height, width, 3), np.uint8)
    image[:] = frameColor
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype('Poppins-Regular.ttf', 20)
    textsize = font.getsize(name)
    textX = (width - textsize[0]) / 2
    textY = height - 30
    draw.text((textX, textY), name, (255,255,255,255), font=font, align='center')
    image = np.array(img_pil)
    x = 30
    y = 30
    for row in keeb:
        gap = (width - x * 2 - unit * sum([key['w'] for key in row])) / (len(row) - 1)
        for key in row:
            w = unit * key['w']
            h = unit
            image = draw_key(image, key, x, y, w, h, keyColor)
            x += w + gap
            # draw gap
        x = 30
        y += unit + 5
    
    image = Image.fromarray(image)
    return image

def draw_heatmap(name, frameColor, keyColor, textColor, specialColor, htext, keeb=keeb, height=580, width=1720, unit=100):

    def draw_key(image, key, x, y, w, h, color):
        x = int(x)
        y = int(y)
        text = key['t']
        if text == '':
            color = specialColor
        elif text in htext:
            color = (255, 84, 84)
        image[y:int(y+h), x:int(x+w)] = color
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype('Poppins-Regular.ttf', 20)
        textsize = font.getsize(text)
        textX = (w - textsize[0]) / 2
        textY = (h + textsize[1]) / 2
        draw.text((x+textX, y+textY), text, textColor, font=font, align='center')
        return np.array(img_pil)

    image = np.zeros((height, width, 3), np.uint8)
    image[:] = frameColor
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype('Poppins-Regular.ttf', 20)
    textsize = font.getsize(name)
    textX = (width - textsize[0]) / 2
    textY = height - 30
    draw.text((textX, textY), name, (255,255,255,255), font=font, align='center')
    image = np.array(img_pil)
    x = 30
    y = 30
    for row in keeb:
        gap = (width - x * 2 - unit * sum([key['w'] for key in row])) / (len(row) - 1)
        for key in row:
            w = unit * key['w']
            h = unit
            image = draw_key(image, key, x, y, w, h, keyColor)
            x += w + gap
            # draw gap
        x = 30
        y += unit + 5
    
    image = Image.fromarray(image)
    return image

if __name__ == '__main__':
    img = draw_keeb('John Doe', (0, 0, 0), (214, 218, 217), (0, 0, 0), (160, 189, 195))
    img.save('keeb.png')
    heatmap = draw_heatmap('John Doe', (0, 0, 0), (214, 218, 217), (0, 0, 0), (160, 189, 195), "H34TKEYB0ARD")
    heatmap.save('heatmap.png')
