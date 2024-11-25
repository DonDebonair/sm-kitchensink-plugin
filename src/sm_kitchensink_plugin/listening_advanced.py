from datetime import datetime, timedelta

from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import (
    process,
    listen_to,
    on,
    require_any_role,
    schedule
)
from machine.plugins.message import Message
from structlog.stdlib import get_logger

main_logger = get_logger(__name__)


class ListeningAdvanced(MachineBasePlugin):
    """Listening Advanced (events, scheduled messages, etc.)"""

    @listen_to(r"^do secret stuff")
    @require_any_role(["admin"])
    async def admin(self, msg: Message):
        await msg.say("You're an admin, so you are allowed to do secret things!", ephemeral=True)

    @on("my-plugin-event")
    async def plugin_event_handle(self, name: str = ""):
        channel = self.find_channel_by_name("#general")
        await self.say(channel, f"I've received my-plugin-event from {name}")

    @listen_to(r"^trigger my-plugin-event")
    async def trigger_plugin_event(self, msg: Message):
        main_logger.info("Triggering my-plugin-event")
        self.emit("my-plugin-event", name=msg.sender.name)

    @listen_to(r"^wait$")
    async def wait(self, msg: Message):
        """wait: the bot replies to you using a scheduled message"""
        await msg.reply("wait for it", in_thread=True)
        dt = datetime.now() + timedelta(seconds=10)
        await msg.reply_scheduled(dt, "hello after 10 seconds", in_thread=True)

    @listen_to(r"^dm reply scheduled$")
    async def dm_scheduled(self, msg: Message):
        """dm reply scheduled: the bot replies to you at a later moment, in a DM"""
        await msg.reply_dm("wait for it")
        dt = datetime.now() + timedelta(seconds=10)
        await msg.reply_dm_scheduled(
            dt, "sure I'll reply to you in a DM after 10 seconds"
        )

    @schedule(minute="*/10")
    async def scheduled_action(self):
        channel = self.find_channel_by_name("#general")
        await self.say(channel, "I'm doing this on a schedule (`*/10`)")

    @listen_to(r".*pin.*")
    async def pin_message(self, msg: Message):
        """... pin ...: pin the message"""
        await msg.say("I will pin this message for you!")
        pinned_item = await self.storage.get("pinned-item")
        if pinned_item is not None:
            await self.unpin_message(msg.channel, pinned_item)
        await msg.pin_message()
        await self.storage.set("pinned-item", msg.ts)

    @process("reaction_added")
    async def match_reaction(self, event):
        """If a user reacts to a message, the bot adds the same reaction"""
        main_logger.info(event)
        main_logger.info("bot info", bot_info=self.bot_info)
        if not event["user"] == self.bot_info["user_id"]:
            emoji = event["reaction"]
            channel = event["item"]["channel"]
            ts = event["item"]["ts"]
            await self.react(channel, ts, emoji)

    @listen_to(r"show bot info")
    async def info(self, msg: Message):
        """show bot info: show the bot info"""
        await msg.say(
            f"Bot info: {self.bot_info}, base url: {self.web_client.base_url}"
        )
