import math
from PIL import Image, ImageFilter
from configparser import ConfigParser

def read_config():
    print("Reading configuration file...")
    file = "settings.ini"
    config = ConfigParser()
    config.read(file)

    # User options
    global TEXT_NAME
    TEXT_NAME = config["UserSettings"]["TextFile"]
    global GUIDES
    GUIDES = config["UserSettings"].getboolean("Guides")
    global RESIZE
    RESIZE = config["UserSettings"].getboolean("Resize")
    global RESIZE_PERCENT
    RESIZE_PERCENT = config["UserSettings"].getfloat("ResizePercent")
    global MAX_CHARACTERS_PER_LINE
    MAX_CHARACTERS_PER_LINE = config["UserSettings"].getint("CharactersPerLine")


    # Program options
    global ALPHABET_FILE
    ALPHABET_FILE = config["ProgramSettings"]["AlphabetFile"]
    global IMAGE_SIZE
    IMAGE_SIZE = config["ProgramSettings"].getint("ImageSize")
    global LINE_WIDTH
    LINE_WIDTH = config["ProgramSettings"].getint("LineWidth")

    # Perform calculations for image formatting
    global HEXAGON_SIDE
    HEXAGON_SIDE = IMAGE_SIZE/2
    global HEXAGON_APOTHEM
    HEXAGON_APOTHEM = math.sqrt(HEXAGON_SIDE**2 - (HEXAGON_SIDE**2)/4)
    global HEXAGON_SMALL_HEIGHT
    HEXAGON_SMALL_HEIGHT = math.sqrt(HEXAGON_SIDE**2 - HEXAGON_APOTHEM**2)
    global CROP_ROOM
    CROP_ROOM = math.floor(IMAGE_SIZE - 2*HEXAGON_APOTHEM)

def read_alphabet(vowels, consonants, modifiers, breaks):
    """ Reads the file in ALPHABET_FILE and returns an array of with
    the symbols for each individual letter."""

    file = open(ALPHABET_FILE, "r", encoding="utf-8")
    n = 0

    for word in file:
        print("Reading Dictionary. Letters Read: {}".format(n), end="\r")
        word = word.strip('\n')
        letters = word.split(",")

        letter = letters[0]
        type = letters[1]
        parts = letters[2:]

        # Begin drawing each letter and assigning it to its corresponding
        # array
        if(type == "v"):
            vowels[letter] = draw_symbol(parts)
        elif(type == "c"):
            consonants[letter] = draw_symbol(parts)
        elif(type == "m"):
            modifiers[letter] = draw_symbol(parts)
        elif(type == "b"):
            breaks[letter] = draw_symbol(parts)
        n += 1
    print("Reading Dictionary. Letters Read: {}".format(n))
    file.close()
    return [vowels, consonants, modifiers, breaks]

def read_text(vowels, consonants, modifiers, breaks):
    """ Main text parser function. Reads the text in TEXT_NAME and returns
    the list of symbols that need to be printed"""

    print("Reading Text...")
    textFile = open(TEXT_NAME, "r", encoding="utf-8")
    symbols = []
    n = 0
    k = 0

    for line in textFile:
        line = line.strip("\n")
        for x in line:
            # Replaces all unknown symbols with a symbol that will later be substituted
            # by a blank.
            if not check_letter(x, vowels, consonants, modifiers, breaks):
                k+=1
                print("Unknown symbols removed: {}".format(k), end="\r")
                line = line.replace(x,"$")
        print()

        while len(line) > 0:  # Main parser loop
            print("Symbols created: {}".format(n), end="\r")
            parts = []
            # Check if symbol is unknown and draws UnknownSymbol
            if line[0] == "$":
                symbol = Image.new('RGBA',(IMAGE_SIZE, IMAGE_SIZE),(255, 255, 255, 0))
                symbol.paste(modifiers["UnknownSymbol"],(0,0),modifiers["UnknownSymbol"])
                symbols.append(symbol)

                line = line[1:]
                n += 1
                continue
            
            c = False
            # Checks if a consonant is present first
            if len(line) >= 2: # Double consonants are a special case that must be checked here
                if line[0].lower() in consonants and (line[0].lower() == line[1].lower()):
                    c = True
                    parts.append(consonants[line[0]])
                    parts.append(modifiers["ModifierLongConsonant"])
                    line = line[2:]
                elif line[0].lower() in consonants:
                    c = True
                    parts.append(consonants[line[0].lower()])
                    line = line[1:]
            elif len(line) >= 1: # Checking for single consonants
                if line[0].lower() in consonants:
                    c = True
                    parts.append(consonants[line[0].lower()])
                    line = line[1:]

            # Check if a vowel is present afterwards.
            v = False
            if len(line) >= 2: # Double vowels are a special case that must be checked here
                if line[0].lower() + line[1].lower() in vowels:
                    v = True
                    parts.append(vowels[line[0].lower() + line[1].lower()])
                    line = line[2:]
                elif line[0].lower() in vowels:
                    v = True
                    parts.append(vowels[line[0].lower()])
                    line = line[1:]
            elif len(line) >= 1: # Checking for single consonants
                if line[0].lower() in vowels:
                    v = True
                    parts.append(vowels[line[0].lower()])
                    line = line[1:]
            
            # Check if there is a break such as a space or a period
            if len(line) >= 1:
                if line[0] in breaks:
                    parts.append(breaks[line[0]])
                    line = line[1:]

            # Puts everything together, accounting for the lack of consonants or vowels
            if not c:
                parts.append(modifiers["ModifierNoConsonant"])
            elif not v:
                parts.append(modifiers["ModifierNoVowel"])

            # The symbols are all put  together into the final syllable.
            symbol = Image.new('RGBA',(IMAGE_SIZE, IMAGE_SIZE),(255, 255, 255, 0))
            for part in parts:
                symbol.paste(part,(0,0),part)
            symbols.append(symbol)
            n += 1

    print("Symbols created: {}".format(n))
    textFile.close()
    return symbols

def check_letter(letter, vowels, consonants, modifiers, breaks):
    # Function that checks if a letter is found in any of the dictionaries
    letter = letter.lower()
    if letter in vowels:
        return True
    elif letter in consonants:
        return True
    elif letter in modifiers:
        return True
    elif letter in breaks:
        return True
    else:
        return False

def draw_symbol(numbers):
    # Takes numbers in an array and joins them into an image by using the corresponding
    # Parts/(number).png files.
    symbol = Image.new('RGBA', (IMAGE_SIZE,IMAGE_SIZE),(255, 255, 255, 0))

    for number in numbers:
        imageName = 'Parts\{}.png'.format(number)
        part = Image.open(imageName)
        symbol.paste(part,(0,0),part)
    
    # Trim the excess from the top and sides of the hexagon for easier pasting later on
    symbol = symbol.crop((CROP_ROOM/2,0,IMAGE_SIZE - CROP_ROOM/2,IMAGE_SIZE))
    return symbol


def draw_text(symbols):
    # Takes the list of symbols and transforms it into the contiguous text.
    collumns = MAX_CHARACTERS_PER_LINE
    if(len(symbols) < MAX_CHARACTERS_PER_LINE):
        collumns = len(symbols)

    rows = math.ceil(len(symbols) / collumns)
    n = 0

    image = create_canvas(rows, collumns)
    if(GUIDES):
        image = draw_guide(rows, collumns, len(symbols), image)

    for r in range(0,rows):
        for c in range(0,collumns):
            print("Working on image {}/{}".format(n,len(symbols)) , end='\r')
            if(n == len(symbols)):
                print("Working on image {}/{}".format(n,len(symbols)))
                return image
            # Decide the placement of each symbol with a bit of math. Hexagons are fun.
            x = math.ceil(2*c*HEXAGON_APOTHEM - c*LINE_WIDTH
                          - (r%2)*LINE_WIDTH/2 + HEXAGON_APOTHEM*(r%2))
            y = math.ceil(r*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2)
            image.paste(symbols[n], (x, y), symbols[n])
            n += 1

    print("Working on image {}/{}".format(n,len(symbols)))
    return image

def create_canvas(rows, columns):
    # Creates the full size of the final image with a bit of hexagon math. Since the hexagon
    # edges must overlap each other and each even numbered line has to be displaced, it
    # requires some math.
    # TODO: fix the canvas size in case of a small number of symbols.
    w = math.ceil(2*HEXAGON_APOTHEM*columns - LINE_WIDTH*(columns-1) - LINE_WIDTH/2)
    if(rows > 1):
        w += math.ceil(HEXAGON_APOTHEM)
    h = math.ceil(rows*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2
                  + HEXAGON_SMALL_HEIGHT + LINE_WIDTH)

    canvas = Image.new('RGBA',(w, h),(255, 255, 255, 255))

    return canvas

def draw_guide(rows, collumns, length, canvas):
    # If GUIDES = True, then this function will draw guidelines for the placement of each
    # hexagonal symbol.
    guide = Image.open('Parts\guide.png')
    guide = guide.crop((CROP_ROOM/2,0,IMAGE_SIZE - CROP_ROOM/2,IMAGE_SIZE))
    n = 0

    for r in range(0,rows):
        for c in range(0,collumns):
            print("Working on guides {}/{}".format(n,length) , end='\r')
            if(n == length):
                print("Working on guides {}/{}".format(n,length))
                return canvas
            # TODO: Implement the following code as a function to avoid rewriting it.
            x = math.ceil(2*c*HEXAGON_APOTHEM - c*LINE_WIDTH - (r%2)*LINE_WIDTH/2
                          + HEXAGON_APOTHEM*(r%2))
            y = math.ceil(r*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2)
            canvas.paste(guide, (x, y), guide)
            n += 1

    guide.close()
    return canvas


def main():
    read_config()

    vowels = {}
    consonants = {}
    modifiers = {}
    breaks = {}
    [vowels, consonants, modifiers, breaks] = read_alphabet(vowels, consonants,
                                                            modifiers, breaks)

    symbols = read_text(vowels, consonants, modifiers, breaks)
    result = draw_text(symbols)

    if(RESIZE): 
        print("Resizing...")
        h, w = result.size
        new_size = (math.ceil(h*RESIZE_PERCENT), math.ceil(w*RESIZE_PERCENT))
        resizedResult = result.resize(new_size)
        #resizedResult = resizedResult.filter(ImageFilter.BoxBlur(2))
        print("Saving...")
        resizedResult.save("result.png", 'PNG')
    else:
        print("Saving...")
        result.save("result.png", "PNG")
    print("Done!")
    resizedResult.show()

main()
