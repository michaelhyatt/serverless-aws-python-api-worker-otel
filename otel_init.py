from os import environ

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


resource = Resource.create({
    SERVICE_NAME: environ.get("OTEL_SERVICE_NAME")
})

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

trace.set_tracer_provider(TracerProvider(resource=resource))

span_processor = SimpleSpanProcessor(otlp_exporter)

trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer("otel-lambda")
