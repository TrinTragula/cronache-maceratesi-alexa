# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

from cronache_maceratesi import get_latest_news

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SENTENCES = {
    "launch": "Ciao, chiedimi di dirti le ultime notizie!",
    "no_news": "Non ho trovato nuove notizie.",
    "no_news_on_category": "Non ho trovato notizie relative a questo argomento.",
    "help": "Chiedimi le ultime notizie e ti leggerò gli ultimi articoli pubblicati da Cronache Maceratesi. Puoi anche chiedere le ultime notizie per la tua città. Prova a chiedere le ultime notizie su 'Camerino'",
    "stop": "A presto!",
    "exception": "Scusa, non ho capito, puoi ripetere?"
}


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = SENTENCES["launch"]

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class LatestNewsIntentHandler(AbstractRequestHandler):
    """Handler for LatestNews Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LatestNewsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        news = get_latest_news()
        speak_output = "Ecco le ultime notizie. " + " ".join(news)

        if news is None or news == []:
            return (
                handler_input.response_builder
                .speak(SENTENCES["no_news"])
                .response
            )

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class LatestNewsOnCategoryIntentHandler(AbstractRequestHandler):
    """Handler for LatestNewsOnCategoryIntent Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LatestNewsOnCategoryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        category = slots["Category"]
        if category.value:
            news = get_latest_news(category.value)
            speak_output = "Ecco le ultime notizie su " + \
                category.value + ". " + " ".join(news)
        else:
            news = []

        if news is None or news == []:
            return (
                handler_input.response_builder
                .speak(SENTENCES["no_news_on_category"])
                .response
            )

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = SENTENCES["help"]

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = SENTENCES["stop"]

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.
        # Empty for now

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Hai attivato l'intent " + intent_name + "."

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = SENTENCES["exception"]
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(LatestNewsIntentHandler())
sb.add_request_handler(LatestNewsOnCategoryIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# IntentReflectorHandler must be the last before the exception handler
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
