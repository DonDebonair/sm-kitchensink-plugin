from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import (
    respond_to,
    listen_to
)
from machine.plugins.message import Message
from slack_sdk.models import blocks
from structlog.stdlib import get_logger, BoundLogger

main_logger = get_logger(__name__)


class ListeningBasics(MachineBasePlugin):
    """Listening Basics"""

    @listen_to(r"^greetings")
    async def greetings(self, msg: Message, logger: BoundLogger):
        """greetings: say hello to the bot"""
        logger.info("someone says hello")
        await msg.say("Hello!")

    @respond_to(r"^I love you", handle_message_changed=True)
    async def love(self, msg: Message, logger):
        logger.info("Love")
        """I love you: express your love to the bot, it might reciprocate"""
        await msg.react("heart")

    @listen_to(r"^list users")
    async def list_users(self, msg: Message):
        """users: list all users in the Slack Workspace"""
        users = [u.name for u in self.users.values()]
        await msg.say(f"{len(users)} Users: {', '.join(users)}")

    @listen_to(r"^reply$")
    async def reply_me(self, msg: Message):
        """reply: the bot replies to you"""
        resp = await msg.reply(
            "sure, I'll reply to you", icon_url="https://placekitten.com/200/200"
        )
        main_logger.info("TS: %s", resp["message"]["ts"])

    @listen_to(r"^reply ephemeral$")
    async def reply_me_ephemeral(self, msg: Message):
        """reply ephemeral: the bot replies to you and only you can see it"""
        await msg.reply(
            "sure, I'll reply to you in an ephemeral message", ephemeral=True
        )

    @listen_to(r"^reply in thread$")
    async def reply_me_in_thread(self, msg: Message):
        """reply in thread: the bot replies to you in a thread"""
        await msg.reply("sure, I'll reply to you in a thread", in_thread=True)

    @listen_to(r"^dm reply$")
    async def dm(self, msg: Message):
        """dm reply: the bot replies to you in a DM"""
        await msg.reply_dm("sure I'll reply to you in a DM")

    @listen_to(r"^show blocks$")
    async def blocks(self, msg: Message):
        """show blocks: show some rich messaging magic using Python block models"""
        bx = [
            blocks.SectionBlock(
                text="*Markdown formatted* text with _italics_ if we want",
                fields=["*Left*", "*Right*", "line 2 left", "line 2 right"],
                accessory=blocks.ImageElement(
                    image_url="https://placecats.com/700/500", alt_text="cute kitten"
                ),
            )
        ]
        await msg.say("fallback", blocks=bx)

    @listen_to(r"^show blocks raw$")
    async def blocks_raw(self, msg: Message):
        """show blocks raw: show some rich messaging magic. Uses raw dict for specifying blocks"""
        bx = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello, Assistant to the Regional Manager Dwight! *Michael Scott* wants to know where you'd like to take the Paper Company investors to dinner tonight.\n\n *Please select a restaurant:*",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Kin Khao*\n:star::star::star::star: 1638 reviews\n The sticky rice also goes wonderfully with the caramelized pork belly, which is absolutely melt-in-your-mouth and so soft.",
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/korel-1YjNtFtJlMTaC26A/o.jpg",
                    "alt_text": "alt text for image",
                },
                "fields": [
                    {"type": "mrkdwn", "text": "*Priority*"},
                    {"type": "mrkdwn", "text": "*Type*"},
                    {"type": "plain_text", "text": "High"},
                    {"type": "mrkdwn", "text": "String"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Farmhouse Thai Cuisine*\n:star::star::star::star: 1528 reviews\n They do have some vegan options, like the roti and curry, plus they have a ton of salad stuff and noodles can be ordered without meat!! They have something for everyone here",
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Ler Ros*\n:star::star::star::star: 2082 reviews\n I would really recommend the  Yum Koh Moo Yang - Spicy lime dressing and roasted quick marinated pork shoulder, basil leaves, chili & rice powder.",
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Farmhouse",
                            "emoji": True,
                        },
                        "value": "click_me_123",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Kin Khao",
                            "emoji": True,
                        },
                        "value": "click_me_123",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Ler Ros",
                            "emoji": True,
                        },
                        "value": "click_me_123",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You can add an image next to text in this block.",
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/plants.png",
                    "alt_text": "plants",
                },
            },
        ]
        await msg.say("fallback", blocks=bx)
