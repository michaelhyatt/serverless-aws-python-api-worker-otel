import logging
import os
import requests
from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

URL = os.getenv('CONSUMER_API')


def producer(event, context):

    # Get trace context if exists. If not, create the request with fresh context
    context = get_trace_context(event=event)

    tracer = trace.get_tracer(__name__)

    # Create the top-level transaction representing the lqmbda work
    with tracer.start_as_current_span(name="producer-function-top-level", context=context, kind=SpanKind.SERVER):

        logger.debug(f'Context: {context}')

        logger.debug(f'Message: {event}')

        # Requests library is auto-instrumented, no need to create custom spans,
        # it will create it's own SpanKind.CLIENT "HTTP GET" span.
        request_to_downstream = requests.Request(method="GET", url=URL, 
        headers={
            "Content-Type": "application/json"
        })

        # Inject the right trace header into the request
        inject_context_into_request(request=request_to_downstream)

        session = requests.Session()

        res = session.send(request_to_downstream.prepare())

    return {'statusCode': res.status_code}


def consumer(event, context):

    # Get trace context sent from the other lambda
    context = get_trace_context(event=event)

    tracer = trace.get_tracer(__name__)

    # Create top level transaction representing the lambda work
    with tracer.start_as_current_span("consumer-function-top-level", context=context, kind=SpanKind.SERVER):

        logger.debug(f'Context: {context}')

        # Some other internal work performed by the lambda
        with tracer.start_as_current_span("consumer-function-some-internal-work", kind=SpanKind.INTERNAL):

            logger.debug(f'Message: {event}')

    return {'statusCode': 200}



# Utility functions
import typing

CarrierT = typing.TypeVar("CarrierT")

from opentelemetry.propagators.textmap import Getter, Setter

PROPAGATOR = propagate.get_global_textmap()

class get_header_from_event_request(Getter):
    def get(self, carrier: CarrierT, key: str) -> typing.Optional[typing.List[str]]:
        value = carrier['headers'].get(key)
        logger.debug(f'Getter requested {key}. Value returned {value}')
        return [value] if value is not None else []
        
    def keys(self, carrier: CarrierT) -> typing.List[str]:
        value = list(carrier['headers'].keys())
        logger.debug(f'Keys: {value}')
        return value

class set_header_into_requests_request(Setter):
    def set(self, request: requests.Request, key: str, value: str) -> None:
        logger.debug(f'Setter requested for {key} to value {value}')
        request.headers[key] = value


# Retrieves trace context from lambda event
def get_trace_context(event):
    return PROPAGATOR.extract(getter=get_header_from_event_request(), carrier=event)

# Injects trace context into requests HTTP header
def inject_context_into_request(request):
    PROPAGATOR.inject(carrier=request, setter=set_header_into_requests_request())
       