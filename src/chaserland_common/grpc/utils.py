import grpc


def to_http_status(status_code: grpc.StatusCode):
    if status_code == grpc.StatusCode.OK:
        return 200
    elif status_code == grpc.StatusCode.CANCELLED:
        return 499
    elif status_code == grpc.StatusCode.UNKNOWN:
        return 500
    elif status_code == grpc.StatusCode.INVALID_ARGUMENT:
        return 400
    elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
        return 504
    elif status_code == grpc.StatusCode.NOT_FOUND:
        return 404
    elif status_code == grpc.StatusCode.ALREADY_EXISTS:
        return 409
    elif status_code == grpc.StatusCode.PERMISSION_DENIED:
        return 403
    elif status_code == grpc.StatusCode.UNAUTHENTICATED:
        return 401
    elif status_code == grpc.StatusCode.RESOURCE_EXHAUSTED:
        return 429
    elif status_code == grpc.StatusCode.FAILED_PRECONDITION:
        return 400
    elif status_code == grpc.StatusCode.ABORTED:
        return 409
    elif status_code == grpc.StatusCode.UNIMPLEMENTED:
        return 501
    elif status_code == grpc.StatusCode.INTERNAL:
        return 500
    elif status_code == grpc.StatusCode.UNAVAILABLE:
        return 503
    elif status_code == grpc.StatusCode.DATA_LOSS:
        return 500
    else:
        return 500
