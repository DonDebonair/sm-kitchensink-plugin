from machine.plugins.base import MachineBasePlugin
from machine.plugins.command import Command
from machine.plugins.decorators import (
    command
)
from structlog.stdlib import get_logger, BoundLogger

main_logger = get_logger(__name__)


class SlashCommands(MachineBasePlugin):
    """Slash Commands"""

    @command("/hello")
    async def hello_command(self, command: Command, logger: BoundLogger):
        logger.info("command triggered", command=command.command, text=command.text)
        yield "Immediate response"
        await command.say(text=f"Well hello there! You sent me: {command.text}")
