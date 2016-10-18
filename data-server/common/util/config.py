def check_config(config, name, *args):
    for arg in args:
        if arg not in config:
            raise Exception("%s should be contain parameter: %s" % (name, arg))
