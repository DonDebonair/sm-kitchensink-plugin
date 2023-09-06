import asyncio
from datetime import datetime, timedelta

from machine.plugins.base import MachineBasePlugin
from machine.plugins.command import Command
from machine.plugins.decorators import (
    process,
    respond_to,
    listen_to,
    on,
    require_any_role,
    schedule,
    command,
)
from machine.plugins.message import Message
from slack_sdk.models import blocks
from slack_sdk.models.views import View
from structlog.stdlib import get_logger, BoundLogger

main_logger = get_logger(__name__)


class MyPlugin(MachineBasePlugin):
    """Example Plugin"""

    async def init(self):
        update_fns = []
        for user in self.users.values():
            home_blocks = [
                blocks.HeaderBlock(
                    text=blocks.PlainTextObject.from_str(
                        f"Welcome {user.profile.display_name}"
                    )
                ),
                blocks.DividerBlock(),
                blocks.SectionBlock(
                    text=blocks.MarkdownTextObject.from_str(
                        "There is *so much* you can do here!"
                    )
                ),
            ]
            view = View(type="home", blocks=home_blocks)
            update_fns.append(self.web_client.views_publish(user_id=user.id, view=view))
        await asyncio.gather(*update_fns)

    @process("reaction_added")
    async def match_reaction(self, event):
        main_logger.info(event)
        main_logger.info("bot info", bot_info=self.bot_info)
        if not event["user"] == self.bot_info["user_id"]:
            emoji = event["reaction"]
            channel = event["item"]["channel"]
            ts = event["item"]["ts"]
            await self.react(channel, ts, emoji)

    @respond_to(r"^I love you", handle_message_changed=True)
    async def love(self, msg: Message, logger):
        logger.info("Love")
        """I love you: express your love to the bot, it might reciprocate"""
        await msg.react("heart")

    @listen_to(r"^users")
    async def list_users(self, msg: Message):
        """users: list all users in the Slack Workspace"""
        users = [u.name for u in self.users.values()]
        await msg.say(f"{len(users)} Users: {users}")

    @listen_to(r"^wait$")
    async def nag(self, msg: Message):
        """wait: the bot replies to you using a scheduled message"""
        await msg.reply("wait for it", in_thread=True)
        dt = datetime.now() + timedelta(seconds=30)
        await msg.reply_scheduled(dt, "hello after 30 seconds", in_thread=True)

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

    @listen_to(r"^dm reply scheduled$")
    async def dm_scheduled(self, msg: Message):
        """dm reply scheduled: the bot replies to you at a later moment, in a DM"""
        await msg.reply_dm("wait for it")
        dt = datetime.now() + timedelta(seconds=30)
        await msg.reply_dm_scheduled(
            dt, "sure I'll reply to you in a DM after 30 seconds"
        )

    @listen_to(r"^blocks$")
    async def blocks(self, msg: Message):
        """blocks: show some rich messaging magic"""
        bx = [
            blocks.SectionBlock(
                text="*Markdown formatted* text with _italics_ if we want",
                fields=["*Left*", "*Right*", "line 2 left", "line 2 right"],
                accessory=blocks.ImageElement(
                    image_url="http://placekitten.com/700/500", alt_text="cute kitten"
                ),
            )
        ]
        await msg.say("fallback", blocks=bx)

    @listen_to(r"^blocks raw$")
    async def blocks_raw(self, msg: Message):
        """blocks raw: show some rich messaging magic. Uses raw dict for specifying blocks"""
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

    @listen_to(r"^admin")
    @require_any_role(["admin"])
    async def admin(self, msg: Message):
        await msg.say("You're an admin!")

    @on("my-plugin-event")
    async def plugin_event_handle(self, name: str = ""):
        channel = self.find_channel_by_name("#general")
        await self.say(channel, f"I'm listening to my-plugin-event with {name}")

    @listen_to(r"^trigger my-plugin-event")
    async def trigger_plugin_event(self, msg: Message):
        main_logger.info("Triggering my-plugin-event")
        self.emit("my-plugin-event", name="Daan")

    @schedule(minute="*/10")
    async def scheduled_action(self):
        channel = self.find_channel_by_name("#general")
        await self.say(channel, f"I'm doing this on a schedule")

    @listen_to(r".*pin.*")
    async def pin_message(self, msg: Message):
        await msg.say("I will pin this message for you!")
        pinned_item = await self.storage.get("pinned-item")
        if pinned_item is not None:
            await self.unpin_message(msg.channel, pinned_item)
        await msg.pin_message()
        await self.storage.set("pinned-item", msg.ts)

    @listen_to(r"info")
    async def info(self, msg: Message):
        await msg.say(
            f"Bot info: {self.bot_info}, base url: {self.web_client.base_url}"
        )

    @command("/hello")
    async def command(self, command: Command, logger: BoundLogger):
        logger.info("command triggered", command=command.command, text=command.text)
        yield "Hullo"
        await command.say(text=f"Yoooo nice! You sent me: {command.text}")

    @listen_to(r"^password")
    async def password(self, msg: Message):
        fields = blocks.SectionBlock(
            text=f"Hey {msg.at_sender}, it looks like you might want to reset your password. Do you want me to do it?"
        )

        approve_button = blocks.ButtonElement(
            text="Yes, please.",
            action_id="password_reset_yes_for_user",
            value=f"{msg.sender.id}",
            style="primary",
        )
        deny_button = blocks.ButtonElement(
            text="No, thank you.",
            action_id="password_reset_no_for_user",
            value=f"{msg.sender.id}",
            style="danger",
        )

        buttons = [approve_button, deny_button]

        actions = blocks.ActionsBlock(
            block_id="password_reset_user_confirmation_block", elements=buttons
        )

        await msg.reply(
            # providing text is strongly advised for i.e. mobile notifications
            text=f"Hey {msg.at_sender}, it looks like you might want to reset your password. Do you want me to do it?",
            in_thread=True,
            blocks=[fields, actions],
        )
