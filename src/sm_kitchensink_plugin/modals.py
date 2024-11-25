import asyncio

from machine.plugins.base import MachineBasePlugin
from machine.plugins.command import Command
from machine.plugins.decorators import (
    command,
    modal,
    modal_closed
)
from machine.plugins.modals import ModalSubmission, ModalClosure
from slack_sdk.models import blocks
from slack_sdk.models.views import View
from structlog.stdlib import get_logger, BoundLogger

main_logger = get_logger(__name__)


class Modals(MachineBasePlugin):
    """Modals (and home tab)"""

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
