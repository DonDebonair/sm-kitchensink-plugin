import asyncio
import re
from datetime import datetime, timedelta

from machine.plugins.base import MachineBasePlugin
from machine.plugins.command import Command
from machine.plugins.block_action import BlockAction
from machine.plugins.modals import ModalSubmission, ModalClosure
from machine.plugins.decorators import (
    process,
    respond_to,
    listen_to,
    on,
    require_any_role,
    schedule,
    command,
    action,
    modal,
    modal_closed
)
from machine.plugins.message import Message
from slack_sdk.models import blocks
from slack_sdk.models.blocks.basic_components import DispatchActionConfig
from slack_sdk.models.views import View
from structlog.stdlib import get_logger, BoundLogger
from typing import cast

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
            update_fns.append(self.publish_home_tab(user=user, view=view))
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
        await self.say(channel, "I'm doing this on a schedule")

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
    async def hello_command(self, command: Command, logger: BoundLogger):
        logger.info("command triggered", command=command.command, text=command.text)
        yield "Hullo"
        await command.say(text=f"Yoooo nice! You sent me: {command.text}")

    @listen_to(r"^interactions")
    async def interactions(self, msg: Message):
        header = blocks.HeaderBlock(text="Interactivity 🎉")
        message = blocks.SectionBlock(
            text=f"Hey {msg.at_sender}, you wanna see some interactive goodness? I can show you!"
        )

        divider1 = blocks.DividerBlock()

        date_picker = blocks.DatePickerElement(action_id="pick_date")
        date_picker_input = blocks.InputBlock(
            label="Pick a date",
            element=date_picker,
            block_id="date_picker",
            hint="Choose your date wisely...",
        )

        checkboxes = blocks.CheckboxesElement(
            action_id="select_options",
            options=[
                blocks.Option(
                    value="apple",
                    label="apple",
                    text=blocks.MarkdownTextObject(text="*juicy apple*"),
                ),
                blocks.Option(value="orange", label="orange", text="fresh orange"),
                blocks.Option(value="cherry", label="cherry", text="red cherry"),
            ],
        )
        checkboxes_input = blocks.InputBlock(
            label="Select some fruits",
            element=checkboxes,
            block_id="checkboxes",
            hint="The fruits are healthy...",
        )

        email = blocks.EmailInputElement(
            action_id="provide_email"
        )
        email_input = blocks.InputBlock(
            label="Provide email address",
            element=email,
            block_id="email",
            hint="Email is personal...",
        )

        multi_select_menu = blocks.StaticMultiSelectElement(
            action_id="multi_select_menu_options",
            options=[
                blocks.Option(value="data", label="data", text="Data"),
                blocks.Option(value="picard", label="picard", text="Picard"),
                blocks.Option(value="worf", label="worf", text="Worf"),
            ],
        )
        multi_select_menu_input = blocks.InputBlock(
            label="Select favorite Star Trek characters",
            element=multi_select_menu,
            block_id="startrek",
            hint="Next Generation...",
        )

        number = blocks.NumberInputElement(
            action_id="enter_number",
            is_decimal_allowed=False,
        )
        number_input = blocks.InputBlock(
            label="What is your favorite number?",
            element=number,
            block_id="number",
            hint="42",
        )

        overflow = blocks.OverflowMenuElement(
            action_id="pick_overflow_option",
            options=[
                blocks.Option(value="one", label="one", text="One"),
                blocks.Option(value="two", label="two", text="Two"),
                blocks.Option(value="three", label="three", text="Three"),
            ]
        )
        overflow_section = blocks.SectionBlock(
            text="Pick a number",
            accessory=overflow,
        )

        plain_text = blocks.PlainTextInputElement(
            action_id="provide_feelings",
            dispatch_action_config=DispatchActionConfig(trigger_actions_on=["on_character_entered"]),
        )
        plain_text_input = blocks.InputBlock(
            label="Your feelings",
            element=plain_text,
            block_id="feelings",
            hint="Be honest...",
        )

        radio_buttons = blocks.RadioButtonsElement(
            action_id="select_radio_option",
            options=[
                blocks.Option(value="1", text="Strongly agree"),
                blocks.Option(value="2", text="Agree"),
                blocks.Option(value="3", text="Neither agree nor disagree"),
                blocks.Option(value="4", text="Disagree"),
                blocks.Option(value="5", text="Strongly disagree"),
            ],
        )
        radio_buttons_input = blocks.InputBlock(
            label="You enjoy this selection of input elements",
            element=radio_buttons,
            block_id="radio_demonstration",
        )

        select_menu = blocks.StaticSelectElement(
            action_id="select_menu_options",
            options=[
                blocks.Option(value="A", label="A", text="AAAA"),
                blocks.Option(value="B", label="B", text="BBBB"),
                blocks.Option(value="C", label="C", text="CCCC"),
            ],
        )
        select_menu_input = blocks.InputBlock(
            label="What is your favorite character in the alphabet?",
            element=select_menu,
            block_id="alphabet",
            hint="Choose wisely...",
        )

        time_picker = blocks.TimePickerElement(
            action_id="pick_time",
        )
        time_picker_input = blocks.InputBlock(
            label="Pick a time",
            element=time_picker,
            block_id="time_picker",
            hint="Choose your time wisely...",
        )

        url = blocks.UrlInputElement(
            action_id="provide_url",
            dispatch_action_config=DispatchActionConfig(trigger_actions_on=["on_character_entered"]),
        )
        url_input = blocks.InputBlock(
            label="Provide a URL",
            element=url,
            block_id="url",
            hint="URLs are cool...",
        )

        channel_select = blocks.ChannelMultiSelectElement(
            action_id="select_channel",
        )
        channel_select_input = blocks.InputBlock(
            label="Select channels",
            element=channel_select,
            block_id="channels_select",
            hint="Choose channels...",
        )

        conversation_select = blocks.ConversationSelectElement(
            action_id="select_conversation",
        )
        conversation_select_input = blocks.InputBlock(
            label="Select a conversation",
            element=conversation_select,
            block_id="conversation_select",
            hint="Choose a conversation...",
        )

        divider2 = blocks.DividerBlock()

        approve_button = blocks.ButtonElement(
            text="Yes, please.",
            action_id="interactions_approve",
            value=f"{msg.sender.id}",
            style="primary",
        )
        deny_button = blocks.ButtonElement(
            text="No, thank you.",
            action_id="interactions_deny",
            value=f"{msg.sender.id}",
            style="danger",
        )

        buttons = [approve_button, deny_button]

        actions = blocks.ActionsBlock(
            block_id="interactions_confirmation", elements=buttons
        )

        await msg.reply(
            # providing text is strongly advised for i.e. mobile notifications
            text=f"Hey {msg.at_sender}, you wanna see some interactive goodness? I can show you!",
            blocks=[
                header,
                message,
                divider1,
                date_picker_input,
                checkboxes_input,
                email_input,
                multi_select_menu_input,
                number_input,
                overflow_section,
                plain_text_input,
                radio_buttons_input,
                select_menu_input,
                time_picker_input,
                url_input,
                channel_select_input,
                conversation_select_input,
                divider2,
                actions,
            ],
        )

    @command("/modal")
    async def modal_command(self, command: Command, logger: BoundLogger):
        raw_modal = {
            "type": "modal",
            "callback_id": "my_modal",
            "notify_on_close": True,
            "title": {
                "type": "plain_text",
                "text": "My App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": ":rocket: Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": ":cry: Cancel",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "What do you want?",
                        "emoji": True
                    }
                },
                {
                    "block_id": "modal_input",
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "opinion"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Give your opinion",
                        "emoji": True
                    }
                }
            ]
        }
        resp = await command.open_modal(view=raw_modal)
        logger.info("Modal opened", response=resp.data)

    @modal("my_modal")
    async def handle_modal(self, submission: ModalSubmission, logger: BoundLogger):
        updated_modal = {
            "type": "modal",
            "callback_id": "my_modal",
            "notify_on_close": True,
            "title": {
                "type": "plain_text",
                "text": "My App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": ":rocket: Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": ":cry: Cancel",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "What do you want?",
                        "emoji": True
                    }
                },
                {
                    "block_id": "modal_input",
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "opinion"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Give your opinion",
                        "emoji": True
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "_Thank you for your submission_"
                        }
                    ]
                }
            ]
        }
        yield {
            "response_action": "update",
            "view": updated_modal
        }
        logger.info("Modal submission", payload=submission.payload)
        value = submission.payload.view.state.values["modal_input"]["opinion"].value
        await self.say(self.find_channel_by_name("#general"), f"Modal submitted! Your grand opinion: {value}")

    @modal_closed("my_modal")
    async def handle_modal_closed(self, closure: ModalClosure, logger: BoundLogger):
        logger.info("Modal closed", payload=closure.payload)
        await self.say(self.find_channel_by_name("#general"), "Sadly the modal was closed")
        await closure.send_dm("You closed the modal. Are you sure you don't to submit your opinion?")

    @respond_to(r"^lunch")
    async def order_lunch(self, msg: Message):
        blcks = [
            blocks.SectionBlock(
                text=blocks.MarkdownTextObject(
                    text='*Where should we order lunch from?* Poll by <fakeLink.toUser.com|Mark>'),
                fields=[]
            ),
            blocks.DividerBlock(),
            blocks.SectionBlock(
                block_id="lunch_sushi",
                text=blocks.MarkdownTextObject(
                    text=':sushi: *Ace Wasabi Rock-n-Roll Sushi Bar*\nThe best landlocked sushi restaurant.'
                ),
                fields=[],
                accessory=blocks.ButtonElement(
                    action_id="sushi",
                    text=blocks.PlainTextObject(text='Vote', emoji=True),
                )
            ),
            blocks.ContextBlock(
                elements=[
                    blocks.ImageElement(image_url='https://api.slack.com/img/blocks/bkb_template_images/profile_1.png',
                                        alt_text='Michael Scott'),
                    blocks.ImageElement(image_url='https://api.slack.com/img/blocks/bkb_template_images/profile_2.png',
                                        alt_text='Dwight Schrute'),
                    blocks.ImageElement(image_url='https://api.slack.com/img/blocks/bkb_template_images/profile_3.png',
                                        alt_text='Pam Beasely'),
                    blocks.PlainTextObject(text='3 votes', emoji=True)
                ]
            ),
            blocks.SectionBlock(
                block_id="lunch_hamburger",
                text=blocks.MarkdownTextObject(
                    text=':hamburger: *Super Hungryman Hamburgers*\nOnly for the hungriest of the hungry.'
                ),
                fields=[],
                accessory=blocks.ButtonElement(
                    action_id="hamburger",
                    text=blocks.PlainTextObject(text='Vote', emoji=True),
                )
            ),
            blocks.ContextBlock(
                elements=[
                    blocks.ImageElement(image_url='https://api.slack.com/img/blocks/bkb_template_images/profile_4.png',
                                        alt_text='Angela'),
                    blocks.ImageElement(image_url='https://api.slack.com/img/blocks/bkb_template_images/profile_2.png',
                                        alt_text='Dwight Schrute'),
                    blocks.PlainTextObject(text='2 votes', emoji=True)
                ]
            ),
            blocks.SectionBlock(
                block_id="lunch_ramen",
                text=blocks.MarkdownTextObject(
                    text=':ramen: *Kagawa-Ya Udon Noodle Shop*\nDo you like to shop for noodles? We have noodles.'
                ),
                fields=[],
                accessory=blocks.ButtonElement(
                    action_id="ramen",
                    text=blocks.PlainTextObject(text='Vote', emoji=True),
                )
            ),
            blocks.ContextBlock(
                elements=[
                    blocks.MarkdownTextObject(text='No votes')]
            ),
            blocks.DividerBlock(),
            blocks.ActionsBlock(
                elements=[
                    blocks.ButtonElement(text=blocks.PlainTextObject(text='Add a suggestion', emoji=True),
                                         value='click_me_123')
                ]
            )
        ]
        await msg.say("Vote for lunch", blocks=blcks)

    @action(action_id=None, block_id=re.compile(r"lunch.*", re.IGNORECASE))
    async def lunch_action(self, action: BlockAction, logger: BoundLogger):
        logger.info("Action triggered", triggered_action=action.triggered_action)
        food_block = \
            [block for block in action.payload.message.blocks if block.block_id == action.triggered_action.block_id][0]
        food_block_section = cast(blocks.SectionBlock, food_block)
        food_description = str(food_block_section.text.text)
        msg = f"{action.user.fmt_mention()} has voted for '{food_description}'"
        await action.say(msg, ephemeral=False)
