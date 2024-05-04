from PIL import Image, ImageFilter
import math

FILE_NAME = "letters.txt"
TEXT_NAME = "text.txt"
IMAGE_SIZE = 1000
HEXAGON_SIDE = IMAGE_SIZE/2
HEXAGON_APOTHEM = math.sqrt(HEXAGON_SIDE**2 - (HEXAGON_SIDE**2)/4)
HEXAGON_SMALL_HEIGHT = math.sqrt(HEXAGON_SIDE**2 - HEXAGON_APOTHEM**2)
LINE_WIDTH = 20
CROP_ROOM = math.floor(IMAGE_SIZE - 2*HEXAGON_APOTHEM)
MAX_CHARACTERS_PER_LINE = 4

# OPTIONS
GUIDES = False
RESIZE = False
RESIZE_PERCENT = 0.2


def readFile(vowels, consonants, modifiers, breaks):
    file = open(FILE_NAME, "r", encoding="utf-8")
    n = 0

    for word in file:
        print("Reading Dictionary. Letters Read: {}".format(n), end="\r")
        word = word.strip('\n')
        letters = word.split(",")

        letter = letters[0]
        type = letters[1]
        parts = letters[2:]

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
    print("Reading Text...")
    textFile = open(TEXT_NAME, "r", encoding="utf-8")
    symbols = []
    n = 0
    k = 0

    for line in textFile:
        line = line.strip("\n")

        for x in line:
            if(not checkLetter(x, vowels, consonants, modifiers, breaks)):
                k+=1
                print("Unknown symbols removed: {}".format(k), end="\r")
                line = line.replace(x,"$")
        
        print()
        while len(line) > 0: 
            print("Symbols created: {}".format(n), end="\r")
            
            parts = []

            if(line[0] == "$"):
                symbol = Image.new('RGBA',(IMAGE_SIZE, IMAGE_SIZE),(255, 255, 255, 0))
                symbol.paste(modifiers["UnknownSymbol"],(0,0),modifiers["UnknownSymbol"])
                symbols.append(symbol)

                line = line[1:]
                n += 1
                continue

            c = False
            if(len(line) >= 2):
                if(line[0].lower() in consonants and (line[0].lower() == line[1].lower())):
                    c = True
                    parts.append(consonants[line[0]])
                    parts.append(modifiers["ModifierLongConsonant"])
                    line = line[2:]
                elif(line[0].lower() in consonants):
                    c = True
                    parts.append(consonants[line[0].lower()])
                    line = line[1:]
            elif(len(line) >= 1):
                if(line[0].lower() in consonants):
                    c = True
                    parts.append(consonants[line[0].lower()])
                    line = line[1:]

            v = False
            if(len(line) >= 2):
                if(line[0].lower() + line[1].lower() in vowels):
                    v = True
                    parts.append(vowels[line[0].lower() + line[1].lower()])
                    line = line[2:]
                elif(line[0].lower() in vowels):
                    v = True
                    parts.append(vowels[line[0].lower()])
                    line = line[1:]
            elif(len(line) >= 1):
                if(line[0].lower() in vowels):
                    v = True
                    parts.append(vowels[line[0].lower()])
                    line = line[1:]
                    
            if(len(line) >= 1):
                if(line[0] in breaks):
                    parts.append(breaks[line[0]])
                    line = line[1:]

            if(not c):
                parts.append(modifiers["ModifierNoConsonant"])
            elif(not v):
                parts.append(modifiers["ModifierNoVowel"])

            symbol = Image.new('RGBA',(IMAGE_SIZE, IMAGE_SIZE),(255, 255, 255, 0))
            for part in parts:
                symbol.paste(part,(0,0),part)
            symbols.append(symbol)
            n += 1

    print("Symbols created: {}".format(n))
    return symbols

def checkLetter(letter, vowels, consonants, modifiers, breaks):
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
    symbol = Image.new('RGBA', (IMAGE_SIZE,IMAGE_SIZE),(255, 255, 255, 0))

    for number in numbers:
        imageName = 'Parts\{}.png'.format(number)
        part = Image.open(imageName)
        symbol.paste(part,(0,0),part)
    
    symbol = symbol.crop((CROP_ROOM/2,0,IMAGE_SIZE - CROP_ROOM/2,IMAGE_SIZE))
    return symbol


def drawText(symbols):
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
            x = math.ceil(2*c*HEXAGON_APOTHEM - c*LINE_WIDTH - (r%2)*LINE_WIDTH/2 + HEXAGON_APOTHEM*(r%2))
            y = math.ceil(r*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2)
            image.paste(symbols[n], (x, y), symbols[n])
            n += 1

    print("Working on image {}/{}".format(n,len(symbols)))
    return image

def createCanvas(rows, columns):
    w = math.ceil(2*HEXAGON_APOTHEM*columns - LINE_WIDTH*(columns-1) - LINE_WIDTH/2)
    if(rows > 1):
        w += math.ceil(HEXAGON_APOTHEM)
    h = math.ceil(rows*(HEXAGON_SIDE - LINE_WIDTH/2)*3/2 + HEXAGON_SMALL_HEIGHT + LINE_WIDTH)

    canvas = Image.new('RGBA',(w, h),(255, 255, 255, 255))

    return canvas

def drawGuide(rows, collumns, length, canvas):
    guide = Image.open('Parts\guide.png')
    guide = guide.crop((CROP_ROOM/2,0,IMAGE_SIZE - CROP_ROOM/2,IMAGE_SIZE))
    n = 0

    for r in range(0,rows):
        for c in range(0,collumns):
            print("Working on guides {}/{}".format(n,length) , end='\r')
            if(n == length):
                print("Working on guides {}/{}".format(n,length))
                return canvas
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

    [vowels, consonants, modifiers, breaks] = readFile(vowels, consonants, modifiers, breaks)

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