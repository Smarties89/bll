#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from sys import argv

from plex import *

from lexicon import lexicon

log = logging.getLogger(__name__)
logging.basicConfig()


class EventHandler:
    def __init__(self, name, args, action_type, action):
        self.name = name
        self.args = args
        self.action_type = action_type
        self.action = action

    def __str__(self):
        return u"on {} {} {} {}".format(
            self.name,
            ' '.join(self.args),
            self.action_type,
            ' '.join(self.action),
        )


class BllInterpreter(Scanner):
    def __init__(self, *args, **kwargs):
        Scanner.__init__(self, *args, **kwargs)
        self.event_handlers = []


    def fail(self, msg):
        log.error("Failed: {}".format(msg))
        exit(1)

    def expect_read(self, expected):
        found = self.read()
        if found[0] != expected:
            self.fail("Expected {} found {}".format(expected, found))

        return found[1]

    def run(self):
        # Dummy to force run first while loop
        token = (1, )
        while token[0] is not None:
            token = self.read()
            if token[0] == 'on':
                self.parse_event_handler()
            elif token[0] == 'put':
                self.handle_put()
            elif token[0] == 'newline':
                continue
            # End of file
            elif token[0] == None:
                break
            else:
                self.fail("Unexpected token {}".format(token))

    def __read_args(self):
        args = []
        while True:
            token = self.read()
            if token[0] == 'ident':
                args.append(token[1])
            elif token[0] == 'output':
                return args, 'output'
            elif token[0] == 'do':
                return args, 'do'
            elif token[0] == None:
                self.fail(
                    "Reading function args expected "
                    "'output', 'ident', or 'do' but received end of file")
            else:
                self.fail(
                    "Reading function args expected "
                    "'output', 'ident', or 'do' but received {}".format(
                        token))

    def __read_parameters(self):
        parameters = []
        while True:
            token = self.read()
            if token[0] == 'string':
                # Using eval to avoid "double" string
                parameters.append(eval(token[1]))
            elif token[0] == None:
                break
            elif token[0] == 'newline':
                break

        return parameters


    def __read_until_newline_or_end(self):
        read = []
        while True:
            token = self.read()
            #if token[0] == 'string':
            #    token = (token[0], eval(token[1]))
            if token[0] is None or token[0] == 'newline':
                break
            read.append(token[1])

        return read

    def handle_event(self, eh, parameters):
        if eh.action_type == 'output':
            action = eval(eh.action[0])
            for i, arg in enumerate(eh.args):
                log.debug("Replacing '${}' -> '{}'".format(arg, parameters[i]))
                action = action.replace('$' + arg, parameters[i])
            log.debug("Executing '{}'".format(action))
            exec(action)

    def parse_event_handler(self):
        name = self.expect_read('ident')
        args, action_type = self.__read_args()
        action = self.__read_until_newline_or_end()
        self.event_handlers.append(EventHandler(
            name, args, action_type, action))

    def handle_put(self):
        name = self.expect_read('ident')
        parameters = self.__read_parameters()

        event_handlers = [eh for eh in self.event_handlers if eh.name == name]
        log.debug("Handling with following event handlers {}".format(event_handlers))
        for eh in event_handlers:
            self.handle_event(eh, parameters)


if __name__ == "__main__":
    if argv[1] == '-v':
        log.setLevel(logging.DEBUG)
        filename = argv[2]
    else:
        log.setLevel(logging.ERROR)
        filename = argv[1]

    with open(filename, 'r') as f:
        scanner = BllInterpreter(lexicon, f)
        scanner.run()
