"""
This code parses flatfile data containing timestamps and youtube subtitles
and creates a JSON file from it.
"""

from os import path, listdir
import re
import json


# def remove_timestamps():
#     import os
#     dirPath = os.path.dirname(os.path.realpath(__file__))+"/data"
#     print(dirPath)
#     for f in listdir(dirPath):
#         match = re.search('_(.*)', f)
#         if match:
#             fileName = match.groups()[0]
#             os.rename(dirPath+"/"+f, dirPath+"/"+fileName)
#         print(match)


class Review:
    def __init__(self):
        with open('reviewed.json', 'r') as f:
            self.reviewed_json = json.loads(f.read())
        with open('to_review.json', 'r') as f:
            self.to_review = json.loads(f.read())

    def log_reviewed(self, file_name, finalized, details):
        self.reviewed_json[file_name] = finalized
        if not finalized:
            self.to_review[file_name] = details
        else:
            if file_name in self.to_review:
                del self.to_review[file_name]

    def write_to_file(self):
        with open('reviewed.json', 'w') as f:
            f.write(json.dumps(self.reviewed_json))
        with open('to_review.json', 'w') as f:
            f.write(json.dumps(self.to_review))


def bad_word_parse():
    with open('bad_words.txt', 'r') as f:
        text = f.read()
        words = text.split(", ")
    with open('bad_word.json', 'w') as f:
        f.write(json.dumps({"offensive_words": words}))


def count_words(text):
    pass


def main():
    import os
    review = Review()
    dirPath = os.path.dirname(os.path.realpath(__file__))+"/data"
    jsonFile = {}

    jsonFile["description"] = "This project attempt to annotate and classify Youtube videos taking into account the content of the video and its composition. While youtube flags content inappropriate for young audiences by requiring viewers to sign in, a lot of youtube content is generally unaudited if the uploader of the video does not flag it so. Also there is no distinction between which content is appropriate for what age groups. We will classify content based the film rating system: G, PG, PG-13 and R. We will also apply a binary classification for classifying clickbait videos."
    jsonFile["corpus"] = []
    for f in listdir(dirPath):
        text = ''
        file_name = ""
        with open(path.join(dirPath, f)) as file:
            file_name = file.name
            while True:
                lineNo = file.readline().strip()
                if not lineNo:
                    break

                lineTimestamp = file.readline().strip()
                lineText = file.readline().strip()
                blankLine = file.readline().strip()

                if not text:
                    text += lineText
                else:
                    text += ' ' + lineText

        # print text

        offensiveWords, profaneWords = {}, {}
        with open('bad_words.json') as badwords:
            data = json.load(badwords)

            for offensiveW in data['offensive']:
                phrase = offensiveW.split()
                if len(phrase) == 1:
                    offensiveWords[phrase[0]] = -1
                elif len(phrase) > 1:
                    offensiveWords[phrase[0]] = phrase

            for profaneW in data['profane']:
                phrase = profaneW.split()
                if len(phrase) == 1:
                    profaneWords[phrase[0]] = -1
                elif len(profaneW) > 1:
                    profaneWords[phrase[0]] = phrase

        proWordCount, offWordCount = 0, 0
        text = text.split()
        for word in text:
            if word in profaneWords:
                if profaneWords[word] == -1:
                    proWordCount += 1
                else:
                    idx = text.index(word) + 1
                    match = True
                    for w in profaneWords[word][1:]:
                        if idx == len(text):
                            match = False
                            break

                        if w != text[idx]:
                            match = False
                            break
                        idx += 1

                    if match == True:
                        proWordCount += 1

            if word in offensiveWords:
                if offensiveWords[word] == -1:
                    offWordCount += 1
                else:
                    idx = text.index(word) + 1
                    match = True
                    for w in offensiveWords[word][1:]:
                        if idx == len(text):
                            match = False
                            break

                        if w != text[idx]:
                            match = False
                            break
                        idx += 1

                    if match == True:
                        offWordCount += 1

        if offWordCount == 0:
            if proWordCount <= 2:
                label = 'G'

            elif proWordCount > 2 and proWordCount <= 4:
                # ********** Call Kaladhar's Function **********
                # No context and not sexual
                review.log_reviewed(file_name, False, [])
                label = 'PG'

                # Context
                label = 'PG13'

            elif proWordCount > 4:
                label = 'PG13'

        elif offWordCount > 1:
            # ********** Call Kaladhar's Function **********
            # Context Sexual
            review.log_reviewed(file_name, False, [])
            label = 'R'

            # Context not sexual and offWordCount > 1 and offWordCount < 4
            label = 'PG13'

        # match = re.search('_(.*)', f)
        # fileName = match.groups()[0]
        # print fileName

        jsonFile["corpus"].append({
            'data': " ".join(text),
            'label': label,
        })

    # print subtitles
    with open('final.json', 'w') as file:
        json.dump(jsonFile, file)


if __name__ == "__main__":
    main()
