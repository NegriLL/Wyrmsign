from PIL import Image, ImageFilter
import math

# TODO: turn these global variables into a config file for easier and modular use.
ALPHABET_FILE = "letters.txt"
TEXT_NAME = "text.txt"
IMAGE_SIZE = 1000
HEXAGON_SIDE = IMAGE_SIZE/2
HEXAGON_APOTHEM = math.sqrt(HEXAGON_SIDE**2 - (HEXAGON_SIDE**2)/4)
HEXAGON_SMALL_HEIGHT = math.sqrt(HEXAGON_SIDE**2 - HEXAGON_APOTHEM**2)
LINE_WIDTH = 20
CROP_ROOM = math.floor(IMAGE_SIZE - 2*HEXAGON_APOTHEM)
MAX_CHARACTERS_PER_LINE = 4

# User options
GUIDES = False # Draw Guidelines for the placement of each symbol
RESIZE = False # Resize image after completion
RESIZE_PERCENT = 0.2 # Amount the image should be resized to


def readAlphabet(vowels, consonants, modifiers, breaks):
    # Reads the file in ALPHABET_FILE and returns an array of with
    # the symbols for each individual letter.

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
            vowels[letter] = drawSymbol(parts)
        elif(type == "c"):
            consonants[letter] = drawSymbol(parts)
        elif(type == "m"):
            modifiers[letter] = drawSymbol(parts)
        elif(type == "b"):
            breaks[letter] = drawSymbol(parts)

        n += 1
    print("Reading Dictionary. Letters Read: {}".format(n))

    return [vowels, consonants, modifiers, breaks]

def readText(vowels, consonants, modifiers, breaks):
    # Main text parser function. Reads the text in TEXT_NAME and returns
    # the list of symbols that need to be printed
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
            if(not checkLetter(x, vowels, consonants, modifiers, breaks)):
                k+=1
                print("Unknown symbols removed: {}".format(k), end="\r")
                line = line.replace(x,"$")
        
        print()
        while len(line) > 0:  # Main parser loop

            print("Symbols created: {}".format(n), end="\r")
            
            parts = []

            # Check if symbol is unknown and draws UnknownSymbol
            if(line[0] == "$"):
                symbol = Image.new('RGBA',(IMAGE_SIZE, IMAGE_SIZE),(255, 255, 255, 0))
                symbol.paste(modifiers["UnknownSymbol"],(0,0),modifiers["UnknownSymbol"])
                symbols.append(symbol)

                line = line[1:]
                n += 1
                continue
            
            c = False
            # Checks if a consonant is present first
            if(len(line) >= 2): # Double consonants are a special case that must be checked here
                if(line[0].lower() in consonants and (line[0].lower() == line[1].lower())):
                    c = True
                    parts.append(consonants[line[0]])
                    parts.append(modifiers["ModifierLongConsonant"])
                    line = line[2:]
                elif(line[0].lower() in consonants):
                    c = True
                    parts.append(consonants[line[0].lower()])
                    line = line[1:]
            elif(len(line) >= 1): # Checking for single consonants
                if(line[0].lower() in consonants):
                    c = True
                    parts.append(consonants[line[0].lower()])
                    line = line[1:]

            # Check if a vowel is present afterwards.
            v = False
            if(len(line) >= 2): # Double vowels are a special case that must be checked here
                if(line[0].lower() + line[1].lower() in vowels):
                    v = True
                    parts.append(vowels[line[0].lower() + line[1].lower()])
                    line = line[2:]
                elif(line[0].lower() in vowels):
                    v = True
                    parts.append(vowels[line[0].lower()])
                    line = line[1:]
            elif(len(line) >= 1): # Checking for single consonants
                if(line[0].lower() in vowels):
                    v = True
                    parts.append(vowels[line[0].lower()])
                    line = line[1:]
            
            # Check if there is a break such as a space or a period
            if(len(line) >= 1):
                if(line[0] in breaks):
                    parts.append(breaks[line[0]])
                    line = line[1:]

            # Puts everything together, accounting for the lack of consonants or vowels
            if(not c):
                parts.append(modifiers["ModifierNoConsonant"])
            elif(not v):
                parts.append(modifiers["ModifierNoVowel"])

            # The symbols are all put  together into the final syllable.
            symbol = Image.new('RGBA',(IMAGE_SIZE, IMAGE_SIZE),(255, 255, 255, 0))
            for part in parts:
                symbol.paste(part,(0,0),part)
            symbols.append(symbol)
            n += 1

    print("Symbols created: {}".format(n))
    return symbols

def checkLetter(letter, vowels, consonants, modifiers, breaks):
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

def drawSymbol(numbers):
    # Takes numbers in an array and joins them into an image by using the corresponding
    # Parts(number).png files.
    symbol = Image.new('RGBA', (IMAGE_SIZE,IMAGE_SIZE),(255, 255, 255, 0))

    for number in numbers:
        imageName = 'Parts\{}.png'.format(number)
        part = Image.open(imageName)
        symbol.paste(part,(0,0),part)
    
    # Trim the excess from the top and sides of the hexagon for easier pasting later on
    symbol = symbol.crop((CROP_ROOM/2,0,IMAGE_SIZE - CROP_ROOM/2,IMAGE_SIZE))
    return symbol


def drawText(symbols):
    # Takes the list of symbols and transforms it into the contiguous text.
    collumns = MAX_CHARACTERS_PER_LINE
    if(len(symbols) < MAX_CHARACTERS_PER_LINE):
        collumns = len(symbols)

    rows = math.ceil(len(symbols) / collumns)
    n = 0

    image = createCanvas(rows, collumns)
    if(GUIDES):
        image = drawGuide(rows, collumns, len(symbols), image)

    for r in range(0,rows):
        for c in range(0,collumns):
            print("Working on image {}/{}".format(n,len(symbols)) , end='\r')
            if(n == len(symbols)):
                print("Working on image {}/{}".format(n,len(symbols)))
                return image
            # Decide the placement of each symbol with a bit of math. Hexagons are fun.
            x = math.ceil(2*c*HEXAGON_APOTHEM - c*LINE_WIDTH - (r%2)*LINE_WIDTH/2 + HEXAGON_APOTHEM*(r%2))
            y = math.ceil(r*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2)
            image.paste(symbols[n], (x, y), symbols[n])
            n += 1

    print("Working on image {}/{}".format(n,len(symbols)))
    return image

def createCanvas(rows, columns):
    # Creates the full size of the final image with a bit of hexagon math. Since the hexagon
    # edges must overlap each other and each even numbered line has to be displaced, it
    # requires some math.
    # TODO: fix the canvas size in case of a small number of symbols.
    w = math.ceil(2*HEXAGON_APOTHEM*columns - LINE_WIDTH*(columns-1) - LINE_WIDTH/2)
    if(rows > 1):
        w += math.ceil(HEXAGON_APOTHEM)
    h = math.ceil(rows*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2 + HEXAGON_SMALL_HEIGHT + LINE_WIDTH)

    canvas = Image.new('RGBA',(w, h),(255, 255, 255, 255))

    return canvas

def drawGuide(rows, collumns, length, canvas):
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
            x = math.ceil(2*c*HEXAGON_APOTHEM - c*LINE_WIDTH - (r%2)*LINE_WIDTH/2 + HEXAGON_APOTHEM*(r%2))
            y = math.ceil(r*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2)
            canvas.paste(guide, (x, y), guide)
            n += 1

    guide.close()
    return canvas


def main():
    vowels = {}
    consonants = {}
    modifiers = {}
    breaks = {}

    [vowels, consonants, modifiers, breaks] = readAlphabet(vowels, consonants, modifiers, breaks)

    symbols = readText(vowels, consonants, modifiers, breaks)
    result = drawText(symbols)

    if(RESIZE): 
        print("Resizing...")
        h, w = result.size
        new_size = (math.ceil(h*RESIZE_PERCENT), math.ceil(w*RESIZE_PERCENT))
        resizedResult = result.resize(new_size)
        resizedResult = resizedResult.filter(ImageFilter.BoxBlur(2))
        print("Saving...")
        resizedResult.save("result.png", 'PNG')
    else:
        print("Saving...")
        result.save("result.png", "PNG")
    print("Done!")

main()