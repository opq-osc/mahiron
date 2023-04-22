import datetime
import os
import random
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

# ==========================================

# 屏蔽群 例：[12345678, 87654321]
blockGroupNumber = []
# 触发命令列表
commandList = ["今日人品", "今日运势", "抽签", "人品", "运势", "小狐狸签", "吹雪签"]

# ==========================================


async def bot_vtuber_fortune(mahiro: GroupMessageMahiro):
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


class VtuberFortuneModel(Enum):
    LITTLE_FOX = "little_fox"

    DEFAULT = "default"


def handlingMessages(msg, bot: Sender, userGroup, userQQ, userNickname):
    match = Tools.commandMatch(msg, commandList)
    if match:
        # Determine if it has been used today
        if testUse(userQQ) == Status.SUCCESS:
            model = VtuberFortuneModel.DEFAULT
            # Detect whether it is a small fox lottery
            if msg.find("小狐狸") != -1 or msg.find("吹雪") != -1:
                model = VtuberFortuneModel.LITTLE_FOX
            # Plot
            outPath = drawing(model, userQQ)
            # Send a message
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
    imgPath = randomBasemap()
    if model == VtuberFortuneModel.LITTLE_FOX:
        imgPath = f"{RESOURCES_BASE_PATH}/img/frame_17.png"
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
    outPath = originalFilePath.replace("/img/", "/out/").replace("frame", str(userQQ))
    dirPath = f"{RESOURCES_BASE_PATH}/out"
    Tools.checkFolder(dirPath)
    return outPath


def randomBasemap():
    p = f"{RESOURCES_BASE_PATH}/img"
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
