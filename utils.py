import subprocess

class BotSwitch:
    def intent(self, command):
        default = "Incorrect command"
        return getattr(self, command, lambda: default)()

    def temperature(self):
        _cmds = ['vcgencmd', 'measure_temp']
        return subprocess.check_output(_cmds).decode("utf-8") 

    def list_all_commands(self):
        return dir(self)

