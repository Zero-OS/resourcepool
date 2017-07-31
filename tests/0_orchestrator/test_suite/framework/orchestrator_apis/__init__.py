from requests import HTTPError


def catch_exception_decoration(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 440:
                self.orchasterator_driver.refresh_jwt()
                wrapper(self, *args, **kwargs)
            else:
                return e.response

    return wrapper

def catch_exception_decoration_return(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 440:
                self.orchasterator_driver.refresh_jwt()
                wrapper(self, *args, **kwargs)
            else:
                return e.response, None

    return wrapper