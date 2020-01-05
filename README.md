# Slack Machine Example Plugin

This is an example plugin for Slack Machine showcasing some of its capabilities.

## Usage

Add the plugin to the requirements of your Slack bot:

_requirements.txt_

```requirements.txt
https://github.com/DandyDev/sm-example-plugin
```

Add the plugin to the `PLUGINS` section of your `local_settings.py`. The fully qualified module path + class is:
`example_plugin.my_plugins.MyPlugin`

```python
PLUGINS = ['machine.plugins.builtin.general.HelloPlugin',
           'machine.plugins.builtin.help.HelpPlugin',
           ...
           'example_plugin.my_plugins.MyPlugin']

SLACK_API_TOKEN = 'xoxb-123'
```
