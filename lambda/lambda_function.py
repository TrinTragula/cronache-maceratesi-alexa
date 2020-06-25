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

NEWS_PAGE_KEY = "NEWS_PAGE_NUMBER"
CATEGORY_KEY = "NEWS_CATEGORY"

SENTENCES = {
    "launch": "Ciao, chiedimi di leggerti le ultime notizie!",
    "invite_to_ask_more": "Chiedimi di nuovo le ultime notizie o notizie su di un particolare argomento.",
    "no_news": "Non ho trovato nuove notizie.",
    "no_news_on_category": "Non ho trovato notizie relative a questo argomento.",
    "no_more_news": "Non ho trovato altre notizie.",
    "help": "Chiedimi le ultime notizie e ti leggerò gli ultimi articoli pubblicati su Cronache Maceratesi. Puoi anche chiedere le ultime notizie per la tua città. Prova a chiedere 'Alexa, dimmi le ultime notizie su Camerino'",
    "stop": "A presto!",
    "exception": "Scusa, non ho capito, puoi ripetere?",
    "more": "Vuoi che continui a leggere altre notizie?",
    "pause": "<break time='1s'/> "
}


def get_current_page_from_session(handler_input):
    return 0 if NEWS_PAGE_KEY not in handler_input.attributes_manager.session_attributes else handler_input.attributes_manager.session_attributes[
        NEWS_PAGE_KEY]


def get_category_from_session(handler_input):
    return None if CATEGORY_KEY not in handler_input.attributes_manager.session_attributes else handler_input.attributes_manager.session_attributes[
        CATEGORY_KEY]


def get_answer(news, category=None, is_more=False):
    if is_more:
        incipit = ""
    else:
        incipit = "Ecco le ultime notizie"
        if category is not None:
            incipit += " su {}".format(category)
        incipit += ". "

    news_string = SENTENCES["pause"].join(news)

    return "{}{}  <break time='1s'/> {}".format(incipit, news_string, SENTENCES["more"])


def reset_all(handler_input):
    handler_input.attributes_manager.session_attributes[NEWS_PAGE_KEY] = 0
    handler_input.attributes_manager.session_attributes[CATEGORY_KEY] = None


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        reset_all(handler_input)
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
        reset_all(handler_input)

        current_page = 0

        news = get_latest_news(current_page)
        speak_output = get_answer(news)

        if news is None or news == []:
            reset_all(handler_input)
            return (
                handler_input.response_builder
                .speak(SENTENCES["no_news"] + " " + SENTENCES["invite_to_ask_more"])
                .ask(SENTENCES["invite_to_ask_more"])
                .response
            )

        handler_input.attributes_manager.session_attributes[NEWS_PAGE_KEY] = current_page + 1
        handler_input.attributes_manager.session_attributes[CATEGORY_KEY] = None

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(SENTENCES["more"])
            .response
        )


class LatestNewsOnCategoryIntentHandler(AbstractRequestHandler):
    """Handler for LatestNewsOnCategoryIntent Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("LatestNewsOnCategoryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        reset_all(handler_input)

        current_page = 0

        slots = handler_input.request_envelope.request.intent.slots
        category = slots["Category"]
        if category.value:
            news = get_latest_news(current_page, category.value)
            speak_output = get_answer(news, category.value)
        else:
            news = []

        if news is None or news == []:
            reset_all(handler_input)
            return (
                handler_input.response_builder
                .speak(SENTENCES["no_news_on_category"] + " " + SENTENCES["invite_to_ask_more"])
                .ask(SENTENCES["invite_to_ask_more"])
                .response
            )

        handler_input.attributes_manager.session_attributes[NEWS_PAGE_KEY] = current_page + 1
        handler_input.attributes_manager.session_attributes[CATEGORY_KEY] = category.value

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(SENTENCES["more"])
            .response
        )


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        current_page = get_current_page_from_session(handler_input)
        category = get_category_from_session(handler_input)

        news = get_latest_news(current_page, category)
        speak_output = get_answer(news, category, True)

        handler_input.attributes_manager.session_attributes[NEWS_PAGE_KEY] = current_page + 1
        handler_input.attributes_manager.session_attributes[CATEGORY_KEY] = category

        if news is None or news == []:
            reset_all(handler_input)
            return (
                handler_input.response_builder
                .speak(SENTENCES["no_more_news"] + " " + SENTENCES["invite_to_ask_more"])
                .ask(SENTENCES["invite_to_ask_more"])
                .response
            )

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(SENTENCES["more"])
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
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        reset_all(handler_input)

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
        reset_all(handler_input)

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
sb.add_request_handler(YesIntentHandler())

# IntentReflectorHandler must be the last before the exception handler
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
