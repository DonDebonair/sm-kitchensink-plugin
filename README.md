# Slack Machine Kitchensink Plugin

This is a plugin for Slack Machine showcasing many of its capabilities.

## Usage

Add the plugin to the dependencies of your Slack bot:

Using uv:

```bash
uv add git+https://github.com/DonDebonair/sm-kitchensink-plugin
```

Using Poetry:

```bash
poetry add git+https://github.com/DonDebonair/sm-kitchensink-plugin
```

When using `pip`, put the following in your _requirements.txt_:

```requirements.txt
https://github.com/DandyDev/sm-kitchensink-plugin
```

Add the separate plugin classes to the `PLUGINS` section of your `local_settings.py`.

```python
PLUGINS = [
    'machine.plugins.builtin.general.HelloPlugin',
    'machine.plugins.builtin.help.HelpPlugin',
    ...
    'sm_kitchensink_plugin.ListeningBasics',
    'sm_kitchensink_plugin.ListeningAdvanced',
    'sm_kitchensink_plugin.SlashCommands',
    'sm_kitchensink_plugin.BlockKit',
    'sm_kitchensink_plugin.Modals',
]

SLACK_APP_TOKEN = 'xapp-123'
SLACK_BOT_TOKEN = 'xoxb-456'
```
