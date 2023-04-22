import datetime
import os
import random
import re
from enum import Enum

from dateutil.parser import parse
from PIL import Image, ImageDraw, ImageFont

try:
    import ujson as json
except Exception:
    import json

from mahiro import GroupMessageMahiro, Sender

# ==========================================

RESOURCES_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "resources", "vtuber-fortune"
)
IMAGE_DIR = 'img-pcr'

# ==========================================

# 屏蔽群 例：[12345678, 87654321]
blockGroupNumber = []
# 触发命令列表
commandList = [
    "今日人品",
    "今日运势",
    "抽签",
    "人品",
    "运势",
    "kkr签",
    "妈签",
    "xcw签",
    "炼签",
    "kyaru签",
    "臭鼬签",
]
# 是否开启泳装签
swimsuitModel = False

# ==========================================

async def bot_pcr_fortune(mahiro: GroupMessageMahiro):
    ctx = mahiro.ctx
    is_text = mahiro.extra.is_text
    userGroup = ctx.groupId

    if Tools.commandMatch(userGroup, blockGroupNumber):
        return

    if not is_text:
        return

    userQQ = ctx.userId
    msg = ctx.msg.Content.strip()

    handlingMessages(
        msg=msg,
        bot=mahiro.sender,
        userGroup=userGroup,
        userQQ=userQQ,
        userNickname=ctx.userNickname,
    )


class Model(Enum):

    ALL = "_all"

    BLURRY = "_blurry"

    SEND_AT = "_send_at"

    SEND_DEFAULT = "_send_default"


class Status(Enum):

    SUCCESS = "_success"

    FAILURE = "_failure"


class Tools:
    @staticmethod
    def writeFile(p, content):
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def readFileByLine(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return f.readlines()

    @staticmethod
    def readJsonFile(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    @staticmethod
    def writeJsonFile(p, content):
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(content))
        return Status.SUCCESS

    @staticmethod
    def readFileContent(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return f.read().strip()

    @staticmethod
    def commandMatch(msg, commandList, model=Model.ALL):
        if model == Model.ALL:
            for c in commandList:
                if c == msg:
                    return True
        if model == Model.BLURRY:
            for c in commandList:
                if msg.find(c) != -1:
                    return True
        return False

    @staticmethod
    def checkFolder(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def atQQ(nickname):
        return f"@{nickname}\n"


class TimeUtils:

    DAY = "day"

    HOUR = "hour"

    MINUTE = "minute"

    SECOND = "second"

    ALL = "all"

    @staticmethod
    def getTheCurrentTime():
        nowDate = str(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"))
        return nowDate

    @staticmethod
    def getAccurateTimeNow():
        nowDate = str(
            datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d/%H:%M:%S")
        )
        return nowDate

    @classmethod
    def judgeTimeDifference(cls, lastTime):
        timeNow = cls.getAccurateTimeNow()
        a = parse(lastTime)
        b = parse(timeNow)
        return int((b - a).total_seconds() / 3600)

    @staticmethod
    def getTheCurrentHour():
        return int(str(datetime.datetime.strftime(datetime.datetime.now(), "%H")))

    @classmethod
    def calculateTheElapsedTimeCombination(cls, lastTime):
        timeNow = cls.getAccurateTimeNow()
        a = parse(lastTime)
        b = parse(timeNow)
        seconds = int((b - a).total_seconds())
        return [int(seconds / 3600), int((seconds % 3600) / 60), int(seconds % 60)]

    @staticmethod
    def replaceHourMinuteAndSecond(parameterList, msg):
        return (
            msg.replace(r"{hour}", str(parameterList[0]))
            .replace(r"{minute}", str(parameterList[1]))
            .replace(r"{second}", str(parameterList[2]))
        )

    @classmethod
    def getTimeDifference(cls, original, model):
        a = parse(original)
        b = parse(cls.getAccurateTimeNow())
        seconds = int((b - a).total_seconds())
        if model == cls.ALL:
            return {
                cls.DAY: int((b - a).days),
                cls.HOUR: int(seconds / 3600),
                cls.MINUTE: int((seconds % 3600) / 60),  # The rest
                cls.SECOND: int(seconds % 60),  # The rest
            }
        if model == cls.DAY:
            b = parse(cls.getTheCurrentTime())
            return int((b - a).days)
        if model == cls.MINUTE:
            return int(seconds / 60)
        if model == cls.SECOND:
            return seconds


class PcrFortuneModel(Enum):

    KYARU = "2"

    XCW = "27"

    M = "41"

    DEFAULT = "default"


class Swimsuit:

    prohibitedValue = [3, 25, [49, 52], 59]

    @classmethod
    def swimsuitRecognition(cls, path):
        # Get the serial number in the path
        try:
            number = int(re.search("frame_(\d)", path).group(1))
        except:
            raise Exception('The image name does not conform to the format "frame_1" !')
        # Identify whether it is within the prohibited range
        for i in cls.prohibitedValue:
            if isinstance(i, list) and (number in [j for j in range(i[0], i[1] + 1)]):
                return True
            if isinstance(i, int) and number == i:
                return True
        return False


def handlingMessages(msg, bot: Sender, userGroup, userQQ, userNickname):
    match = Tools.commandMatch(msg, commandList)
    if match:
        # Determine if it has been used today
        if testUse(userQQ) == Status.SUCCESS:
            model = PcrFortuneModel.DEFAULT
            # kkr
            if msg.find("kkr") != -1 or msg.find("妈") != -1:
                model = PcrFortuneModel.M
            # kyaru
            if msg.find("kyaru") != -1 or msg.find("臭鼬") != -1:
                model = PcrFortuneModel.KYARU
            # xcw
            if msg.find("xcw") != -1 or msg.find("炼") != -1:
                model = PcrFortuneModel.XCW
            # Plot
            outPath = drawing(model, userQQ)
            bot.send_to_group(
                group_id=userGroup,
                fast_image=outPath,
                msg=Tools.atQQ(userNickname),
            )


def testUse(userQQ):
    p = f"{RESOURCES_BASE_PATH}/user/{userQQ}.json"
    dir = f"{RESOURCES_BASE_PATH}/user"
    Tools.checkFolder(dir)
    content = Tools.readJsonFile(p)
    if content == Status.FAILURE:
        userStructure = {"time": TimeUtils.getTheCurrentTime()}
        Tools.writeJsonFile(p, userStructure)
        return Status.SUCCESS
    interval = TimeUtils.getTimeDifference(content["time"], TimeUtils.DAY)
    if interval >= 1:
        content["time"] = TimeUtils.getTheCurrentTime()
        Tools.writeJsonFile(p, content)
        return Status.SUCCESS
    return Status.FAILURE


def copywriting():
    p = f"{RESOURCES_BASE_PATH}/fortune/copywriting.json"
    content = Tools.readJsonFile(p)
    return random.choice(content["copywriting"])


def getTitle(structure):
    p = f"{RESOURCES_BASE_PATH}/fortune/goodLuck.json"
    content = Tools.readJsonFile(p)
    for i in content["types_of"]:
        if i["good-luck"] == structure["good-luck"]:
            return i["name"]
    raise Exception("Configuration file error")


def drawing(model, userQQ):
    fontPath = {
        "title": f"{RESOURCES_BASE_PATH}/font/Mamelon.otf",
        "text": f"{RESOURCES_BASE_PATH}/font/sakura.ttf",
    }
    imgPath = ""
    # When not a specific picture
    if model == PcrFortuneModel.DEFAULT:
        randomPath = randomBasemap()
        if not swimsuitModel:
            # Take three random values
            for i in range(0, 3):
                if Swimsuit.swimsuitRecognition(randomPath):
                    randomPath = randomBasemap()
                    continue
                break
            # Judge whether it is reasonable
            if Swimsuit.swimsuitRecognition(randomPath):
                # If it is still a swimsuit three times, the kkr base map is taken by default
                imgPath = (
                    f"{RESOURCES_BASE_PATH}/{IMAGE_DIR}/frame_{PcrFortuneModel.M.value}.jpg"
                )
            else:
                imgPath = randomPath
        else:
            imgPath = randomPath
    # kkr
    if model == PcrFortuneModel.M:
        imgPath = f"{RESOURCES_BASE_PATH}/{IMAGE_DIR}/frame_{PcrFortuneModel.M.value}.jpg"
    # kyaru
    if model == PcrFortuneModel.KYARU:
        imgPath = f"{RESOURCES_BASE_PATH}/{IMAGE_DIR}/frame_{PcrFortuneModel.KYARU.value}.jpg"
    # xcw
    if model == PcrFortuneModel.XCW:
        imgPath = f"{RESOURCES_BASE_PATH}/{IMAGE_DIR}/frame_{PcrFortuneModel.XCW.value}.jpg"
    img = Image.open(imgPath)
    # Draw title
    draw = ImageDraw.Draw(img)
    text = copywriting()
    title = getTitle(text)
    text = text["content"]
    font_size = 45
    color = "#F5F5F5"
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath["title"], font_size)
    font_length = ttfront.getsize(title)
    draw.text(
        (
            image_font_center[0] - font_length[0] / 2,
            image_font_center[1] - font_length[1] / 2,
        ),
        title,
        fill=color,
        font=ttfront,
    )
    # Text rendering
    font_size = 25
    color = "#323232"
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath["text"], font_size)
    result = decrement(text)
    if not result[0]:
        return
    textVertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = vertical(result[i + 1])
        x = int(
            image_font_center[0]
            + (result[0] - 2) * font_size / 2
            + (result[0] - 1) * 4
            - i * (font_size + 4)
        )
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)
    # Save
    outPath = exportFilePath(imgPath, userQQ)
    img.save(outPath)
    return outPath


def exportFilePath(originalFilePath, userQQ):
    outPath = originalFilePath.replace(f"/{IMAGE_DIR}/", "/out/").replace("frame", str(userQQ))
    dirPath = f"{RESOURCES_BASE_PATH}/out"
    Tools.checkFolder(dirPath)
    return outPath


def randomBasemap():
    p = f"{RESOURCES_BASE_PATH}/{IMAGE_DIR}"
    return p + "/" + random.choice(os.listdir(p))


def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = " "
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [
                numberOfSlices,
                text[: int(length / 2)] + fillIn,
                fillIn + text[int(length / 2) :],
            ]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [
                numberOfSlices,
                text[: int((length + 1) / 2)] + fillIn,
                fillIn + space + text[int((length + 1) / 2) :],
            ]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality :])
        else:
            result.append(text[i * cardinality : (i + 1) * cardinality])
    return result


def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return "\n".join(list)
