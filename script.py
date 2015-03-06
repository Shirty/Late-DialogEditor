from PIL import Image, ImageFont, ImageDraw
from xml.etree import ElementTree
import os.path, sys

import options

# Check everything we need is here
if not os.path.exists(options.image_folder):
    os.mkdir(options.image_folder)

if not os.path.exists(options.xml_file_name):
    print "Could not find XML!"
    sys.exit()

if not os.path.exists(options.font_name):
    print "Could not find font!"
    sys.exit()

if not os.path.exists(options.black_dialog_filename):
    print "Could not find black dialog image!"
    sys.exit()

if not os.path.exists(options.white_dialog_filename):
    print "Could not find white dialog image!"
    sys.exit()

# TODO: Need a way to figure out text_offset, should be possible with font size
# TODO: Build in checker make sure we don't have extra characters etc
# TODO: Make it so dialogs are smaller when one liners

tree = ElementTree.parse(options.xml_file_name)
root = tree.getroot()

discussion_i = 0
line_i = 0
for act in root:
    for initiator in act:
        for discussion in initiator:
            discussion_i += 1
            for line in discussion:
                # MAKE THE IMAGE
                # Do not process special nodes
                if line.tag == "Action":
                    continue
                elif line.tag == "NewItem":
                    continue
                #TODO dangerous thing here
                # Process character nodes
                elif line.tag == "Player":
                    dialog_filename = options.black_dialog_filename
                    fill_color = (255, 255, 255)
                else:
                    dialog_filename = options.white_dialog_filename
                    fill_color = (0, 0, 0)

                text = line.text

                image = Image.open(dialog_filename)
                font = ImageFont.truetype(options.font_name, options.font_size)

                image_width, image_height = image.size
                print "Image height: " + str(image_height)
                print "Image width: " + str(image_width)

                words = text.split()
                wordI = 0
                phrases = []
                phrasesI = 0

                text_width_limit = base_text_width_limit = image.size[0] - 2 * options.initial_text_offset[0]
                print "Base text width limit: " + str(base_text_width_limit)
                phrases.append(words[wordI])
                text_width_limit -= font.getsize(words[wordI])[0]
                wordI += 1

                # TextWrapping
                while wordI < len(words):
                    text_width_limit -= font.getsize(" " + words[wordI])[0]
                    if text_width_limit < 0:
                        text_width_limit = base_text_width_limit - font.getsize(" " + words[wordI])[0]
                        phrases.append(words[wordI])
                        phrasesI += 1
                    else:
                        phrases[phrasesI] = phrases[phrasesI] + " " + words[wordI]
                    wordI += 1

                text_height = sum([font.getsize(phrase)[1] for phrase in phrases])
                print "Text height: " + str(text_height)

                difference = image_height - (text_height + 2 * options.initial_text_offset[1])
                print "Difference: " + str(difference)

                new_image = image.resize((image_width, image_height - difference), Image.LANCZOS)
                draw = ImageDraw.Draw(new_image)

                # offset_y = (new_image.size[1] / float(image_height)) * initial_text_offset[1]
                # print offset_y

                write_position = [options.initial_text_offset[0], options.initial_text_offset[1]]
                for phrase in phrases:
                    draw.text(write_position, phrase, font=font, fill=fill_color)
                    write_position[1] += draw.textsize(phrase, font=font)[1]

                print "Length of each phrase: "
                for phrase in phrases:
                    print phrase + "// size: " + str(draw.textsize(phrase, font=font))

                print "New image size: " + str(new_image.size)

                # Notice we increment before this is mainly for construct and xpath which uses 1 as the first index
                act_name = act.tag
                initiator_name = initiator.tag
                line_i += 1
                new_image.save(os.path.join(options.image_folder, act_name + "_" + initiator_name + "_" + str(discussion_i) + "_" + str(line_i) + ".png"))
