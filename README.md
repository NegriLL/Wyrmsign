# Wyrmsign Generator

Wyrmsign is a syllabarium parser that converts latin text into a fictional alphabet. Each symbol in this alphabet is a complete syllable. Two vowels in a row result in a long vowel, while two consonants result in a consonant break. The hexagons are tesselated side by side, creating a seamless language that flows from character to character.
To create an image, write your text in the text.txt file (or change the target file name in settings.ini). The configuration file has instructions to suit your preferences. Run the code on the same directory as the text file.
Once complete, the code will generate your image, display it, and save it as result.png.

# Language Guide
![Wyrmsign syllabarium guide](https://i.imgur.com/JCI4ucK.png)

# Example
Here is an example of an image created using 10 syllables per line, with guides on, and resize set to 10%:
![Example of the wyrmsign hexagonal script](https://i.imgur.com/FhENQcG.png)

## WARNING
If resize is set to false, the generated images can be very large due to the resolution of the individual parts. It is recommended to keep resize on.
