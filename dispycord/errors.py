__all__ = (
	"error",
)


class BaseError(Exception):
	
	...
	
	
class LoginFailure(BaseError):
	
	...
	
	
class UncaughtError(BaseError):
	
	...
	
	
error: dict = {
	"4004": LoginFailure,
	"default": UncaughtError
}