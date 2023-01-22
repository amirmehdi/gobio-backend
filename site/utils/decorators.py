import json
from functools import wraps

from utils import decimal_encoder


def cors_headers(handler_or_origin=None, origin=None, credentials=False):
    """
    Automatically injects ``Access-Control-Allow-Origin`` headers to http
    responses. Also optionally adds ``Access-Control-Allow-Credentials: True`` if
    called with ``credentials=True``
    """
    if isinstance(handler_or_origin, str) and origin is not None:
        raise TypeError(
            "You cannot include any positonal arguments when using"
            " the `origin` keyword argument"
        )
    if isinstance(handler_or_origin, str) or origin is not None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                response = handler(event, context)
                if response is None:
                    response = {}
                headers = response.setdefault("headers", {})
                if origin is not None:
                    headers["Access-Control-Allow-Origin"] = origin
                else:
                    headers["Access-Control-Allow-Origin"] = handler_or_origin
                if credentials:
                    headers["Access-Control-Allow-Credentials"] = True
                return response

            return wrapper

        return wrapper_wrapper
    elif handler_or_origin is None:
        return cors_headers("*", credentials=credentials)
    else:
        return cors_headers("*")(handler_or_origin)


def json_http_resp(handler_or_none=None, **json_dumps_kwargs):
    """
    Automatically serialize return value to the body of a successful HTTP
    response.

    Returns a 500 error if the response cannot be serialized
    """

    if handler_or_none is not None and len(json_dumps_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                try:
                    resp = handler(event, context)
                    if isinstance(resp, dict) :
                        status = resp.pop('statusCode', 200)
                        headers = resp.pop('headers', {})
                        headers['Content-Type'] = 'application/json'
                        body = resp.pop('body', {})
                    elif isinstance(resp, list):
                        status = 200
                        headers = {'Content-Type': 'application/json'}
                        body = resp
                    elif isinstance(resp, str):
                        status = 200
                        headers = {'Content-Type': 'application/json'}
                        body = {'message': resp}
                    else:
                        # raise Exception("response type is not supported")
                        status = 200
                        body = resp
                        headers = None

                    http_resp = {
                        "statusCode": status,
                        "body": json.dumps(
                            body,
                            cls=decimal_encoder.DecimalEncoder,
                            **json_dumps_kwargs,
                        ),
                    }
                    if headers:
                        http_resp["headers"] = headers
                    return http_resp
                except Exception as exception:
                    if hasattr(context, "serverless_sdk"):
                        context.serverless_sdk.capture_exception(exception)
                    return {"statusCode": 500, "body": str(exception)}

            return wrapper

        return wrapper_wrapper
    else:
        return json_http_resp()(handler_or_none)


def load_json_body(handler_or_none=None, **json_loads_kwargs):
    """
    Automatically deserialize event bodies with json.loads.

    Automatically returns a 400 BAD REQUEST if there is an error while parsing.

    note that ``event['body']`` is already a dictionary and didn't have to
    explicitly be parsed.
    """
    if handler_or_none is not None and len(json_loads_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                if isinstance(event.get("body"), str):
                    try:
                        event["body"] = json.loads(event["body"], **json_loads_kwargs)
                    except Exception as exception:
                        if hasattr(context, "serverless_sdk"):
                            context.serverless_sdk.capture_exception(exception)
                        return {"statusCode": 400, "body": "BAD REQUEST"}
                return handler(event, context)

            return wrapper

        return wrapper_wrapper
    else:
        return load_json_body()(handler_or_none)
