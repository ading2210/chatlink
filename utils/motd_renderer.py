from io import BytesIO
import os, base64, random, json, re, socket
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from utils import ping, extractor

class MCFont:
    def __init__(self, path):
        self.init_font(path)
        self.path = path

    #load fonts as PIL image objects
    def init_font(self, path):
        f_default = open(path+"/assets/minecraft/font/default.json")
        self.default_json = json.loads(f_default.read())
        f_default.close()
        
        self.textures = {}
        for provider in self.default_json["providers"]:
            if "file" in provider and provider["file"] == "minecraft:font/accented.png":
                continue
            #only supports bitmap fonts for now
            if provider["type"] == "bitmap":
                texture_path = path+"/assets/minecraft/textures/"+provider["file"].replace("minecraft:", "", 1)
                self.textures[provider["file"]] = Image.open(texture_path)
            elif provider["type"] == "legacy_unicode":
                sizes_path = texture_path = path+"/assets/minecraft/"+provider["sizes"].replace("minecraft:", "", 1)
                template_path = path+"/assets/minecraft/textures/"+provider["template"].replace("minecraft:", "", 1)
                font_dir = path+"/assets/minecraft/textures/font/"

                pattern = re.compile(r"^unicode_page_..\.png$")
                files = os.listdir(font_dir)
                for file in files:
                    if not pattern.match(file):
                        continue

                    page = file.replace(".png", "", 1).replace("unicode_page_", "", 1)
                    self.textures[page] = Image.open(font_dir+file)
                
                f = open(sizes_path, "rb")
                self.sizes = f.read()
                f.close()

    #checks to see if a character needs to be rendered as unicode
    def is_unicode(self, char):
        for provider in self.default_json["providers"]:
            if not provider["type"] == "bitmap":
                continue
            #todo: implement binary search
            for i in range(0, len(provider["chars"])):
                if char in provider["chars"][i]:
                    if "file" in provider and provider["file"] == "minecraft:font/accented.png":
                        continue
                    return False
        return True

    #gets a random unicode character with a specific width
    def get_random_char(self, size=10):
        while True:
            rand = random.randint(0, 65535)
            size_byte = self.sizes[rand]
            start = size_byte >> 4
            end = size_byte & 0x0f
            diff = end-start
            if diff == size:
                return chr(rand)

    #check to see if a character is an emoji
    def is_emoji(self, char):
        regex = "^[☀-➿]$"
        return bool(re.match(regex, char))

    #extract a character from the mc font textures
    #returns a PIL image object
    def get_char(self, char=None, color=None, size=True, unicode=None):
        x, y = (-1, -1)
        if not unicode == True:
            for provider in self.default_json["providers"]:
                if not provider["type"] == "bitmap":
                    continue
                #todo: implement binary search
                for i in range(0, len(provider["chars"])):
                    if char in provider["chars"][i]:
                        if "file" in provider and provider["file"] == "minecraft:font/accented.png":
                            continue
                        if "height" in provider:
                            height = provider["height"]
                        else:
                            height = 8
                        y = i*height
                        x = provider["chars"][i].index(char)*8
                        width = 8
                        file = provider["file"]
                        break
        if x == -1 or unicode == True:
            value = ord(char)
            if value > 65535:
                return self.get_char("␀", color)

            page_int = value >> 8
            page_hex = f'{page_int:x}'
            if len(page_hex) == 1:
                page_hex = "0"+page_hex
            if not page_hex in self.textures:
                return self.get_char("␀", color)
            index = value & 0xff
            x = (index & 0x0f)*16
            y = (index // 16)*16
            img = self.textures[page_hex].crop((x, y, x+16, y+16))
            img = img.convert("RGBA")
            pixdata = img.load()
            unicode = True

        else:
            img = self.textures[file].crop((x, y, x+width, y+height))
            img = img.convert("RGBA")
            pixdata = img.load()
            unicode = False
            
        if size == True:
            size = self.get_size(char, img=img, unicode=unicode)
        else:
            size = []
        if color != None:
            for y in range(0, img.size[1]):
                for x in range(0, img.size[0]):
                    if pixdata[x, y] == (255, 255, 255, 255):
                        pixdata[x, y] = color
        return img, unicode, size

    #get the pixel size of a string or character 
    def get_size(self, text, img=None, unicode=None):
        size = [0, 0]
        if img == None and len(text) == 0:
            char_img, unicode, size = self.get_char(text[0], unicode=unicode)
            return tuple(size + [0])
        else:
            char_img = img
        counter = 0
        for char in text:
            if char == "§":
                counter += 1; continue
            elif len(text)>1 and text[counter-1] == "§":
                counter += 1; continue
            if img == None:
                char_img, unicode = self.get_char(text[0], unicode=unicode)[:2]
            if unicode == None:
                unicode = self.is_unicode(text[0])
            if unicode == False:
                pixdata = char_img.load()
                start, end = (0, 0)
                columns = []
                for x in range(0, char_img.size[0]):
                    columns.append(0)
                    for y in range(0, char_img.size[1]):
                        pixel = pixdata[x, y]
                        if not pixel[3] == 0:
                            columns[x] = 1

                if 1 in columns:
                    start = columns.index(1)
                    end = len(columns)-columns[::-1].index(1)
                size_new = [end-start, char_img.size[1]]
                if char == " ":
                    size_new = [3, char_img.size[1]]
                            
                size[0] += int((size_new[0])*2)+2
                if int(size_new[1]*2) > size[1]:
                    size[1] = int(size_new[1]*2)
                    
            else:
                sizes_index = ord(char)
                size_byte = self.sizes[sizes_index]
                start = size_byte >> 4
                end = size_byte & 0x0f
                diff = end-start
                
                if diff > 0:
                    size[0] += diff+3
                else:
                    extrema = char_img.getextrema()
                    if extrema[3][0] < 255:
                        size[0] += diff+3
                if size[1] < 16:
                    size[1] = 16
            counter += 1

        if unicode == False:
            start *= 2
            
        return tuple(size+[start])
                
class MOTDRenderer:
    def __init__(self, extracted_dir=os.path.dirname(__file__)+"/minecraft"):
        self.extracted_dir = extracted_dir
        #map color codes to rgb values
        self.colors = {
            "0": (0, 0, 0),
            "1": (0, 0, 170),
            "2": (0, 170, 0),
            "3": (0, 170, 170),
            "4": (170, 0, 0),
            "5": (170, 0, 170),
            "6": (255, 170, 0),
            "7": (170, 170, 170),
            "8": (85, 85, 85),
            "9": (85, 85, 255),
            "a": (85, 255, 85),
            "b": (85, 255, 255),
            "c": (255, 85, 85),
            "d": (255, 85, 255),
            "e": (255, 255, 85),
            "f": (255, 255, 255)
        }
        #map color and formatting values to the legacy color code system
        self.json_text_colors = {
            "black": "0",
            "dark_blue": "1",
            "dark_green": "2",
            "dark_aqua": "3",
            "dark_red": "4",
            "dark_purple": "5",
            "gold": "6",
            "gray": "7",
            "dark_gray": "8",
            "blue": "9",
            "green": "a",
            "aqua": "b",
            "red": "c",
            "light_purple": "d",
            "yellow": "e",
            "white": "f"
        }
        self.json_text_formats = {
            "bold": "l", 
            "italic": "o", 
            "underlined": "n",
            "strikethrough": "m",
            "obfuscated": "k"
        }
        self.font = MCFont(extracted_dir)

    #pings a server and returns stats
    def ping_server(self, address=("127.0.0.1", 25565)):
        pinger = ping.Pinger(address)
        stats = pinger.ping()
        return stats
    
    #parse text to extract information about formatting
    #accepts a string (legacy system) or a dict (new system)
    def parse_text(self, data, color_override = None):
        text_returned = []
        if type(data) is not str and data["text"] != "":
            data = data["text"]
        if type(data) is str:
            text_split = data.split("\n")
            for line in text_split:
                color = "7"
                format_code = ""
                text_returned.append([])
                for i in range(0, len(line)):
                    if line[i] == "§":
                        if line[i+1] == "r":
                            color = "7"
                            format_code = ""
                        else:
                            if line[i+1] in self.colors:
                                color = line[i+1]
                                format_code = ""
                            else:
                                format_code += line[i+1]
                    elif line[i-1] == "§":
                        continue
                    else:
                        char = {
                            "char": line[i],
                            "color": color,
                            "format_code": format_code
                            }
                        text_returned[-1].append(char)
                        
        else:
            text_returned.append([])
            for item in data["extra"]:
                color = ""
                if "color" in item:
                    if color != "reset":
                        color = self.json_text_colors[item["color"]]
                format_code = ""
                for text_format in self.json_text_formats:
                    if text_format in item:
                        format_code += self.json_text_formats[text_format]
                for char in item["text"]:
                    if char == "\n":
                        text_returned.append([])
                        continue
                    if color == "":
                        color = "7"
                    char_json = {
                        "char": char,
                        "color": color,
                        "format_code": format_code
                    }
                    text_returned[-1].append(char_json)
        return text_returned

    #draw a single character on an image
    def draw_char(self, img, pos, char, color="7", format_code="", char_obj=None, unicode=None):
        char_displayed = char
        if char_obj == None:
            char_img, unicode, size = self.font.get_char(char_displayed, unicode=unicode)
        else:
            char_img, unicode, size = char_obj
        start = size[2]
        drawer = ImageDraw.Draw(img)
        if unicode == True:
            scale = 1
        else:
            scale = 2
        color_raw = self.colors[color]
        pixdata = char_img.load()
        if color != None:
            for y in range(0, char_img.size[1]):
                for x in range(0, char_img.size[0]):
                    if pixdata[x, y] == (255, 255, 255, 255):
                        pixdata[x, y] = color_raw

        char_img = char_img.resize((char_img.size[0]*scale, char_img.size[1]*scale), Image.NEAREST)
        
        if "l" in format_code: #bold
            img.paste(char_img, (pos[0]+1-start, pos[1]), mask=char_img)
            if not unicode:
                img.paste(char_img, (pos[0]+2-start, pos[1]), mask=char_img)
        if "o" in format_code: #italics
            char_img_new = Image.new("RGBA", (int(char_img.size[0]*1.25), char_img.size[1]))
            char_img_new.paste(char_img, (int(char_img.size[0]*0.25), 0))
            char_img = char_img_new
            char_img = char_img.transform(img.size, Image.AFFINE, (1, 0.25, 0, 0, 1, 0))
        if "n" in format_code: #underline
            drawer.line((pos[0]-2-start, pos[1]+16, pos[0]+size[0], pos[1]+16),
                        fill=self.colors[color], width=2)
        if "m" in format_code: #strikethrough
            drawer.line((pos[0]-2-start, pos[1]+7, pos[0]+size[0], pos[1]+7),
                        fill=self.colors[color], width=2)
        img.paste(char_img, (pos[0]-start, pos[1]), mask=char_img)

    #draw text on a image
    def draw_text(self, image, pos, text_parsed, force_unicode=False):
        letter_spacing = 10
        x, y = pos
        if force_unicode == False:
            unicode = None
            
        for line in text_parsed:
            line_offset = 0
            for char in line:
                y_offset = 0
                if "k" in char["format_code"]: #obfuscated
                    char_size = self.font.get_size(char["char"], unicode=force_unicode)[0]-3
                    if char_size > 0:
                        char["char"] = self.font.get_random_char(char_size)
                        unicode = True
                if force_unicode:
                    unicode = True
                    if char["char"] == " ":
                        unicode = False
                    
                char_size, height, start = self.font.get_size(char["char"], unicode=unicode)
                
                if "l" in char["format_code"]:
                    if self.font.is_emoji(char["char"]):
                        char["format_code"] = char["format_code"].replace("l", "")
                    else:
                        #char_size += 1
                        if unicode != True:
                            char_size += 2
                if char_size > 0:
                    self.draw_char(image, (x+line_offset, y+y_offset), **char, unicode=unicode)
                    line_offset += char_size
                else:
                    pass
                unicode = None
            y += 18

    def get_connection_icon(self, status=0):
        icon_page = Image.open(self.extracted_dir+"/assets/minecraft/textures/gui/icons.png")
        y = 16+8*status
        icon = icon_page.crop((0, y, 10, y+8))
        return icon

    #get only a server's icon
    def get_thumbnail(self, stats=None, address=("127.0.0.1", 25565)):
        try:
            if stats == None:
                stats = self.ping_server(address)
            if "favicon" in stats:
                image_base64 = stats["favicon"].replace("data:image/png;base64,", "", 1)
                image_data = BytesIO(base64.b64decode(image_base64, validate=True))
                thumbnail = Image.open(image_data)
        except socket.gaierror:
            pass
        finally:
            if stats == None or not "favicon" in stats:
                thumbnail = Image.open(self.extracted_dir+"/assets/minecraft/textures/misc/unknown_server.png")
                thumbnail = thumbnail.resize((thumbnail.size[0]//2, thumbnail.size[1]//2), Image.NEAREST)
        return thumbnail

    #renders what a server would look like in the mc server list
    #can also imitate the "force unicode font" option
    #returns a PIL image object
    def get_full_image(self, title="A Minecraft Server", address=("127.0.0.1", 25565), force_unicode=False, status=None):
        stats = None
        try:
            stats = self.ping_server(address)
            motd_raw = stats["description"]
        except socket.gaierror:
            motd_raw = "§4Can't resolve hostname"
        except (socket.timeout, ConnectionRefusedError) as e:
            motd_raw = "§4Can't connect to server"
        motd_parsed = self.parse_text(motd_raw)

        thumbnail = self.get_thumbnail(stats=stats, address=address)
        image = Image.new("RGB", (610, 72))
        drawer = ImageDraw.Draw(image)
        
        background = Image.open(self.extracted_dir+"/assets/minecraft/textures/gui/options_background.png")
        background = background.convert("RGB")
        background = background.point(lambda i: (i + 8 // 2) // 8)
        pixdata = background.load()
        background = background.resize((background.size[0]*4, background.size[1]*4), Image.NEAREST)
        for y in range(0, image.size[1]//64+1):
            for x in range(0, image.size[0]//64+1):
                image.paste(background, (x*64-2, y*64-4))
                
        image.paste(thumbnail, (4, 4), mask=thumbnail)
        title_parsed = self.parse_text("§f"+title)
        self.draw_text(image, (74, 6), title_parsed, force_unicode=force_unicode)
        self.draw_text(image, (74, 28), motd_parsed, force_unicode=force_unicode)

        if status == None:
            if stats == None:
                status = 5
            elif stats["ping"] > 1000:
                status = 4
            elif stats["ping"] > 500:
                status = 3
            elif stats["ping"] > 250:
                status = 2
            elif stats["ping"] > 100:
                status = 1
            else:
                status = 0
        connection_icon = self.get_connection_icon(status)
        connection_icon = connection_icon.resize((connection_icon.size[0]*2, connection_icon.size[1]*2), Image.NEAREST)
        image.paste(connection_icon, (584, 6), mask=connection_icon)

        if stats != None:
            player_count_text = "{numplayers}§8/§r{maxplayers}".format(
                numplayers=stats["players"]["online"], maxplayers=stats["players"]["max"])
            player_count_start = 580-self.font.get_size(player_count_text, unicode=force_unicode)[0]
            player_count_parsed = self.parse_text(player_count_text)
            self.draw_text(image, (player_count_start, 6), player_count_parsed, force_unicode=force_unicode)

        return image
