import json
import re
from typing import cast

from machine.plugins.base import MachineBasePlugin
from machine.plugins.block_action import BlockAction
from machine.plugins.decorators import (
    respond_to,
    listen_to,
    action
)
from machine.plugins.message import Message
from slack_sdk.models import blocks
from slack_sdk.models.blocks.basic_components import DispatchActionConfig
from structlog.stdlib import get_logger, BoundLogger

main_logger = get_logger(__name__)


class BlockKit(MachineBasePlugin):
    """Block Kit"""

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
            block_id="interaction_date_picker",
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
            block_id="interaction_checkboxes",
            hint="The fruits are healthy...",
        )

        email = blocks.EmailInputElement(
            action_id="provide_email"
        )
        email_input = blocks.InputBlock(
            label="Provide email address",
            element=email,
            block_id="interaction_email",
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
            block_id="interaction_startrek",
            hint="Next Generation...",
        )

        number = blocks.NumberInputElement(
            action_id="enter_number",
            is_decimal_allowed=False,
        )
        number_input = blocks.InputBlock(
            label="What is your favorite number?",
            element=number,
            block_id="interaction_number",
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
            block_id="interaction_overflow",
        )

        plain_text = blocks.PlainTextInputElement(
            action_id="provide_feelings",
            dispatch_action_config=DispatchActionConfig(trigger_actions_on=["on_character_entered"]),
        )
        plain_text_input = blocks.InputBlock(
            label="Your feelings",
            element=plain_text,
            block_id="interaction_feelings",
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
            block_id="interaction_radio_buttons",
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
            block_id="interaction_alphabet",
            hint="Choose wisely...",
        )

        time_picker = blocks.TimePickerElement(
            action_id="pick_time",
        )
        time_picker_input = blocks.InputBlock(
            label="Pick a time",
            element=time_picker,
            block_id="interaction_time_picker",
            hint="Choose your time wisely...",
        )

        url = blocks.UrlInputElement(
            action_id="provide_url",
            dispatch_action_config=DispatchActionConfig(trigger_actions_on=["on_character_entered"]),
        )
        url_input = blocks.InputBlock(
            label="Provide a URL",
            element=url,
            block_id="interaction_url",
            hint="URLs are cool...",
        )

        channel_select = blocks.ChannelMultiSelectElement(
            action_id="select_channel",
        )
        channel_select_input = blocks.InputBlock(
            label="Select channels",
            element=channel_select,
            block_id="interaction_channels_select",
            hint="Choose channels...",
        )

        conversation_select = blocks.ConversationSelectElement(
            action_id="select_conversation",
        )
        conversation_select_input = blocks.InputBlock(
            label="Select a conversation",
            element=conversation_select,
            block_id="interaction_conversation_select",
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

    @action(action_id=None, block_id=re.compile(r"interaction.*", re.IGNORECASE))
    async def interactions_logger(self, action: BlockAction, logger: BoundLogger):
        logger.info("Interaction triggered", triggered_action=action.triggered_action)
        msg = f"{action.user.fmt_mention()} has triggered:\n```{action.triggered_action.model_dump_json(indent=2)}```"
        await action.say(msg, ephemeral=False)


    @respond_to(r"^order lunch")
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
