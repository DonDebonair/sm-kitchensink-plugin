import logging

from machine.plugins.decorators import process, route, respond_to, listen_to
from machine.plugins.base import MachineBasePlugin, Message
from datetime import datetime, timedelta

from slack.web.classes import blocks, elements

logger = logging.getLogger(__name__)


class MyPlugin(MachineBasePlugin):
    """Example Plugin"""

    @process("reaction_added")
    def match_reaction(self, event):
        if not event['user'] == self.bot_info['id']:
            emoji = event['reaction']
            channel = event['item']['channel']
            ts = event['item']['ts']
            self.react(channel, ts, emoji)

    @route("/hello")
    @route("/hello/<name>")
    def my_exposed_function(self, name="World"):
        channel = self.find_channel_by_name('#test')
        self.say(channel, '{} is talking to me'.format(name))
        return {"hello": name}

    @respond_to(r"^I love you")
    def love(self, msg):
        """I love you: express your love to the bot, it might reciprocate"""
        msg.react("heart")

    @listen_to(r"^users")
    def list_users(self, msg):
        """users: list all users in the Slack Workspace"""
        users = [u.name for u in self.users.values()]
        msg.say(f"{len(users)} Users: {users}")

    @listen_to(r"^wait$")
    def nag(self, msg):
        """wait: the bot replies to you using a scheduled message"""
        msg.reply("wait for it", in_thread=True)
        dt = datetime.now() + timedelta(seconds=5)
        msg.reply_scheduled(dt, 'hello', in_thread=True)

    @listen_to(r"^reply$")
    def reply_me(self, msg: Message):
        """reply: the bot replies to you"""
        msg.reply("sure, I'll reply to you", icon_url="https://placekitten.com/200/200")

    @listen_to(r"^reply ephemeral$")
    def reply_me_ephemeral(self, msg: Message):
        """reply ephemeral: the bot replies to you and only you can see it"""
        msg.reply("sure, I'll reply to you in an ephemeral message", ephemeral=True)

    @listen_to(r"^reply in thread$")
    def reply_me_in_thread(self, msg: Message):
        """reply in thread: the bot replies to you in a thread"""
        msg.reply("sure, I'll reply to you in a thread", in_thread=True)

    @listen_to(r"^dm reply$")
    def dm(self, msg: Message):
        """dm reply: the bot replies to you in a DM"""
        msg.reply_dm("sure I'll reply to you in a DM")

    @listen_to(r"^dm reply scheduled$")
    def dm_scheduled(self, msg: Message):
        """dm reply scheduled: the bot replies to you at a later moment, in a DM"""
        msg.reply_dm("wait for it")
        dt = datetime.now() + timedelta(seconds=5)
        msg.reply_dm_scheduled(dt, "sure I'll reply to you in a DM after 5 seconds")

    @listen_to(r"^blocks$")
    def blocks(self, msg: Message):
        """blocks: show some rich messaging magic"""
        bx = [
            blocks.SectionBlock(
                text="*Markdown formatted* text with _italics_ if we want",
                fields=["*Left*", "*Right*", "line 2 left", "line 2 right"],
                accessory=elements.ImageElement(image_url="http://placekitten.com/700/500",
                                                alt_text="cute kitten")
            )
        ]
        msg.say("fallback", blocks=bx)

    @listen_to(r"^blocks raw$")
    def blocks_raw(self, msg: Message):
        """blocks raw: show some rich messaging magic. Uses raw dict for specifying blocks"""
        bx = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello, Assistant to the Regional Manager Dwight! *Michael Scott* wants to know where you'd like to take the Paper Company investors to dinner tonight.\n\n *Please select a restaurant:*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Kin Khao*\n:star::star::star::star: 1638 reviews\n The sticky rice also goes wonderfully with the caramelized pork belly, which is absolutely melt-in-your-mouth and so soft."
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/korel-1YjNtFtJlMTaC26A/o.jpg",
                    "alt_text": "alt text for image"
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Priority*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Type*"
                    },
                    {
                        "type": "plain_text",
                        "text": "High"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "String"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Farmhouse Thai Cuisine*\n:star::star::star::star: 1528 reviews\n They do have some vegan options, like the roti and curry, plus they have a ton of salad stuff and noodles can be ordered without meat!! They have something for everyone here"
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg",
                    "alt_text": "alt text for image"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Ler Ros*\n:star::star::star::star: 2082 reviews\n I would really recommend the  Yum Koh Moo Yang - Spicy lime dressing and roasted quick marinated pork shoulder, basil leaves, chili & rice powder."
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "alt text for image"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Farmhouse",
                            "emoji": True
                        },
                        "value": "click_me_123"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Kin Khao",
                            "emoji": True
                        },
                        "value": "click_me_123"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Ler Ros",
                            "emoji": True
                        },
                        "value": "click_me_123"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You can add an image next to text in this block."
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/plants.png",
                    "alt_text": "plants"
                }
            }
        ]
        msg.say("fallback", blocks=bx)
